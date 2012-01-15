'''
Created on Dec 30, 2011

@author: vitali
'''

from math import floor
from math import ceil

from PySide.QtCore import Signal
from PySide.QtCore import Qt

from PySide.QtCore  import QLine
from PySide.QtGui  import QPen
from PySide.QtGui  import QColor
from PySide.QtGui  import QGraphicsScene 
from PySide.QtGui  import QGraphicsItem


import items.builtin
from sggle.resources import loader



class LayeredGraphicsScene(QGraphicsScene):
    
    selectionMasterChanged      = Signal(object)
    activeLayerChanged          = Signal(object)
    listOfLayersChanged         = Signal(list)   # @param - list of scene layers
    listOfItemsChanged          = Signal(object) # @param - parent object
        
        
    def __init__(self,):
        QGraphicsScene.__init__(self)
        
        self._rootItem        = items.newRootItem()
        self._activeLayer     = None
        self._selectionMaster = None
        
        #FIXME: use QSettings
        self._bgColor   = Qt.gray   
        self._showGrid  = True
        self._gridSize  = 100
        self._gridColor = Qt.black
        
        QGraphicsScene.addItem(self, self._rootItem)
        self.selectionChanged.connect(self._updateSelectionMaster)
        self.sceneRectChanged.connect(lambda r: self._buildGridLines(r))

    
    def rootItem(self): 
        return self._rootItem    
               
    def layers(self):
        return self._rootItem.childItems()
    

    def addLayer(self, layer):
        assert layer not in self.layers()
        
        layers = self.layers()
        if len(layers) > 0:   
            z = layers[-1].zValue() + 1
        else:
            z = 0
        layer.setZValue(z)
                
        layer.setParentItem(self._rootItem)
        self.listOfLayersChanged.emit(self.layers())
        self.setActiveLayer(layer)

    
    def removeLayer(self, layer):
        assert layer in self.layers()
        
        setNewActiveLayer = False
        if layer is self.activeLayer():
            self.setActiveLayer(None)
            setNewActiveLayer = True

        for item in layer.childItems():
            self.removeItem(item)
        
        layer.setParentItem(None)
        self.listOfLayersChanged.emit(self.layers())
        
        if setNewActiveLayer and self.layers():
            self.setActiveLayer(self.layers()[-1])
            
         
    def addItem(self, item, layer = None, aX = 0, aY = 0):
        assert item not in self.items()
        assert layer in self.layers() or self.activeLayer()
        
        layer = layer if layer else self.activeLayer()
  
        # Z
        layerItems = layer.childItems()
        if layerItems:   
            z = layerItems[-1].zValue() + 1
        else:
            z = 0
        
        item.setParentItem(layer)
        
        item.setValueDirectly("position", x=aX, y=aY)
        item.setZValue(z)
        
        if layer is self.activeLayer():
            self._activateItem(item)
            item.setSelected(True)
        
        
        
        
    def removeItem(self, item):
        assert item in self.items()
        
        for child in item.childItems():
            self.removeItem(child)
        
        self._deactivateItem(item)
        QGraphicsScene.removeItem(self, item)
        
    
    def activeLayer(self):
        return self._activeLayer
    
    
    def setActiveLayer(self, newActiveLayer):
        assert newActiveLayer is None or newActiveLayer in self.layers()
        
        if newActiveLayer is not self.activeLayer():
            oldActive         = self.activeLayer()
            
            if oldActive is not None:
                self._deactivateLayerItems(oldActive)
                
            self._activeLayer = newActiveLayer
                
            if newActiveLayer is not None:
                self._activateLayerItems(newActiveLayer)
                            
            # the order of signals is important here 
            self.setSelectionMaster(None) 
            self.activeLayerChanged.emit(newActiveLayer)


    def adjustParallax(self, center):
        x,y = center.toTuple()
        for layer in self.layers():
            layer._adjustParallax(x,y)

        
    def selectionMaster(self):
        return self._selectionMaster
   
    
    def setSelectionMaster(self, item):
        assert item is None or self.activeLayer() is None or item in self.activeLayer().childItems()

        if self.activeLayer() is None:
            return # Can happen with multiple views
        
        oldSelectionMaster = self.selectionMaster()
        if item is not oldSelectionMaster:
            self._selectionMaster = item
            self.selectionMasterChanged.emit(item)


    def drawBackground(self, painter, rect):
        QGraphicsScene.drawBackground(self, painter, rect)
        painter.fillRect(rect, self._bgColor) 
        if self._showGrid:
            self._drawGrid(painter, rect)
    
    
        # << Helper methods >> #

    def _drawGrid(self, painter, rect):
        color    = self._gridColor

        painter.setPen(QPen(color, 0.0)) 
        painter.drawLines(self._gridLines)


    def _buildGridLines(self, rect):
        gridSize   = self._gridSize
        realLeft   = int(floor(rect.left()))
        realRight  = int(ceil(rect.right()))
        realTop    = int(floor(rect.top()))
        realBottom = int(ceil(rect.bottom()))
        
        lines = []
        firstLeft = realLeft - (realLeft % gridSize) 
        firstTop  = realTop - (realTop % gridSize)   

        for x in range(firstLeft, realRight, gridSize):
            lines.append(QLine(x, realTop, x, realBottom))
            
        for y in range(firstTop, realBottom, gridSize):
            lines.append(QLine(realLeft, y, realRight, y))
        
        self._gridLines = lines
        
        
    def _activateLayerItems(self, layer):
        
        for item in layer.childItems():  
            self._activateItem(item)   
       
        
    def _deactivateLayerItems(self, layer):
        for item in layer.childItems():     
            self._deactivateItem(item)
        
        
    def _activateItem(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable            , True)
        item.setFlag(QGraphicsItem.ItemIsSelectable         , True)
        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges , True)
    
    
    def _deactivateItem(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable            , False)
        item.setFlag(QGraphicsItem.ItemIsSelectable         , False)
        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges , False)
        
            
    def _updateSelectionMaster(self):
        master = self.selectionMaster() 
        items  = self.selectedItems()
        
        if master in items or (master is None and not items):
            return
        
        newMaster = items[0] if items else None
        self.setSelectionMaster(newMaster)
  
            
    
    
