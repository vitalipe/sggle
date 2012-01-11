'''
Created on Dec 31, 2011

@author: vitali
'''



from PySide.QtCore import Qt
from PySide.QtCore import QPointF
from PySide.QtCore import QRectF
from PySide.QtCore import QDir


from PySide.QtGui  import QGraphicsPixmapItem

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

        
        
class TextureItem(SceneItem, QGraphicsPixmapItem):
    
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        SceneItem.__init__(self)
        
        self.setTransformationMode(Qt.SmoothTransformation)

    
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name"     , self, "item"))
        self._addProperty(newBuiltinProperty("position" , self, QPointF(0,0)))
        self._addProperty(newBuiltinProperty("z_order"  , self,  0.0))
        self._addProperty(newBuiltinProperty("rotation" , self,  0))
        self._addProperty(newBuiltinProperty("scale"    , self,  1.0))
        self._addProperty(newBuiltinProperty("flip_x"   , self,  False))
        self._addProperty(newBuiltinProperty("flip_y"   , self,  False))
        self._addProperty(newBuiltinProperty("opacity"  , self,  1.0))
        self._addProperty(newBuiltinProperty("texture"  , self,  None))

        
    def setPixmap(self, pixmap): 
        QGraphicsPixmapItem.setPixmap(self, pixmap) 
        self.setTransformOriginPoint(self.pixmap().width()/2 , self.pixmap().height()/2)   


    
    
    