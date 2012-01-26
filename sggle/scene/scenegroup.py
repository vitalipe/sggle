'''
Created on Dec 30, 2011

@author: vitali
'''

from PySide.QtCore  import QObject
from PySide.QtCore  import Signal
from PySide.QtGui   import QUndoStack 

import models



class SceneGroup(QObject):
    
    # Signals
    activeSceneChanged         =  Signal(object, object) # @param: new @param: old 
    sceneWasAdded              =  Signal(int, str)
    sceneWasRemoved            =  Signal(int)
    
    # Scene Signals
    selectionChanged           =  Signal()
    activeLayerChanged         =  Signal(object)
    selectionMasterChanged     =  Signal(object)
    itemPropertyWasChanged     =  Signal(object, str)
    editModeChanged            =  Signal(object, object)
    listOfLayersChanged        =  Signal(list)
    listOfItemsChanged          = Signal(object) 

    
    def __init__(self, undoGroup):
        QObject.__init__(self)
        
        
        self._undoGroup         = undoGroup
        self._activeScene       = None
        self._sceneList         = []
        
        self._layerModel      = models.LayerListModel(self)
        self._itemsModel      = models.ItemTreeModel(self)
        self._propertiesModel = models.ItemPropertiesModel(self)
    
    
    def index(self, scene):
        if scene in self.sceneList():
            return self.sceneList().index(scene)
        else:
            return None
        
        
    def swapIndexs(self, fromIndex, toIndex):
        sceneList = self.sceneList()
        tmp       = sceneList[toIndex]
        sceneList[toIndex]   = sceneList[fromIndex]
        sceneList[fromIndex] = tmp
        
        
    def scene(self, index):
        try:
            return self.sceneList()[index]
        except IndexError:  
            return None
    
    
    def activeScene(self):
        return self._activeScene
    
    
    def setActiveScene(self, scene):
        assert scene in self.sceneList() or scene is None
        
        if scene is self.activeScene():
            return
        
        if self.activeScene():
            self._disconnectScene(self.activeScene())
        self._connectScene(scene)
        
        oldActiveScene     = self._activeScene
        self._activeScene = scene
        self._undoGroup.setActiveStack(scene.undoStack() if scene else None)
 
            
        
        self.activeSceneChanged.emit(scene, oldActiveScene)
        
    
    def addScene(self, scene):
        assert scene not in self.sceneList()
        
        self._sceneList.append(scene)
        self._undoGroup.addStack(scene.undoStack())
        
        self.sceneWasAdded.emit(self.index(scene), scene.rootItem().value("name"))
        
        if self.activeScene() is None:
            self.setActiveScene(scene)
        

    def removeScene(self, scene):        
        assert scene in self.sceneList()
        
        if scene is self.activeScene():
            if len(self.sceneList()) > 1: # then pick the one before or after
                index = self.index(scene)
                nextScene = self.sceneList()[index + (-1 if index else 1)]
            else: 
                nextScene = None
            self.setActiveScene(nextScene)    
        
        index = self.sceneList().index(scene)
        self._sceneList.pop(index)
        self._undoGroup.removeStack(scene.undoStack())
        
        self.sceneWasRemoved.emit(index)
        
        
    def sceneList(self):
        return self._sceneList
    
    
    def undoGroup(self):
        return self._undoGroup
    
    
    def layerListModel(self):
        return self._layerModel
    
    
    def activeItemsTreeModel(self):
        return self._itemsModel
    
    
    def itemPropertiesModel(self):
        return self._propertiesModel
            
            
    # FIXME: cleanup code
    def _connectScene(self, scene):
        if scene is None:
            return 
        
        scene.selectionChanged.connect(self.selectionChanged.emit)
        scene.activeLayerChanged.connect(self.activeLayerChanged.emit)
        scene.selectionMasterChanged.connect(self.selectionMasterChanged.emit)
        scene.editModeChanged.connect(self.editModeChanged.emit)
        scene.listOfLayersChanged.connect(self.listOfLayersChanged.emit)
        scene.listOfItemsChanged.connect(self.listOfItemsChanged.emit)
        scene.itemPropertyWasChanged.connect(self.itemPropertyWasChanged.emit)

        
    
    def _disconnectScene(self, scene):
        scene.selectionChanged.disconnect(self.selectionChanged.emit)
        scene.activeLayerChanged.disconnect(self.activeLayerChanged.emit)
        scene.selectionMasterChanged.disconnect(self.selectionMasterChanged.emit)
        scene.editModeChanged.disconnect(self.editModeChanged.emit)
        scene.listOfLayersChanged.disconnect(self.listOfLayersChanged.emit)
        scene.listOfItemsChanged.disconnect(self.listOfItemsChanged.emit)
        scene.itemPropertyWasChanged.disconnect(self.itemPropertyWasChanged.emit)
