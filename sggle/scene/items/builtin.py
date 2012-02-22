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
from item import BaseItem
from item import SceneItem


class SceneRoot(BaseItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        BaseItem.__init__(self)
        
        
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name", self, "scene"))
        self._addProperty(newBuiltinProperty("content", self, QDir.homePath())) 
        self._addProperty(newBuiltinProperty("camera", self, QPointF(0,0)) )


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
        

        
        
class Layer(BaseItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        BaseItem.__init__(self)
    
    
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name", self,     "layer"))
        self._addProperty(newBuiltinProperty("parallax", self, QPointF(100,100)))
        
        
    def _adjustParallax(self, x, y):
        pX, pY = self.value("parallax").toTuple()
        
        x -= x * (pX/100)
        y -= y * (pY/100)
        
        self.setPos(int(x),int(y))
        

        
        
class SpriteItem(SceneItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        SceneItem.__init__(self)
        
        self.setTransformationMode(Qt.SmoothTransformation)
        
   
    def setPixmap(self, pixmap): 
        QGraphicsPixmapItem.setPixmap(self, pixmap)
        self._adjustOrigin()

        
    def _createBuiltinProperties(self):
        SceneItem._createBuiltinProperties(self)
        self._addProperty(newBuiltinProperty("texture"  , self,  None))

 

    
    
    