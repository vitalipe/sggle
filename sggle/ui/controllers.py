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
    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self)
        
        self._sceneGroup          = sceneGroup
        self._sceneToFilePathMap  = {}
        self._sceneSaveStateMap   = {}


    def new(self):
        print "new"
        
        newScene = scene.newEmptyGraphicsScene()
        self._sceneGroup.addScene(newScene)
        
        self._sceneToFilePathMap[newScene] = None
        self._sceneSaveStateMap[newScene]  = False
    
    
    def openScene(self): 
        fileName   = "/tmp/test.xml" #FIXME: create file dialog
        fileType   = "xml"
        
        fileStream = open(fileName, "r")
        newScene = saveload.readScene( fileStream, fileType)
        
        self._sceneGroup.addScene(newScene)
        print "opend"
        
    
    
    def saveActiveScene(self):
        scene      = self._sceneGroup.activeScene()
        fileName   = "/tmp/test.xml"
        fileType   = "xml"
        
        fileStream = open(fileName, "w")
        saveload.writeScene(scene, fileStream, fileType)
        print "saved"
    
    
    def saveActiveSceneAs(self):
        pass
    
    
    def closeActiveScene(self):
        self.closeScene(self._sceneGroup.index(self._sceneGroup.activeScene()))
    
    
    def closeScene(self, sceneIndex):
        self._sceneGroup.removeScene(self._sceneGroup.scene(sceneIndex))
    
    
    def exit(self):
        pass
        

class ItemsController(BaseController):
    
#    canMoveItemsUpChanged   = Signal(bool)
#    canMoveItemsDownChanged = Signal(bool)
#    canMoveLayerUpChanged   = Signal(bool)
#    canMoveLayerDownChanged = Signal(bool)
#    
    
    def __init__(self, sceneGroup):
        BaseController.__init__(self)
        
        self._sceneGroup   = sceneGroup
        self._commandBatch = None
        
        sceneGroup.itemPropertyChangeRequest.connect(self._handleItemPropertyChangeRequest)
        sceneGroup.editModeChanged.connect(self._handleSceneEditModeChanged)
        
               
    def _scene(self):
        return self._sceneGroup.activeScene()
        
           
    def _pushCommand(self, cmd):
        self._sceneGroup.undoGroup().activeStack().push(cmd)
        
        
    def _handleSceneEditModeChanged(self, editMode, oldEditMode):
        if self._commandBatch and self._commandBatch.childCount() > 0:
            self._pushCommand(self._commandBatch)
        
        if editMode:
            self._commandBatch = commands.newCommandBatch()
        else:
            self._commandBatch = None
                
        
    def _handleItemPropertyChangeRequest(self, item, property, value):
        cmd = commands.newEditItemPropertyCommand(item, property, value, self._commandBatch) 
        
        if self._commandBatch:
            cmd.redo()
        else:
            self._pushCommand(cmd)        
    
    
    def moveItemSelectionUp(self):
        self._moveItemSelectionZOrder(self._scene().activeLayer(), self._scene().selectedItems(), +1)
            
       
    def moveItemSelectionDown(self):          
        self._moveItemSelectionZOrder(self._scene().activeLayer(), self._scene().selectedItems(), -1)
 
    
    def moveItemSelectionToTop(self):
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
    
        self._moveToTop(selectedItems, items)

        
    def moveItemSelectionToBottom(self):
        items         = self._scene().activeLayer().childItems()
        selectedItems = self._sortByZOrder(self._scene().selectedItems())
        
        self._moveToBottom(selectedItems, items)
    
    
    def moveLayerUp(self):
        scene = self._scene()
        self._moveItemSelectionZOrder(scene.rootItem(), [scene.activeLayer()], +1)
    
    
    def moveLayerDown(self):
        scene = self._scene()
        self._moveItemSelectionZOrder(scene.rootItem(), [scene.activeLayer()], -1)
    
    
    def moveLayerToTop(self):
        scene = self._scene()
        self._moveToTop([scene.activeLayer()], scene.rootItem().childItems())
    
    
    def moveLayerToBottom(self):
        scene = self._scene()
        self._moveToBottom([scene.activeLayer()], scene.rootItem().childItems())
    
    
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
    
    
    def _moveItemSelectionZOrder(self, parentItem, items, offset):
        assert offset == -1 or offset == 1
            
        self._sortByZOrder(items)
        if offset > 0:
            items.reverse()
        
        for item in items:
            z     = item.zValue()
            items = parentItem.childItems() # update on each iteration
            index = int(z) + offset
            if -1 < index < len(items):
                other = items[index] # sorted by zValue
                # swap:
                other.setZValue(z)
                item.setZValue(index)
            
            
    def _moveToBottom(self, selectedItems, items):
        for z,item in enumerate(selectedItems):
            item.setZValue(z)
            
        for z, item in enumerate(items, z+1):
            if item not in selectedItems:
                item.setZValue(z)
    
        
    def _moveToTop(self, selectedItems, items):
        z = 0
        for item in items:
            if item not in selectedItems:
                item.setZValue(z)
                z += 1
        
        for z,item in enumerate(selectedItems,z):
            item.setZValue(z)
        
        
        
        
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
        
        self._maxZoom   = 100 * 10
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

    