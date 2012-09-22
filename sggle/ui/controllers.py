'''
Created on Nov 8, 2011

@author: vitali
'''


from PySide.QtCore import QObject
from PySide.QtCore import Signal
from PySide.QtCore import QPointF

 
import sggle.scene.commands as commands
import sggle.scene as scene
import sggle.saveload.readwrite as saveload

from   sggle.saveload.error import ParseError
import dialogs




class ItemsClipboard(QObject): 
    
    clipboardDataAvailableChanged = Signal(bool) 
    
    def __init__(self):
        QObject.__init__(self)
        
        self._data = []
        
        
    def clear(self):    
        self._data = []
        self.clipboardDataAvailableChanged.emit(False)


    def data(self):
        return self._data
    
    
    def append(self, data):
        self._data.append(data)
        if len(self._data):
            self.clipboardDataAvailableChanged.emit(True)

        
    def  hasData(self):
        return len(self._data) > 0


    def hasLayer(self):
        return self.hasData() and type(self._data[0]).__name__ == "Layer"




class BaseController(QObject):
    
    def __init__(self, sceneGroup):
        QObject.__init__(self)
    
        self.sceneGroup = sceneGroup
        
        
    def _scene(self):
        return self.sceneGroup.activeScene()
        
           
    def _pushCommand(self, cmd):
        self.sceneGroup.undoGroup().activeStack().push(cmd)  
        


    
class FileController(BaseController):  
    
    cleanStateChanged     = Signal(bool)
    sceneAvailableChanged = Signal(bool)
    
    sceneAdded                = Signal(str) # @param str: name 
    sceneRemoved              = Signal(int) # @param int: index
    activeSceneNameChanged    = Signal(str) # @param int: index, @param str: name 

    
    def __init__(self, sceneGroup, mainWindow):
        super(FileController, self).__init__(sceneGroup)
        
        self._sceneFileInfo       = {} # sceneObject : (filePath, fileType)
        self._sceneList           = []
        self._mainWindow          = mainWindow
        
        sceneGroup.activeItemPoprertyChanged.connect(self._forwardActiveSceneNameChanges)
        sceneGroup.undoGroup().cleanChanged.connect(self.cleanStateChanged.emit)
        sceneGroup.activeSceneChanged.connect(lambda s: self.sceneAvailableChanged.emit(s != None))

        
    def _forwardActiveSceneNameChanges(self, item, key):
        if key == "name" and item is self.sceneGroup.activeScene().rootItem():                
            self.activeSceneNameChanged.emit(item.value("name"))
        
        
    def _addScene(self, scene, filePath, fileType):
        self._sceneFileInfo[scene] = (filePath, fileType)
        self.sceneGroup.addScene(scene)
        self._sceneList.append(scene)
        
        self.sceneAdded.emit(scene.rootItem().value("name"))


    def _removeScene(self, scene):
        self._sceneFileInfo.pop(scene)
        self.sceneGroup.removeScene(scene)
        
        index = self._sceneList.index(scene)
        self._sceneList.pop(index)
        
        self.sceneRemoved.emit(index)

        
   
    def _writeScene(self, scene, filePath, fileType):
        
        try:
            fileStream = open(filePath, "w") 
        except IOError as e:
            dialogs.showErrorDialog("IO Error", "Unable to open file for writing.", e)
            return
        
        saveload.writeScene(scene, fileStream, fileType)
        fileStream.close()

        self._sceneFileInfo[scene] = (filePath, fileType)
        scene.undoStack().setClean()
        
    
    def newScene(self):        
        newScene = scene.newEmptyGraphicsScene()
        self._addScene(newScene, "","")

    
    def openScene(self): 
        fileTypes = saveload.formats.knowFileFormats()
        fileName, fileType = dialogs.showOpenSceneDialog(fileTypes)
 
        if  not fileName:
            return 
 
        try:
            fileStream = open(fileName, "r") 
        except IOError as e: 
            dialogs.showErrorDialog("IO Error", " Unable to open file for reading.", e)
            return

        try:
            newScene = saveload.readScene(fileStream, fileType)
        except ParseError as e: 
            dialogs.showErrorDialog("Parsing Error", "Unable to load Scene.", e)
        else:
            self._addScene(newScene, fileName, fileType)
        finally:
            fileStream.close()        
        
        
    def saveScene(self, scene):
        filePath, fileType = self._sceneFileInfo.get(scene, ("",""))
        if not filePath:
            self.saveSceneAs(scene)
        else:
            self._writeScene(scene, filePath, fileType)
        
        
    def saveActiveScene(self):
        if self._scene():
            self.saveScene(self.sceneGroup.activeScene())
    
    
    def saveActiveSceneAs(self):
        if self._scene():
            self.saveSceneAs(self.sceneGroup.activeScene())
        
        
    def saveSceneAs(self, scene):
        fileTypes = saveload.formats.knowFileFormats()
        fileName, fileType  = dialogs.showSaveSceneAsDialog(fileTypes)
        
        if fileName:
            self._writeScene(scene, fileName, fileType)
    
    
    def closeActiveScene(self):
        if self._scene():
            self.closeScene(self.sceneGroup.index(self.sceneGroup.activeScene()))
    
 
    def closeScene(self, sceneIndex):
        scene = self._sceneList[sceneIndex]
        name  = scene.rootItem().value("name")
        
        if not scene.undoStack().isClean():
            result = dialogs.showCloseSceneDialog(name)
            if result == dialogs.Response.Save:
                self.saveScene(scene)
                self.closeScene(sceneIndex)  
                return
                  
            if result == dialogs.Response.Discard:
                self._removeScene(scene) 
                
        else:
            self._removeScene(scene) 
       
            
    def openResourceFolder(self):
          
        path =  dialogs.showOpenResourceFolderDialog()
        if path:
            self._mainWindow.addDockedReourceViewer(path) 

    
    def setActiveScene(self, sceneIndex):
        self.sceneGroup.setActiveScene(None if sceneIndex == -1 else self._sceneList[sceneIndex])
        
        
    def swapSceneIndexOrder(self, fromIndex, toIndex):
        sceneList = self._sceneList
        tmp       = sceneList[toIndex]
        sceneList[toIndex]   = sceneList[fromIndex]
        sceneList[fromIndex] = tmp
    
    
    def unsavedScenes(self):
        dirtyScenes = []
        for s in  self.sceneGroup.sceneList():
            if not s.undoStack().isClean():
                dirtyScenes.append(s)
        return dirtyScenes
    
    
    def confirmExit(self):
        dirtyCount = len(self.unsavedScenes())
        
        if dirtyCount == 0:
            return True
        else:
            return dialogs.showExitDialog(dirtyCount) == dialogs.Response.Discard




