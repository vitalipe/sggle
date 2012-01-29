from PySide.QtCore   import Qt

import items
import commands


                
class IEditMode(object):
    
    
    def mousePressEvent(self, scene, mouseEvent):
        pass
    
    def mouseReleaseEvent(self,  scene, mouseEvent):
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
    
    
    def mousePressEvent(self, scene, mouseEvent):    
        
        itemUnderMouse = scene.itemAt(mouseEvent.scenePos())
        if itemUnderMouse and itemUnderMouse.isSelected():

            if mouseEvent.button() == Qt.LeftButton: 
                scene.enterEditMode(scene.MoveEditMode)
                
            elif  mouseEvent.button() == Qt.RightButton:
                scene.enterEditMode(scene.RotateEditMode)
            
            elif  mouseEvent.button() == Qt.MiddleButton:
                scene.enterEditMode(scene.scaleEditMode)
    
    
    def dragEnterEvent(self, scene, event):
        scene.enterEditMode(scene.PixmapDropMode)
        scene.PixmapDropMode.dragEnterEvent(scene, event)
        
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


    def mouseMoveEvent(self, scene, mouseEvent):
        oldPos   = mouseEvent.lastScenePos()
        pos      = mouseEvent.scenePos()
        
        deltaX = pos.x() - oldPos.x()
        for item in scene.selectedItems():
            rotation = item.rotation() + int(deltaX)
            item.setRotation(rotation)    
    
    
    def mouseReleaseEvent(self, scene, mouseEvent):
        scene.exitEditMode()
    


    
class MoveEditMode(IEditMode): # Do nothing here, movement is handled by QGraphicsScene
    
    def mouseReleaseEvent(self, scene, mouseEvent):
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

        x    = self.pos.x()
        y    = self.pos.y()
        scene.undoStack().push(commands.newAddItemCommand(scene, self.item.copy(), x, y))
        
        scene.exitEditMode()
        
        
    def drawForeground(self, scene, painter, rect):
        pos    = self.pos
        pixmap = self.item.value("texture")
        pos.setX(pos.x() - (pixmap.width()/2))
        pos.setY(pos.y() - (pixmap.height()/2))

        painter.drawPixmap(pos, pixmap)
        
            