'''
Created on Dec 30, 2011

@author: vitali
'''

from math import floor
from math import ceil

from PySide.QtCore import Signal
from PySide.QtCore import Qt

from PySide.QtCore  import QLine
from PySide.QtCore  import QRectF
from PySide.QtCore  import QPointF
from PySide.QtGui  import QPen
from PySide.QtGui  import QColor
from PySide.QtGui  import QGraphicsScene 
from PySide.QtGui  import QGraphicsItem
from PySide.QtGui  import QTransform


import items.builtin
import commands

from sggle.resources import loader
from editmodes       import  *


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
        self._selectionRect   = QRectF()
        
        #FIXME: use QSettings
        self._bgColor   = QColor(83,113,121)
        self._showGrid  = True
        self._gridSize  = 64
        self._gridColor = QColor(96, 125,  133)
        
        QGraphicsScene.addItem(self, self._rootItem)
        self.selectionChanged.connect(self._updateSelectionMaster)
        self.selectionChanged.connect(self._updateSelectionRect)
        self.sceneRectChanged.connect(lambda r: self._buildGridLines(r))
    
            
    def isShowGrid(self):
        return self._showGrid
    
    
    def setShowGrid(self, show):
        self._showGrid = show
        self.invalidate(layers=self.BackgroundLayer)
        
            
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
            
    
    def selectionOrigin(self):
        return self._selectionOrigin
    
    
    def selectionRect(self):
        return self._selectionRect
            
            
    def drawForeground(self, painter, rect):
        if not self.selectionRect().isNull():        
            self._drawSelectionFrame(painter)
      
        
        # << Helper methods >> #

    def _updateSelectionRect(self):
        if len(self.selectedItems()) == 0: # clear selection rect
            self._selectionRect = QRectF() 
            self.invalidate(layers=self.ForegroundLayer)
            return 
        
        items = self.selectedItems()
        rect  = self.selectedItems()[0].sceneBoundingRect()
        
        #FIXME: very naive approach... later I should probably
        #       rewrite this, and make use of the BSP Tree... 
        for i in self.selectedItems():  
            boundingRect = i.sceneBoundingRect()
            
            top    = boundingRect.top()
            bottom = boundingRect.bottom()
            left   = boundingRect.left()
            right  = boundingRect.right()
            
            if top < rect.top():
                rect.setTop(top)
            if bottom > rect.bottom():
                rect.setBottom(bottom)
            if left < rect.left():
                rect.setLeft(left)
            if right > rect.right():
                rect.setRight(right)
                
        self._selectionRect = rect
        self.invalidate(layers=self.ForegroundLayer)
        
        
    def _drawSelectionFrame(self, painter):
        selectionRect = self._selectionRect        
        scaleFactor   = painter.transform().m11() # scale to match zoom 
        
        # draw selection frame
        framePen  = QPen()
        framePen.setWidthF(1 / scaleFactor)
        framePen.setColor(Qt.black)
        
        painter.setPen(framePen)
        painter.drawRect(selectionRect)
        
        # draw corners
        pen = QPen()
        pen.setColor(Qt.black)
        pen.setCapStyle(Qt.SquareCap)
        pen.setWidthF(6.0 / scaleFactor)
        
        painter.setPen(pen)    
        painter.drawPoint(selectionRect.topRight())
        painter.drawPoint(selectionRect.topLeft())
        painter.drawPoint(selectionRect.bottomLeft())
        painter.drawPoint(selectionRect.bottomRight())
        
        
    def _drawGrid(self, painter, rect):
        color    = self._gridColor
        color2   = QColor(color.red()+20,color.green()+20, color.blue()+20)
        color4   = QColor(color2.red()+20,color2.green()+20, color2.blue()+20)
        
        painter.setPen(QPen(color, 0.0)) 
        painter.drawLines(self._gridLines)
        
        painter.setPen(QPen(color2, 0.0)) 
        for i, ln in enumerate(self._gridLines):
            if i % 2 == 0:
                painter.drawLine(ln)
        
        painter.setPen(QPen(color4, 0.0)) 
        for i, ln in enumerate(self._gridLines):
            if i % 4 == 0:
                painter.drawLine(ln)


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
        item.setFlag(QGraphicsItem.ItemIsSelectable         , True)
        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges , True)
    
    
    def _deactivateItem(self, item):
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
    NoEditMode      = NoEditMode()
    MoveEditMode    = MoveEditMode()
    RotateEditMode  = RotateEditMode()
    scaleEditMode   = ScaleEditMode()
    PixmapDropMode  = PixmapDropMode()
    
    RectDrawMode    = None
    PathDrawMode    = None
    ElipseDrawMod   = None
    
       
    itemPropertyWasChanged     = Signal(object, str)
    editModeChanged            = Signal(IEditMode, IEditMode) # @param new @param old  
    
        
    def __init__(self, undoStack):
        LayeredGraphicsScene.__init__(self)
        
        self._editMode         = EditableScene.NoEditMode
        self._editModeCmdBatch = None
        self._mousePosition    = QPointF()
        self._undoStack        = undoStack
        
        self.itemPropertyWasChanged.connect(lambda i,p: self._updateSelectionRect() if
                                            p in ["position", "rotation", "scale"] else None)
        
        
    def mousePosition(self):
        return self._mousePosition
   
   
    def editMode(self):
        return self._editMode
    
    
    def enterEditMode(self, mode):
        assert self.editMode() == self.NoEditMode or mode == self.NoEditMode
        
        batch = self._editModeCmdBatch
        if batch is not None and batch.childCount() > 0:
                self._undoStack.push(self._editModeCmdBatch)
        
        # clear data
        if mode == self.NoEditMode:
            self._editModeData     = None
            self._editModeCmdBatch = None
        else:
            self._editModeCmdBatch = commands.newCommandBatch()
        
        # set mode
        oldMode        = self.editMode()
        self._editMode = mode
        self.editModeChanged.emit(mode, oldMode)
        
     
    def exitEditMode(self):
        self.enterEditMode(self.NoEditMode) 

        
    def mousePressEvent(self, mouseEvent):
        self.editMode().mousePressEvent(self, mouseEvent)

            
    def mouseReleaseEvent(self,  mouseEvent):
        self.editMode().mouseReleaseEvent(self, mouseEvent)        

    
    
    def mouseDoubleClickEvent(self, mouseEvent):
        self.editMode().mouseDoubleClickEvent(self, mouseEvent)
    
    
    def mouseMoveEvent(self, mouseEvent):
        self._mousePosition = mouseEvent.scenePos()
        
        self.editMode().mouseMoveEvent(self, mouseEvent)
        return LayeredGraphicsScene.mouseMoveEvent(self, mouseEvent)
        
                          
    def dragEnterEvent(self, event):
            self.editMode().dragEnterEvent(self, event)
            
        
    def dragMoveEvent(self, event):
        self.editMode().dragMoveEvent(self, event)
        
        
    def dropEvent(self, event):
        self.editMode().dropEvent(self, event)
        
    
    def dragLeaveEvent(self, event):
        self.editMode().dragLeaveEvent(self, event)
    
          
    def drawForeground(self, painter, rect):
        self.editMode().drawForeground(self, painter, rect)
        super(EditableScene, self).drawForeground(painter, rect)
        
        
    def notifyItemPropertyChangeRequest(self, item, propertyName, value):
        batch = self._editModeCmdBatch
        cmd = commands.newEditItemPropertyCommand(item, propertyName, value, batch)
        
        if batch is not None:
            cmd.redo()
        else:
            self._undoStack.push(cmd)
            
            
    def undoStack(self):
        return self._undoStack
    
    def adjustParallax(self, center):
        if self.editMode():
            return
        LayeredGraphicsScene.adjustParallax(self, center)

            
            