class ItemsController(BaseController):
    
       
    canMoveSelectionUpChanged      = Signal(bool)
    canMoveSelectionDownChanged    = Signal(bool)
    canDeleteItemSelectionChanged  = Signal(bool) 
    canSelectAllChanged            = Signal(bool)   
    
    canMoveSelectionToLayerAboveChanged = Signal(bool) 
    canMoveSelectionToLayerBelowChanged = Signal(bool) 
    canMoveSelectionToNewLayerChanged   = Signal(bool) 
    
    canMoveLayerUpChanged        = Signal(bool)
    canMoveLayerDownChanged      = Signal(bool)
    canDeleteActiveLayerChanged  = Signal(bool) 
    canAddNewLayerChanged        = Signal(bool)
    canDuplicateLayerChanged     = Signal(bool)

    canCopyChanged               = Signal(bool) 
    canPasteChanged              = Signal(bool)
    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self, sceneGroup)
        
        self._clipboard  = ItemsClipboard()
        
        self.sceneGroup.listOfItemsChanged.connect(self._updateAllSignalTriggers)
        self.sceneGroup.selectionChanged.connect(self._updateAllSignalTriggers)
        self.sceneGroup.activeLayerChanged.connect(self._updateAllSignalTriggers)
        self.sceneGroup.activeSceneChanged.connect(self._updateAllSignalTriggers)
        self.sceneGroup.editModeChanged.connect(self._updateAllSignalTriggers)
        self.sceneGroup.listOfLayersChanged.connect(self._updateAllSignalTriggers)
        self._clipboard.clipboardDataAvailableChanged.connect(self._updateAllSignalTriggers)


    def _updateAllSignalTriggers(self):
        scene  = self._scene()
        
        self._updateSelectionTriggers(scene)
        self._updateLayerSignals(scene)
        self._updateCopyPasteTriggers(scene, self._clipboard)
        
        
    def _updateSelectionTriggers(self, scene):
        if scene:
            selection   = scene.selectedItems()
            items       = scene.activeLayer().childItems() if scene.activeLayer() else []  
            editMode    = scene.editMode()
            activeLayer = scene.activeLayer()
        else:
            selection = []

        if len(selection) and not editMode:
            self.canMoveSelectionDownChanged.emit(not items[0].isSelected())
            self.canMoveSelectionUpChanged.emit(not items[-1].isSelected())
            self.canDeleteItemSelectionChanged.emit(True)
            self.canMoveSelectionToLayerAboveChanged.emit(True if self._layerAbove(activeLayer) else False)
            self.canMoveSelectionToLayerBelowChanged.emit(True if self._layerBelow(activeLayer) else False)
            self.canMoveSelectionToNewLayerChanged.emit(True)
        else:
            self.canMoveSelectionDownChanged.emit(False)
            self.canMoveSelectionUpChanged.emit(False)
            self.canDeleteItemSelectionChanged.emit(False)
            self.canMoveSelectionToLayerAboveChanged.emit(False)
            self.canMoveSelectionToLayerBelowChanged.emit(False)
            self.canMoveSelectionToNewLayerChanged.emit(False)

        
        if scene and not editMode:
            if activeLayer and activeLayer.childItems():
                self.canSelectAllChanged.emit(len(activeLayer.childItems()) != len(scene.selectedItems()))
        else:
            self.canSelectAllChanged.emit(False)
            
            
    def _updateCopyPasteTriggers(self, scene, clipboard):
        if scene:
            activeLayer = scene.activeLayer()
            editMode    = scene.editMode() 
        else:
            activeLayer  = None
            editMode     = None
   
        if activeLayer and not editMode:
            self.canCopyChanged.emit(True)
            self.canPasteChanged.emit(clipboard.hasData())
        else:
            self.canCopyChanged.emit(False)
            self.canPasteChanged.emit(scene and clipboard.hasLayer())
    
    
    def _updateLayerSignals(self, scene):
        if scene:
            activeLayer = scene.activeLayer()
            layers      = scene.layers()
            editMode    = scene.editMode()
        else:
            activeLayer = None
        
        if activeLayer and not editMode:
            self.canMoveLayerUpChanged.emit(True if   activeLayer is not layers[-1] else False)
            self.canMoveLayerDownChanged.emit(True if activeLayer is not layers[0] else False)
            self.canDeleteActiveLayerChanged.emit(True)
            self.canDuplicateLayerChanged.emit(True)

        else:
            self.canMoveLayerUpChanged.emit(False)
            self.canMoveLayerDownChanged.emit(False)
            self.canDeleteActiveLayerChanged.emit(False)
            self.canDuplicateLayerChanged.emit(False)
            
        if scene and not editMode:
            self.canAddNewLayerChanged.emit(True)
        else:
            self.canAddNewLayerChanged.emit(False)


    def _sortByZOrder(self, items):
        cmpZ     = lambda x,y: ( 1 if x.zValue()  > y.zValue() else 
                                -1 if  x.zValue() < y.zValue() else 0)
        items.sort(cmp=cmpZ)
        return items
    
    
    def _moveItemSelectionZOrder(self, parentItem, selectedItems, offset, commandBatch):
        assert offset == -1 or offset == 1
            
        items = parentItem.childItems() # sorted by zValue
        self._sortByZOrder(selectedItems)
        if offset > 0:  
            selectedItems.reverse()
          
        for item in selectedItems:
            z     = item.zValue()
            index = int(z) + offset
            if -1 < index < len(items):
                other = items[index] 
                # swap to keep items z sorted:
                items[index]  = items
                items[int(z)] = other
                
                commands.newChangeZValueCommand(other, z, commandBatch)
                commands.newChangeZValueCommand(item, index, commandBatch)
            
            
    def _stackItemsAfter(self, parentItem, items, afterItem, commandBatch):
        assert afterItem not in items
        assert afterItem in parentItem.childItems()
        
        otherItems = self._sortByZOrder(list(set(parentItem.childItems()) - set(items)))
        z = 0
        for item in otherItems:
            commands.newChangeZValueCommand(item, z, commandBatch)
            z += 1
            if item is afterItem:
                for i in items:
                    commands.newChangeZValueCommand(i, z, commandBatch)
                    z += 1
            
        
    def _moveToBottom(self, selectedItems, items, commandBatch):
        for z,item in enumerate(selectedItems):
            if item.zValue() != z:
                commands.newChangeZValueCommand(item, z, commandBatch)
            
        for z, item in enumerate(items, z+1):
            if item not in selectedItems and item.zValue() != z:
                    commands.newChangeZValueCommand(item, z, commandBatch)
    
        
    def _moveToTop(self, selectedItems, items, commandBatch):
        z = 0
        for item in items:
            if item not in selectedItems and item.zValue() != z:
                commands.newChangeZValueCommand(item, z, commandBatch)
                z += 1
        
        for z,item in enumerate(selectedItems,z):
            if item.zValue() != z:
                commands.newChangeZValueCommand(item, z, commandBatch)


    def _pasteLayerFromClipboard(self, clipboard, commandBatch = None):
        scene  = self._scene()
        layer  = clipboard.data()[0].copy()
        
        if commandBatch:
            commands.newAddExistingLayerCommand(scene, layer, commandBatch)
        else:
            self._pushCommand(commands.newAddExistingLayerCommand(scene, layer))
        
        return layer
        
        
    def _pasteItemsFromClipboard(self, clipboard):
        if not clipboard.hasData():
            return
        
        scene = self._scene()
        view  = scene.views()[0]
        items = clipboard.data()
        batch = commands.newCommandBatch()
                
        scene.clearSelection()
        
        posMax = posMin = items[0].value("position")
        for item in items:
            pos = item.value("position")
            posMin = pos if (pos.x() < posMin.x() and pos.y() < posMin.y()) else posMin
            posMax = pos if (pos.x() > posMax.x() and pos.y() > posMax.y()) else posMax
        
        itemsCenterPos = posMin + ((posMax - posMin) / 2)
        pastePos       = scene.mousePosition() if view.hasMouse() else view.center()

        for clipboardItem in items:
            item     = clipboardItem.copy()
            itemPos  = item.value("position")
            pos      = pastePos + (itemPos - itemsCenterPos)
            commands.newAddItemCommand(scene, item, pos, select=True, commandBatch=batch)
            
        self._pushCommand(batch)
      
      
    def _copySelectedItemsToClipboard(self, clipboard):
        items = self._sortByZOrder(self._scene().selectedItems())
        
        clipboard.clear() 
        for item in items:
            clipboard.append(item.copy())
            
    
    def _copyActiveLayerToClipboard(self, clipboard): 
        activeLayer = self._scene().activeLayer().copy()
        
        clipboard.clear() 
        clipboard.append(activeLayer)
    
    
    def _moveItemToAnotherLayer(self, items, dstLayer, cmdBatch):
        scene     = self._scene()
        clipboard = ItemsClipboard()
                
        for item in self._sortByZOrder(items):
            commands.newDeleteItemCommand(scene, item, commandBatch=cmdBatch)
            commands.newAddItemCommand(scene, item, item.value("position"), layer = dstLayer,
                                       select=True, commandBatch=cmdBatch)
    
    def _layerAbove(self, layer):
        layers    =  self._scene().layers()
        nextIndex = layers.index(self._scene().activeLayer()) + 1
        
        if nextIndex < len(layers):
            return layers[nextIndex]
        else:
            return None
        
        
    def _layerBelow(self, layer):
        layers    =  self._scene().layers()
        nextIndex = layers.index(self._scene().activeLayer()) - 1
        
        if nextIndex >= 0:
            return layers[nextIndex]
        else:
            return None
        
        
    def _deleteSelectedItems(self, cmdBatch):
        scene = self._scene()              
        for item in scene.selectedItems():
            commands.newDeleteItemCommand(scene, item, cmdBatch)
        
        
    ## Action callback functions ##

    def addNewLayer(self):
        if self._scene():
            cmd = commands.newAddLayerCommand(self._scene())
            self._pushCommand(cmd)
        
    
    def deleteActiveLayer(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        scene = self._scene()
        cmd = commands.newDeleteLayerCommand(scene, scene.activeLayer())
        self._pushCommand(cmd)
    
    
    def deleteSelectedItems(self):
        if self._scene() is None or not self._scene().selectedItems():
            return

        batch = commands.newCommandBatch()

        self._deleteSelectedItems(batch) 
        if batch.childCount() > 0:
            self._pushCommand(batch)    

    
    def copyToClipboard(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return

        scene         = self._scene()
        clipboard     = self._clipboard
        
        if scene.selectedItems():
            self._copySelectedItemsToClipboard(clipboard)
        elif scene.activeLayer():
            self._copyActiveLayerToClipboard(clipboard)
                    
        
    def cutToClipboard(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return

        self.copyToClipboard()
        
        if self._scene().selectedItems():
            self.deleteSelectedItems()
        else:
            self.deleteActiveLayer()
    
        
    def pasteFromClipboard(self):
        if self._scene() is None or self._clipboard.hasData() == False:
            return

        clipboard = self._clipboard
        if self._clipboard.hasLayer():
            self._pasteLayerFromClipboard(clipboard)
        else:
            self._pasteItemsFromClipboard(clipboard)
        
    
    def moveItemSelectionUp(self):
        if self._scene() is None or not self._scene().selectedItems():
            return

        cmdBatch = commands.newCommandBatch()
        self._moveItemSelectionZOrder(self._scene().activeLayer(), 
                                      self._scene().selectedItems(), +1, cmdBatch)
        
        self._pushCommand(cmdBatch)

       
    def moveItemSelectionDown(self): 
        if self._scene() is None or not self._scene().selectedItems():
            return

        cmdBatch = commands.newCommandBatch() 
        self._moveItemSelectionZOrder(self._scene().activeLayer(), 
                                      self._scene().selectedItems(), -1, cmdBatch)
       
        self._pushCommand(cmdBatch)

    
    def moveItemSelectionToTop(self):
        if self._scene() is None or not self._scene().selectedItems():
            return
        
        cmdBatch      = commands.newCommandBatch()
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
    
        self._moveToTop(selectedItems, items,cmdBatch)
        self._pushCommand(cmdBatch)
                

        
    def moveItemSelectionToBottom(self):
        if self._scene() is None or not self._scene().selectedItems():
            return
        
        cmdBatch      = commands.newCommandBatch()
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
        
        self._moveToBottom(selectedItems, items, cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerUp(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        cmdBatch = commands.newCommandBatch()
        scene    = self._scene()
        self._moveItemSelectionZOrder(scene.rootItem(), [scene.activeLayer()], +1, cmdBatch)
        
        self._pushCommand(cmdBatch)
    
    
    def moveLayerDown(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        cmdBatch = commands.newCommandBatch()
        scene    = self._scene()
        
        self._moveItemSelectionZOrder(scene.rootItem(), 
                                      [scene.activeLayer()], -1, cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerToTop(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        cmdBatch = commands.newCommandBatch()
        scene = self._scene()
        
        self._moveToTop([scene.activeLayer()], scene.rootItem().childItems(), cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerToBottom(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        scene    = self._scene()
        cmdBatch = commands.newCommandBatch()

        self._moveToBottom([scene.activeLayer()], scene.rootItem().childItems(), cmdBatch)
        self._pushCommand(cmdBatch)


    def duplicateActiveLayer(self):
        if self._scene() is None or self._scene().activeLayer() is None:
            return
        
        cmdBatch    = commands.newCommandBatch()
        clipboard   = ItemsClipboard()
        scene       = self._scene()
        
        self._copyActiveLayerToClipboard(clipboard)
        layer = self._pasteLayerFromClipboard(clipboard, cmdBatch)
        self._stackItemsAfter(scene.rootItem(), [layer], scene.activeLayer(), cmdBatch)

        self._pushCommand(cmdBatch)


    def moveSelectionToLayerAbove(self):
        if self._scene() is None:
            return 
        if not self._scene().selectedItems():
            return
        if self._layerAbove(self._scene().activeLayer()) is None:
            return
       
        scene       = self._scene()
        activeLayer =  scene.activeLayer()
        cmdBatch    = commands.newCommandBatch()
        layerAbove  = self._layerAbove(activeLayer)
        items       = scene.selectedItems()
        
        scene.setActiveLayer(layerAbove)
        self._moveItemToAnotherLayer(items, layerAbove, cmdBatch)    
        self._pushCommand(cmdBatch)
    
    
    def moveSelectionToLayerBelow(self):
        if self._scene() is None:
            return 
        if not self._scene().selectedItems():
            return
        if self._layerBelow(self._scene().activeLayer()) is None:
            return
        
        scene       = self._scene()
        activeLayer =  scene.activeLayer()
        cmdBatch    = commands.newCommandBatch()
        layerBelow  = self._layerBelow(activeLayer)
        items       = scene.selectedItems()
        
        scene.setActiveLayer(layerBelow)
        self._moveItemToAnotherLayer(items, layerBelow, cmdBatch)    
        self._pushCommand(cmdBatch)
    
    
    def moveSelectionToNewLayer(self):
        if self._scene() is None:
             return 
        
        cmdBatch    = commands.newCommandBatch()
        scene       = self._scene()
        items       = scene.selectedItems()
        
        layer = commands.newAddLayerCommand(scene, cmdBatch)._layer
        self._moveItemToAnotherLayer(items, layer, cmdBatch)
        
        self._pushCommand(cmdBatch)
        scene.setActiveLayer(layer)


    def selectAll(self):
        if self._scene() is None:
            return 
        
        scene = self._scene()
        
        scene.clearSelection()
        for item in scene.activeLayer().childItems():
            item.setSelected(True)

        
        
                
class ViewController(BaseController):
    
    
    canZoomInChanged                 = Signal(bool)
    canZoomOutChanged                = Signal(bool)
    canResetZoomChanged              = Signal(bool)
    canCenterOnSeletionMasterChanged = Signal(bool)
    
    showGridChanged                  = Signal(bool)
    snap2GridChanged                 = Signal(bool)
    showAxisCanged                   = Signal(bool)
    showCameraCanged                 = Signal(bool)
    
    zoomChanged                      = Signal(int, int) # old, new 
    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self, sceneGroup)

        self._welcomeScene  = None
        self._view          = None
        self._zoomByScene   = []
        self._centerByScene = [] 
        
        self._maxZoom   = 100 * 10 #FIXME: move to config
        self._minZoom   = 100 / 10
        self._zoomStep  = 10
    
        sceneGroup.activeSceneChanged.connect(self._handleActiveSceneChanged)
        sceneGroup.sceneWasAdded.connect(self._handleSceneWasAdded)
        sceneGroup.sceneWasRemoved.connect(self._handleSceneWasRemoved)

        self.zoomChanged.connect(self._updateAllSignalTriggers)
        sceneGroup.activeSceneChanged.connect(self._updateAllSignalTriggers)
        sceneGroup.selectionChanged.connect(self._updateAllSignalTriggers)


    def _updateAllSignalTriggers(self):
        if self._scene():

            self.canZoomInChanged.emit(self.zoomPercentage() < self._maxZoom)
            self.canZoomOutChanged.emit(self.zoomPercentage() > self._minZoom)    
            self.canResetZoomChanged.emit(self.zoomPercentage() != 100)
            self.canCenterOnSeletionMasterChanged.emit(len(self._scene().selectedItems()) > 0)  
            self.showGridChanged.emit(self._scene().isShowGrid())  
            self.snap2GridChanged.emit(self._scene().isSnap2Grid())
            self.showAxisCanged.emit(self._scene().isShowAxis())  
            self.showCameraCanged.emit(self._scene().isShowCamera())  

        else:
            self.canCenterOnSeletionMasterChanged.emit(False)
            self.canZoomInChanged.emit(False)
            self.canZoomOutChanged.emit(False)    
            self.canResetZoomChanged.emit(False)
            self.showGridChanged.emit(False)
            self.snap2GridChanged.emit(False)
            self.showAxisCanged.emit(False)  
            self.showCameraCanged.emit(False)  

            
    
    def _handleSceneWasAdded(self, index):
        self._zoomByScene.append(100)
        self._centerByScene.append(QPointF(0,0)) 
    
    
    def _handleSceneWasRemoved(self, index):
        self._centerByScene.pop(index)
        self._zoomByScene.pop(index)
    
    
    def _handleActiveSceneChanged(self, new, old):
        
        if old: # save zoom & center
            index = self.sceneGroup.index(old) #FIXME: don't really need inexes here...
            self._centerByScene[index] = self._view.center()
            self._zoomByScene[index]   = self.zoomPercentage()
            
        if new:
            self._view.setScene(new)
            index = self.sceneGroup.index(new)
            self.setZoomPercentage(self._zoomByScene[index])
            self._view.centerOn(self._centerByScene[index])
            
        else:
            self._view.setZoomPercentage(100)
            self._view.setScene(self._welcomeScene)
    
           
    def canChangeZoom(self):
        return self._scene() != None
    
    
    def maxZoom(self):
        return self._maxZoom
    
    
    def minZoom(self):
        return self._minZoom
    
    
    def zoomStep(self):
        return self._zoomStep
    
           
    def setWelcomeScene(self, welcomeScene):
        self._welcomeScene = welcomeScene
        self._view.setScene(welcomeScene)
        
        
    def setView(self, view):
        assert self._view is None
        self._view = view
        view.setScene(self._welcomeScene)
    
    
    def zoomPercentage(self):
        return self._view.zoomPercentage()
    
    
    def resetZoom(self):
        self.setZoomPercentage(100)
    
    
    def zoomIn(self):
        self.setZoomPercentage(self.zoomPercentage() + self._zoomStep)
        
    
    def zoomOut(self):
        self.setZoomPercentage(self.zoomPercentage() - self._zoomStep)
    
    
    def setZoomPercentage(self, percentage):
        if not self._scene():
            return
        
        if percentage > self._maxZoom:
            percentage = self._maxZoom
        if percentage < self._minZoom:
            percentage = self._minZoom

        oldZoom = self.zoomPercentage()
        self._view.setZoomPercentage(percentage)
        
        # emit signals
        self.zoomChanged.emit(percentage, oldZoom)
    
    
    def centerOnOrigin(self):
        if self._scene():
            self._view.centerOn(0,0)
    
    
    def centerOnSelectionMaster(self):
        if self._scene() is None or self._scene().selectionMaster() is None:
            return 
        
        master = self.sceneGroup.activeScene().selectionMaster()
        self._view.centerOn(master)
    
    
    def centerOnCamera(self):
        if not self._scene():
            return
        
        point = self._view.scene().rootItem().value("camera")
        self._view.centerOn(point)
        
        
    def setShowAxis(self, show):
        if self._scene():
            self._scene().setShowAxis(show)
    
    
    def setShowGrid(self, show):
        if self._scene():
            self._scene().setShowGrid(show)
        
        
    def setSnap2Grid(self, snap):
        if self._scene():
            self._scene().setSnap2Grid(snap)
        
        
    def setShowCamera(self, show):
        if self._scene():
            self._scene().setShowCamera(show)
        

        
         
class PropertiesController(BaseController):
    
    canLockPropertyChanged       = Signal(bool)
    lockSelectedPropertyChanged  = Signal(bool)
    
    canUnlockAllPropertiesChanged       = Signal(bool)
    canResetPropertyChanged             = Signal(bool)
    canReplicateSelectedPropertyChanged = Signal(bool)
    
    
    def __init__(self,sceneGroup):
        BaseController.__init__(self, sceneGroup)
        
        itemsModel = sceneGroup.itemPropertiesModel()        
        itemsModel.selectionModel().selectionChanged.connect(self._updateAllSignalTriggers)
        itemsModel.editorItemChanged.connect(self._updateAllSignalTriggers)
        sceneGroup.activeItemPoprertyChanged.connect(self._updateAllSignalTriggers)
        
        
    def _updateAllSignalTriggers(self):
        activeItem       = self.activeItem()
        selectedProperty = self.selectedProperty()
        editMode         = self._scene().editMode() if self._scene() else None

        
        if selectedProperty and not editMode:
            self.canLockPropertyChanged.emit(True)
            self.lockSelectedPropertyChanged.emit(selectedProperty.locked())
            self.canResetPropertyChanged.emit(selectedProperty.changed())
            self.canReplicateSelectedPropertyChanged.emit(self._canReplicateSelectedProperty())
        else:
            self.canLockPropertyChanged.emit(False)
            self.lockSelectedPropertyChanged.emit(False)
            self.canResetPropertyChanged.emit(False)
            self.canReplicateSelectedPropertyChanged.emit(False)

            
        if activeItem:
            self.canUnlockAllPropertiesChanged.emit(True)
        else:
            self.canUnlockAllPropertiesChanged.emit(False)
        
        
    def selectedProperty(self):
        propertiesModel = self.sceneGroup.itemPropertiesModel()
        selectionModel  = propertiesModel.selectionModel()
        
        rows = selectionModel.selectedRows(propertiesModel.NameColumn)
        if rows:
            return propertiesModel.data(rows[0], propertiesModel.PropertyRole)        
        else:
            return None
        
        
    def activeItem(self):
        propertiesModel = self.sceneGroup.itemPropertiesModel()
        return propertiesModel.item()
          
          
    def lockSelectedProperty(self, lock):
        property = self.selectedProperty()
        if property:
            property.setLocked(lock)
            
            
    def unlockAllProperties(self):
        item = self.activeItem()
        if item:
            for p in item.properties():
                p.setLocked(False)
        self._updateAllSignalTriggers()
        
        
    def resetProperty(self):
        property = self.selectedProperty()
        item     = self.activeItem()
        
        if property and property.changed():
            self._pushCommand(commands.newItemPropertyResetCommand(property))

        
    def replicateSelectedProperty(self):
        selectedProperty = self.selectedProperty()
        selectedItems    = self._scene().selectedItems()

        if self._canReplicateSelectedProperty() == False:
            return
        else:
            selectedItems.pop(selectedItems.index(selectedProperty.item()))
        
        propertyName = selectedProperty.name()
        cmdBatch     = commands.newCommandBatch()
        value        = selectedProperty.value()
        
        if hasattr(selectedProperty, "parent"): # component
            parentName = selectedProperty.parent().name()
            for item in selectedItems:
                p = item.property(parentName)
                if p is not None and value != p.value(propertyName):
                    commands.newEditPropertyCommand(p.component(propertyName), value, cmdBatch)
        else: 
            for item in selectedItems:
                if item.hasProperty(propertyName) and value != item.value(propertyName):
                    commands.newEditItemPropertyCommand(item, propertyName, value, cmdBatch)
        
        self._pushCommand(cmdBatch)
        
    
    def _canReplicateSelectedProperty(self):
        selectedProperty = self.selectedProperty()
        selectedItems    = self._scene().selectedItems()

        if selectedProperty is None or len(selectedItems) < 2:
            return False
        else:
            selectedItems.pop(selectedItems.index(selectedProperty.item()))
        
        value        = selectedProperty.value()
        propertyName = selectedProperty.name()
        dCount       = 0
        
        if hasattr(selectedProperty, "parent"): # component
            parentName = selectedProperty.parent().name()
            for item in selectedItems:
                p = item.property(parentName)
                if p is not None and value != p.value(propertyName):
                        dCount += 1
        else: # property
            for item in selectedItems:
                if item.hasProperty(propertyName) and value != item.value(propertyName):
                    dCount += 1
            
        return dCount > 0 
                
        

