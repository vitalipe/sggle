import math


from PySide.QtCore   import Qt
from PySide.QtCore   import QPointF
from PySide.QtGui    import QVector2D
from PySide.QtGui    import QPen

import items
import commands


                
class IEditMode(object):
    
    
    def mousePressEvent(self, scene, mouseEvent):
        pass
    
    def mouseReleaseEvent(self,  scene, mouseEvent):
        pass
    
    def mouseDoubleClickEvent(self, scene, mouseEvent):
        pass
    
    def mouseMoveEvent(self, scene, mouseEvent):
        pass
    
    def dragEnterEvent(self, scene, event):
        event.ignore()
    
    def dragMoveEvent(self, scene, event):
        pass
    
    def dropEvent(self, scene, event):
        pass
    
    def dragLeaveEvent(self, scene, event):
        pass
    
    def drawForeground(self, scene, painter, rect):
        pass
        
        
    
        
class NoEditMode(IEditMode):
    
    def mouseDoubleClickEvent(self, scene, mouseEvent):
        if  mouseEvent.modifiers() & Qt.ControlModifier:
            return # do nothing when ctrl is pressed
        else:
            scene.clearSelection()
            itemUnderMouse = self.activeItemAt(scene, mouseEvent.scenePos())
            if itemUnderMouse:
                itemUnderMouse.setSelected(True)
             

    def mousePressEvent(self, scene, mouseEvent):    
        self._handleSelection(mouseEvent, scene)
        self._handleEditModeSwitch(mouseEvent, scene)
    
    
    def dragEnterEvent(self, scene, event):
        scene.enterEditMode(scene.PixmapDropMode)
        scene.PixmapDropMode.dragEnterEvent(scene, event)
    
        
    def activeItemAt(self, scene, pos):
        item = scene.itemAt(pos)        
        return item if (item and item.flags() & item.ItemIsSelectable) else None


    def _handleSelection(self, mouseEvent, scene):
        itemUnderMouse      = self.activeItemAt(scene, mouseEvent.scenePos())
        insideSelectionRect = scene.selectionRect().contains(mouseEvent.scenePos())
        controlMode         = (mouseEvent.modifiers() & Qt.ControlModifier)                               
        
        if mouseEvent.button() == Qt.LeftButton:
            if controlMode:
                if itemUnderMouse:
                    itemUnderMouse.setSelected(not itemUnderMouse.isSelected())
            else: # simple left click
                if not insideSelectionRect:
                    scene.clearSelection()
                if (itemUnderMouse and not itemUnderMouse.isSelected()):
                    scene.clearSelection()
                    itemUnderMouse.setSelected(True) 

        # on any mouse button click
        if itemUnderMouse and itemUnderMouse.isSelected(): 
                    scene.setSelectionMaster(itemUnderMouse)     


    def _handleEditModeSwitch(self, mouseEvent, scene):
        itemUnderMouse      = self.activeItemAt(scene, mouseEvent.scenePos())
        insideSelectionRect = scene.selectionRect().contains(mouseEvent.scenePos())
        controlMode         = (mouseEvent.modifiers() & Qt.ControlModifier)                               
        
        if len(scene.selectedItems()) > 0 and not controlMode:

            if mouseEvent.button() == Qt.LeftButton:
                if insideSelectionRect: 
                    scene.enterEditMode(scene.MoveEditMode)
                    scene.editMode().mousePressEvent(scene, mouseEvent)
                
            elif  mouseEvent.button() == Qt.RightButton:
                scene.enterEditMode(scene.RotateEditMode)
                scene.editMode().mousePressEvent(scene, mouseEvent)
            
            elif  mouseEvent.button() == Qt.MiddleButton:
                scene.enterEditMode(scene.scaleEditMode)
                scene.editMode().mousePressEvent(scene, mouseEvent)


    def __nonzero__(self): # allows me to do: if scene.editMode() ...
        return False
    
    
    
    
class ScaleEditMode(IEditMode):
    
    
    def mouseMoveEvent(self, scene, mouseEvent):
        oldPos   = mouseEvent.lastScenePos()
        pos      = mouseEvent.scenePos()
        
        deltaY = pos.y() - oldPos.y()
        for item in scene.selectedItems():
            scale = item.scale() + (deltaY / 10)
            if scale < 0.1:    
                scale = 0.1
            elif scale > 10.0: 
                scale = 10.0
            item.setScale(scale)     
    
    
    def mouseReleaseEvent(self, scene, mouseEvent):
        scene.exitEditMode()
        
    
    
        