class EditableScene(LayeredGraphicsScene):
    
    # EditModes
    NoEditMode      = 0
    MoveEditMode    = 1
    RotateEditMode  = 2
    scaleEditMode   = 3
    PixmapDropMode  = 4
    
    RectDrawMode    = 5
    PathDrawMode    = 6
    ElipseDrawMod   = 7
    
       
    itemPropertyChangeRequest  = Signal(items.builtin.SceneItem, str, object)
    itemPropertyWasChanged     = Signal(object, str)
    itemCreationRequest        = Signal(object, float, float)
    editModeChanged            = Signal(int, int)
    
        
    def __init__(self,):
        LayeredGraphicsScene.__init__(self)
        
        self._editMode             = EditableScene.NoEditMode
        self._editModeCommandBatch = None
        self._editModeData         = None
        self._mousePos             = None
   
        
    def mousePosition(self):
        return self._mousePos
   
   
    def editMode(self):
        return self._editMode
    
    
    def enterEditMode(self, mode):
        assert type(mode) is int 
        assert self.editMode() == self.NoEditMode or mode == self.NoEditMode
        
        # clear data
        if mode == self.NoEditMode:
            self._editModeData = None
        
        # set mode
        oldMode        = self.editMode()
        self._editMode = mode
        self.editModeChanged.emit(mode, oldMode)
        
     
    def exitEditMode(self):
        self.enterEditMode(self.NoEditMode) 

        
     
    def mousePressEvent(self, mouseEvent):
        QGraphicsScene.mousePressEvent(self, mouseEvent) # Handle selection first
        
        if self.editMode() != self.NoEditMode:
            return
        
        itemUnderMouse = self.itemAt(mouseEvent.scenePos())
        if itemUnderMouse and itemUnderMouse.isSelected():

            if mouseEvent.button() == Qt.LeftButton: 
                self.enterEditMode(self.MoveEditMode)
                
            if  mouseEvent.button() == Qt.RightButton:
                self.enterEditMode(self.RotateEditMode)
            
            if  mouseEvent.button() == Qt.MiddleButton:
                self.enterEditMode(self.scaleEditMode)
            
        
    def mouseReleaseEvent(self,  mouseEvent):
        self.exitEditMode()
        
        return QGraphicsScene.mouseReleaseEvent(self, mouseEvent)
    
    
    def mouseMoveEvent(self, mouseEvent):
        
        editMode = self.editMode()
        oldPos   = mouseEvent.lastScenePos()
        pos      = mouseEvent.scenePos()        

        # Update mousePosition first         
        self._mousePos = pos
        
        if editMode == self.scaleEditMode:
            deltaY = pos.y() - oldPos.y()
            for item in self.selectedItems():
                scale = item.scale() + (deltaY / 10)
                if scale < 0.1:    scale = 0.1
                elif scale > 10.0: scale = 10.0
                item.setScale(scale)   
 
        if editMode == self.RotateEditMode:
            deltaX = pos.x() - oldPos.x()
            for item in self.selectedItems():
                rotation = item.rotation() + int(deltaX)
                item.setRotation(rotation)   
                   
        LayeredGraphicsScene.mouseMoveEvent(self, mouseEvent)
        
                          
    def dragEnterEvent(self, event):        
        if not event.mimeData().hasText() or not self.activeLayer():
            event.ignore()
            return
        
        event.accept()
        
        path =  event.mimeData().text()
        self._editModeData = { 
                              "pos"    : event.scenePos(), 
                              "pixmap" : loader.pixmap.load(path),
                              "path"   : path
                              }
        
        self.enterEditMode(self.PixmapDropMode)
            
        
    def dragMoveEvent(self, event):
        self._editModeData["pos"] = event.scenePos()
        self.invalidate(layers=self.ForegroundLayer)
        
        
    def dropEvent(self, event):
        self.invalidate(layers=self.ForegroundLayer)
        path = self._editModeData["path"]
        x    = self._editModeData["pos"].x()
        y    = self._editModeData["pos"].y()
        self.itemCreationRequest.emit(items.newPixmapItemFromPath(path), x, y)
        self.exitEditMode()
        
        
        
    
    def dragLeaveEvent(self, event):
        self.exitEditMode()
        self.invalidate(layers=self.ForegroundLayer)
        
          
    def drawForeground(self, painter, rect):
        if self.editMode() == self.PixmapDropMode:
            pos    = self._editModeData["pos"]
            pixmap = self._editModeData["pixmap"]
            pos.setX(pos.x() - (pixmap.width()/2))
            pos.setY(pos.y() - (pixmap.height()/2))

            assert pos and pixmap
            painter.drawPixmap(pos, pixmap)
            
        QGraphicsScene.drawForeground(self, painter, rect)
        
            
        
            