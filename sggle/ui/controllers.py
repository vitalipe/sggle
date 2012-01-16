'''
Created on Nov 8, 2011

@author: vitali
'''

from os.path import splitext

from PySide.QtCore import QObject
from PySide.QtCore import Signal
from PySide.QtCore import QPointF
from PySide.QtGui  import QFileDialog


import sggle.scene.commands as commands
import sggle.scene as scene
import sggle.saveload.readwrite as saveload




class Clipboard(QObject):
    
    
    def __init__(self):
        QObject.__init__(self)
        
        self._data = []
        
        
    def clear(self):    
        self._data = []
    
    
    def data(self):
        return self._data
    
    
    def append(self, data):
        self._data.append(data)



class BaseController(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        
    


class SceneEditController(BaseController):
    
    clipboardDataAvailableChanged = Signal(bool)
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self)
        
        self._sceneGroup = sceneGroup
        self._clipboard  = Clipboard()
        
        sceneGroup.itemCreationRequest.connect(self._handleItemCreationRequest)
        
         
    def _scene(self):
        return self._sceneGroup.activeScene()
    
    
    def _pushCommand(self, cmd):
        self._sceneGroup.undoGroup().activeStack().push(cmd)
        
       
    def _handleItemCreationRequest(self, item, x, y):

        cmd = commands.newAddItemCommand(self._scene(), item, x, y)
        self._pushCommand(cmd)
        
        
    def addNewLayer(self):
        cmd = commands.newAddLayerCommand(self._scene())
        self._pushCommand(cmd)
        
    
    def deleteActiveLayer(self):
        if self._scene().editMode():
            return
        
        scene = self._scene()
        cmd = commands.newDeleteLayerCommand(scene, scene.activeLayer())
        self._pushCommand(cmd)
    
    
    def deleteSelectedItems(self):
        scene = self._scene()
        batch = commands.newCommandBatch()
        
        for item in scene.selectedItems():
            commands.newDeleteItemCommand(scene, item, batch)
        
        if scene.selectedItems():
            self._pushCommand(batch)    
    
    
    def copySelectionToClipboard(self):
        scene     = self._scene()
        clipboard = self._clipboard
        items     = scene.selectedItems()
        
        if items: 
            self._clipboard.clear()
            
        for item in items:
            clipboard.append(item.copy())
            
        self.clipboardDataAvailableChanged.emit(True if clipboard.data() else False)
        
    
    def cutSelectionToClipboard(self):
        self.copySelectionToClipboard()
        self.deleteSelectedItems()
    
    
    def pasteFromClipboard(self):
        assert self._clipboard.data()
        
        scene        = self._scene()
        clipboard    = self._clipboard
        batch        = commands.newCommandBatch()
        
        scene.clearSelection()
        
        for clipboardItem in clipboard.data():
            item = clipboardItem.copy()
            pos = item.value("position")
            commands.newAddItemCommand(scene, item, x = pos.x(), y = pos.y(), commandBatch=batch)

        self._pushCommand(batch)
            
            
    
    
class FileController(BaseController):
    
    sceneSaveStateChanged = Signal(object, bool) # scane, 
    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self)
        
        self._sceneGroup          = sceneGroup
        self._sceneToFilePathMap  = {}
        self._sceneSaveStateMap   = {}


    def _addScene(self, scene, filePath):
        self._sceneToFilePathMap[scene] = filePath
        self._sceneSaveStateMap[scene]  = False if filePath is None else True
        self._sceneGroup.addScene(scene)


    def _removeScene(self, scene):
        self._sceneToFilePathMap.pop(scene)
        self._sceneSaveStateMap.pop(scene)
        self._sceneGroup.removeScene(scene)
        
   
    def _writeScene(self, scene, filePath):
        fileType   = splitext(filePath)[1].strip(".")

        fileStream = open(filePath, "w") # FIXME: add error check
        saveload.writeScene(scene, fileStream, fileType)
        fileStream.close()
        
        self._sceneToFilePathMap[scene] = filePath
        self._sceneSaveStateMap[scene]  = False

        
    def new(self):        
        newScene = scene.newEmptyGraphicsScene()
        self._addScene(newScene, None)
    
    
    def openScene(self): 
        filters  = " ".join([ "*." + f for f in saveload.formats.knowFileFormats()])
        result   = QFileDialog.getOpenFileName(None, "Open Scene", None, filters)
        fileName = result[0]
        fileType = splitext(fileName)[1].strip(".")
        
        if not fileName: # canceled by user
            return
        
        fileStream = open(fileName, "r") #FIXME: Error check
        
        newScene = saveload.readScene( fileStream, fileType) #FIXME: pass scene ref
        
        fileStream.close()
        self._addScene(newScene, fileName)
        
        
    def saveScene(self, scene):
        filePath = self._sceneToFilePathMap.get(scene)
        if not filePath:
            self.saveSceneAs(scene)
        else:
            self._writeScene(scene, filePath)
        
        
    def saveActiveScene(self):
        self.saveScene(self._sceneGroup.activeScene())
    
    
    def saveActiveSceneAs(self):
        self.saveSceneAs(self._sceneGroup.activeScene())
        
        
    def saveSceneAs(self, scene):
        filters  = ";;".join([ f + " (*." + f + ")" for f in saveload.formats.knowFileFormats()])
        result   = QFileDialog.getSaveFileName(None, "Save Scene As", None, filters)
        if not result[0]:
            return
        
        fileName = result[0] + "." + (result[1].split())[0]
        self._writeScene(scene, fileName)
    
    
    def closeActiveScene(self):
        self.closeScene(self._sceneGroup.index(self._sceneGroup.activeScene()))
    
    
    def closeScene(self, sceneIndex):
        self._removeScene(self._sceneGroup.scene(sceneIndex)) #FIXME:Ugly API
    
    
    def exit(self):
        pass
        

