'''
Created on Dec 31, 2011

@author: vitali
'''



from PySide.QtCore import Qt
from PySide.QtCore import QPointF
from PySide.QtCore import QRectF
from PySide.QtCore import QDir

from PySide.QtGui  import QGraphicsPixmapItem
from PySide.QtGui  import QGraphicsItem
from PySide.QtGui  import QTransform       

from properties import newBuiltinProperty
from item import SceneItem


class SceneRootItem(SceneItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        SceneItem.__init__(self)
        
        
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name", self, "scene"))
        self._addProperty(newBuiltinProperty("content", self, QDir.homePath())) 
        self._addProperty(newBuiltinProperty("bounds", self, QRectF(0,0,0,0))) 
        self._addProperty(newBuiltinProperty("origin", self, QPointF(0,0)) )


    def bounds(self):
        scene = self.scene()
        if scene is not None:
            return scene.sceneRect()
        else:
            return QRectF(0,0,0,0)
        
        
    def setBounds(self,rect):
        scene = self.scene()
        if scene is not None:
            scene.setSceneRect(rect)
        

        
        
class Layer(SceneItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        SceneItem.__init__(self)
    
    
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name", self,     "layer"))
        self._addProperty(newBuiltinProperty("z_order" , self, 0.0))
        self._addProperty(newBuiltinProperty("parallax", self, QPointF(100,100)))
        
        
    def _adjustParallax(self, x, y):
        pX, pY = self.value("parallax").toTuple()
        
        x -= x * (pX/100)
        y -= y * (pY/100)
        
        self.setPos(int(x),int(y))
        

        
        
class TextureItem(SceneItem, QGraphicsPixmapItem):
    
    ItemXFlipChange     = 100
    ItemXFlipHasChanged = 101
    ItemYFlipChange     = 102
    ItemYFlipHasChanged = 103
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        SceneItem.__init__(self)
        
        self.setTransformationMode(Qt.SmoothTransformation)

       
    def flipX(self, flip):
        flip    = self.itemChange(TextureItem.ItemXFlipChange, flip)
        if flip == self.xFlipped():
            return
        
        x,y   = self.transformOriginPoint().toTuple()
        xFlip = -1 if flip else 1
        yFlip = -1 if self.yFlipped() else 1 
        self.setTransform(QTransform().translate(x, y).scale(xFlip,yFlip).translate(-x, -y))
        
        self.itemChange(TextureItem.ItemXFlipHasChanged, flip)
    
    
    def flipY(self, flip):
        flip    = self.itemChange(TextureItem.ItemYFlipChange, flip)
        if flip == self.yFlipped():
            return
              
        x,y   = self.transformOriginPoint().toTuple()
        xFlip = -1 if self.xFlipped() else 1
        yFlip = -1 if flip else 1
        self.setTransform(QTransform().translate(x, y).scale(xFlip,yFlip).translate(-x, -y))
        
        self.itemChange(TextureItem.ItemYFlipHasChanged, flip)

    
    def xFlipped(self):
        return False if self.transform().m11() > 0 else True
    
    
    def yFlipped(self):
        return False if self.transform().m22() > 0 else True
    
           
    def setPixmap(self, pixmap): 
        QGraphicsPixmapItem.setPixmap(self, pixmap) 
        self.setTransformOriginPoint(self.pixmap().width()/2 , self.pixmap().height()/2)   


    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name"     , self, "item"))
        self._addProperty(newBuiltinProperty("position" , self, QPointF(0,0)), QGraphicsItem.ItemPositionChange)
        self._addProperty(newBuiltinProperty("z_order"  , self,  0.0),         QGraphicsItem.ItemZValueChange)
        self._addProperty(newBuiltinProperty("rotation" , self,  0),           QGraphicsItem.ItemRotationChange)
        self._addProperty(newBuiltinProperty("scale"    , self,  1.0),         QGraphicsItem.ItemScaleChange)
        self._addProperty(newBuiltinProperty("flip_x"   , self,  False),       TextureItem.ItemXFlipChange)
        self._addProperty(newBuiltinProperty("flip_y"   , self,  False),       TextureItem.ItemYFlipChange)
        self._addProperty(newBuiltinProperty("opacity"  , self,  1.0),         QGraphicsItem.ItemOpacityChange)
        self._addProperty(newBuiltinProperty("texture"  , self,  None))

 

    
    
    