class RotateEditMode(IEditMode):

    def __init__(self):
        IEditMode.__init__(self)

        self._origin = None
        
        
    def mousePressEvent(self, scene, mouseEvent):
        self._origin = scene.selectionMaster().pos()
        
        
    def mouseMoveEvent(self, scene, mouseEvent):
        origin = self._origin
        pos    = convertPositionDeltaToVector(origin, mouseEvent.scenePos())
        oldPos = convertPositionDeltaToVector(origin, mouseEvent.lastScenePos())
        
        angleDelta = (math.atan2(pos.y(), pos.x()) - math.atan2(oldPos.y(), oldPos.x())) 
        angleDelta =  int(angleDelta * (180 / math.pi)) 

        for item in scene.selectedItems():
            if item.xFlipped() != item.yFlipped(): # xor
                item.setRotation(item.rotation() -  angleDelta)
            else:
                item.setRotation(item.rotation() +  angleDelta)


    def mouseReleaseEvent(self, scene, mouseEvent):
        scene.invalidate(layers=scene.ForegroundLayer)
        scene.exitEditMode()
    
    
    def drawForeground(self, scene, painter, rect):
        origin   = self._origin
        painter.drawLine(origin, scene.mousePosition())
        
        # draw 2 circled points (mouse position and origin)
        scaleFactor = painter.transform().m11() # scale to match zoom 
        x,y         = scene.mousePosition().toTuple()
        width       = 8  / scaleFactor
        pen         = QPen()
        
        pen.setColor(Qt.black)
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidthF(width)        
        painter.setPen(pen)

        painter.drawPoint(x,y)
        painter.drawPoint(origin)
    
    
    
    
class MoveEditMode(IEditMode): 
    
    def mousePressEvent(self, scene, mouseEvent):
        scene.views()[0].setCursor(Qt.DragMoveCursor)
    
    
    def mouseMoveEvent(self, scene, mouseEvent):
        posDelta = mouseEvent.scenePos() - mouseEvent.lastScenePos()
  
        for item in scene.selectedItems():
            item.setPos(item.pos() + posDelta)
        
    
    def mouseReleaseEvent(self, scene, mouseEvent):
        if scene.isSnap2Grid():
            snap2Grid(scene.selectedItems(), scene.gridSize())
        
        scene.views()[0].setCursor(Qt.ArrowCursor)
        scene.exitEditMode()




class PixmapDropMode(IEditMode):
    
    def __init__(self):
        IEditMode.__init__(self)
        
        self.pos    = None
        self.item   = None
    
    
    def dragEnterEvent(self, scene, event):
        if not event.mimeData().hasText() or not scene.activeLayer():
            event.ignore()
            scene.exitEditMode()
            return
        else:
            event.accept()
            
            path =  event.mimeData().text()
            
            self.pos     = event.scenePos()
            self.item  = items.newPixmapItemFromPath(path)
    
    
    def dragLeaveEvent(self, scene, event):
        scene.exitEditMode()
        scene.invalidate(layers=scene.ForegroundLayer)
    
            
    def dragMoveEvent(self, scene, event):
        self.pos = event.scenePos()
        scene.invalidate(layers=scene.ForegroundLayer)
    
        
    def dropEvent(self, scene, event):
        scene.invalidate(layers=scene.ForegroundLayer)

        xy           = event.scenePos()
        item         = self.item.copy()
        ctrlModifier = event.modifiers() & Qt.ControlModifier

        if not ctrlModifier:
            scene.clearSelection()
            
        scene.undoStack().push(commands.newAddItemCommand(scene, item, xy, select=True))
        
        if scene.isSnap2Grid():
            snap2Grid((item,), scene.gridSize())
        
        scene.exitEditMode()
        
        
    def drawForeground(self, scene, painter, rect):
        pos    = self.pos
        pixmap = self.item.value("texture")
        pos.setX(pos.x() - (pixmap.width()/2))
        pos.setY(pos.y() - (pixmap.height()/2))

        painter.drawPixmap(pos, pixmap)
        
        
        
        
def convertPositionDeltaToVector(origin, pos):
    return QVector2D(pos - origin)
            
        
def snap2Grid(items, gridSize):
    size = int(gridSize)
    
    for item in items:
        x,y     = item.pos().toTuple()
        x, y    = int(x), int(y)
        
        x = size * ((abs(x)+(size/2)) / size) * (-1 if x < 0 else 1)
        y = size * ((abs(y)+(size/2)) / size) * (-1 if y < 0 else 1)
        
        item.setX(x)
        item.setY(y)