class ItemsController(BaseController):
    
    canMoveSelectionUpChanged   = Signal(bool)
    canMoveSelectionDownChanged = Signal(bool)
    canMoveLayerUpChanged       = Signal(bool)
    canMoveLayerDownChanged     = Signal(bool)
    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self)
        
        self._sceneGroup   = sceneGroup
        self._commandBatch = None
        
        sceneGroup.itemPropertyChangeRequest.connect(self._handleItemPropertyChangeRequest)
        sceneGroup.editModeChanged.connect(self._handleSceneEditModeChanged)
        
        sceneGroup.listOfItemsChanged.connect(self._updateSignals)
        sceneGroup.selectionChanged.connect(self._updateSignals)

        
               
    def _scene(self):
        return self._sceneGroup.activeScene()
        
           
    def _pushCommand(self, cmd):
        self._sceneGroup.undoGroup().activeStack().push(cmd)
        
        
    def _handleSceneEditModeChanged(self, editMode, oldEditMode): #FIXME: move to scene
        if self._commandBatch and self._commandBatch.childCount() > 0:
            self._pushCommand(self._commandBatch)
        
        if editMode:
            self._commandBatch = commands.newCommandBatch()
        else:
            self._commandBatch = None
                
        
    def _handleItemPropertyChangeRequest(self, item, property, value): #FIXME: move to scene
        cmd = commands.newEditItemPropertyCommand(item, property, value, self._commandBatch) 
        
        if self._commandBatch:
            cmd.redo()
        else:
            self._pushCommand(cmd)        
    
    
    def _updateSignals(self):
        scene       = self._scene()
        layers      = scene.layers()
        selection   = scene.selectedItems()
        activeLayer = scene.activeLayer()
        items       = activeLayer.childItems() if activeLayer else []  

        if len(layers):
            self.canMoveLayerUpChanged.emit(True if   activeLayer is not layers[-1] else False)
            self.canMoveLayerDownChanged.emit(True if activeLayer is not layers[0] else False)
        else:
            self.canMoveLayerUpChanged.emit(False)
            self.canMoveLayerDownChanged.emit(False)
            
        if len(selection):
            self.canMoveSelectionDownChanged.emit(not items[0].isSelected())
            self.canMoveSelectionUpChanged.emit(not items[-1].isSelected())
        else:
            self.canMoveSelectionDownChanged.emit(False)
            self.canMoveSelectionUpChanged.emit(False)
        
        
        
    def moveItemSelectionUp(self):
        cmdBatch = commands.newCommandBatch()
        self._moveItemSelectionZOrder(self._scene().activeLayer(), 
                                      self._scene().selectedItems(), +1, cmdBatch)
        
        self._pushCommand(cmdBatch)

       
    def moveItemSelectionDown(self): 
        cmdBatch = commands.newCommandBatch() 
        self._moveItemSelectionZOrder(self._scene().activeLayer(), 
                                      self._scene().selectedItems(), -1, cmdBatch)
       
        self._pushCommand(cmdBatch)

    
    def moveItemSelectionToTop(self):
        cmdBatch      = commands.newCommandBatch()
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
    
        self._moveToTop(selectedItems, items,cmdBatch)
        self._pushCommand(cmdBatch)
                

        
    def moveItemSelectionToBottom(self):
        cmdBatch      = commands.newCommandBatch()
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
        
        self._moveToBottom(selectedItems, items, cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerUp(self):
        cmdBatch = commands.newCommandBatch()
        scene    = self._scene()
        self._moveItemSelectionZOrder(scene.rootItem(), [scene.activeLayer()], +1, cmdBatch)
        
        self._pushCommand(cmdBatch)
    
    
    def moveLayerDown(self):
        cmdBatch = commands.newCommandBatch()
        scene    = self._scene()
        
        self._moveItemSelectionZOrder(scene.rootItem(), 
                                      [scene.activeLayer()], -1, cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerToTop(self):
        cmdBatch = commands.newCommandBatch()
        scene = self._scene()
        
        self._moveToTop([scene.activeLayer()], scene.rootItem().childItems(), cmdBatch)
        self._pushCommand(cmdBatch)

    
    def moveLayerToBottom(self):
        scene    = self._scene()
        cmdBatch = commands.newCommandBatch()

        self._moveToBottom([scene.activeLayer()], scene.rootItem().childItems(), cmdBatch)
        self._pushCommand(cmdBatch)

    
    def alignSelectionVertical(self):
        selection = self._scene().selectedItems()
        master    = self._scene().selectionMaster()
        batch     = commands.newCommandBatch()
        x         = master.value("position").x()
        
        for item in selection:
            pos = item.value("position")
            pos.setX(x)
            commands.newEditItemPropertyCommand(item, "position", pos, batch)
            
        if batch.childCount() > 1:
            self._pushCommand(batch)
    
    
    def alignSelectionHorizontal(self):
        selection = self._scene().selectedItems()
        master    = self._scene().selectionMaster()
        batch     = commands.newCommandBatch()
        y         = master.value("position").y()

        for item in selection:
            pos = item.value("position")
            pos.setY(y)
            commands.newEditItemPropertyCommand(item, "position", pos, batch)
            
        if batch.childCount() > 1:
            self._pushCommand(batch)

           
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

        
        
        
        
class ViewController(BaseController):
    
    
    canZoomInChanged  = Signal(bool)
    canZoomOutChanged = Signal(bool)
    zoomChanged       = Signal(int, int)
    
    
    def __init__(self, sceneGroup, welcomeScene):
        BaseController.__init__(self)

        self._sceneGroup    = sceneGroup
        self._welcomeScene  = welcomeScene
        self._view          = None
        self._zoomByScene   = []
        self._centerByScene = [] 
        
        self._maxZoom   = 100 * 10 #FIXME: move to config
        self._minZoom   = 100 / 10
        self._zoomStep  = 10
    
        sceneGroup.activeSceneChanged.connect(self._handleActiveSceneChanged)
        sceneGroup.sceneWasAdded.connect(self._handleSceneWasAdded)
        sceneGroup.sceneWasRemoved.connect(self._handleSceneWasRemoved)


    def _handleSceneWasAdded(self, index):
        self._zoomByScene.append(100)
        self._centerByScene.append(QPointF(0,0)) #FIXME: scene origin
    
    
    def _handleSceneWasRemoved(self, index):
        self._centerByScene.pop(index)
        self._zoomByScene.pop(index)
    
    
    def _handleActiveSceneChanged(self, new, old):
        
        if old: # save zoom & center
            index = self._sceneGroup.index(old)
            self._centerByScene[index] = self._view.center()
            self._zoomByScene[index]   = self.zoomPercentage()
            
        if new:
            self._view.setScene(new)
            index = self._sceneGroup.index(new)
            self.setZoomPercentage(self._zoomByScene[index])
            self._view.centerOn(self._centerByScene[index])
            
        else:
            self._view.setScene(self._welcomeScene)
           
    
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
        assert self._view
        assert self._sceneGroup.activeScene()
        
        if percentage > self._maxZoom:
            percentage = self._maxZoom
        if percentage < self._minZoom:
            percentage = self._minZoom

        oldZoom = self.zoomPercentage()
        self._view.setZoomPercentage(percentage)
        
        # emit signals
        self.zoomChanged.emit(percentage, oldZoom)
        self.canZoomInChanged.emit(percentage < self._maxZoom)
        self.canZoomOutChanged.emit(percentage > self._minZoom)
    
    
    def centerOnOrigin(self):
        assert self._view
        originPoint = self._sceneGroup.activeScene().rootItem().value("origin")
        self._view.centerOn(originPoint)
    
    
    def centerOnSelectionMaster(self):
        assert self._view
        assert self._sceneGroup.activeScene()
        
        master = self._sceneGroup.activeScene().selectionMaster()
        self._view.centerOn(master)
    
    
    def setShowOrigin(self, show):
        pass
    
    
    def setShowGrid(self, show):
        pass    

    