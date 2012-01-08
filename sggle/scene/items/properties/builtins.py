'''
Created on Dec 29, 2011

@author: vitali
'''

from os.path import join    as joinPath
from os.path import relpath as relativePath

from property import Property
from property import PointProperty
from property import RectProperty

from validators import DirPathValidator
from validators import NameValidator
from validators import FloatValadator
from validators import IntValadator

import sggle.resources as resources


def newBuiltinProperty(propertyName, item):
    factories =  {
                   "name"         : NameProperty,
                   "z_order"      : ZOrderProperty,
                   "position"     : PositionProperty,
                   "scale"        : ScaleProperty,
                   "rotation"     : RotationProperty,
                   "texture"      : TextureProperty,
                   "parallax"     : ParallaxProperty,
                   "flip_x"       : FlipXProperty,
                   "flip_y"       : FlipYProperty,
                   "opacity"      : OpacityProperty,
                   "tint"         : None,
                   "content"      : ContentRootProperty,
                   "bounds"       : BoundsProperty,
                   "origin"       : OriginProperty,
                 }
                 
    factory = factories.get(propertyName)
    return factory(item) if factory else None




class NameProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "name", item, readOnly = False, builtin = True)
        
        
    def validator(self):
        return NameValidator()




class ContentRootProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "content", item, readOnly = False, builtin = True)
        
        
    def validator(self):
        return DirPathValidator()

        


class ZOrderProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "z_order", item, readOnly = False, builtin = True)


    def setValue(self, value):
        self.item().setZValue(value)

        
    def value(self):
        return self.item().zValue()
        
        
    def validator(self):
        return FloatValadator(0, 100, 2, None)

        
        
        
class PositionProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "position", item, readOnly = False, builtin = True)
    
    
    def _setValue(self, value):
        self.item().setPos(value)
        
    
    def _value(self):
        return self.item().pos()
    
    
    
        
class ScaleProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "scale", item, readOnly = False, builtin = True)
    
    
    def setValue(self, value):    
        self.item().setScale(value)
    
    
    def value(self):
        return self.item().scale()
    
    
    def validator(self):
        return FloatValadator(0.1, 10.0, 2, None)




class RotationProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "rotation", item, readOnly = False, builtin = True)
    
    
    def setValue(self, value):    
        self.item().setRotation(value % 360) #FIXME: remove this
    
    
    def value(self):
        return self.item().rotation()
        
        
    def validator(self):
        return IntValadator(0, 359, None)
        
        
        
        
class TextureProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "texture", item, readOnly = True , builtin = True)
    
    
    def setValue(self, value):
        if not isinstance(value, resources.resource.PixmapResource): 
            value = resources.loader.pixmap.load(value) #FIXME: this API is ugly!!   
             
        self.item().setPixmap(value) 
        Property.setValue(self, value) # cache


    def serializeValue(self):
        path  = self.value().path()
        scene = self._item.scene()
        
        if scene is None:
            return path
        
        contentRoot = scene.rootItem().value("content")
        return ":" + relativePath(path, contentRoot)


    def deserializeValue(self, value):
        value = value[1:]
        contentRoot = self._item.scene().rootItem().value("content")
        self.setValue(joinPath(contentRoot, value))
        
        
    
class ParallaxProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "parallax", item, readOnly = False, builtin = True)
        
        
    def componentValidator(self, key):
        return FloatValadator(0.0, 100.0, 1, None)
        
    
    

        
class FlipXProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "flip_x", item, readOnly = False, builtin = True)
    
    
    def setValue(self, value):    
        self.item().flipX(value)
    
    
    def value(self):
        return self.item().xFlipped()
    
        
        
class FlipYProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "flip_y", item, readOnly = False, builtin = True)
    
    
    def setValue(self, value):    
        self.item().flipY(value)
    
    
    def value(self):
        return self.item().yFlipped()
        
        
        
        
class OpacityProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "opacity", item, readOnly = False, builtin = True)
    
    
    def setValue(self, value):
        self.item().setOpacity(value)
    
    
    def value(self):
        return self.item().opacity()
    
    
    def validator(self):
        return FloatValadator(0.1, 1.0, 1, None)
           
            
           
class OriginProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "origin", item, readOnly = False, builtin = True)
        
        
    def min(self, key=None):
        return 0
    
    def max(self, key=None):
        return 42
    
    
class BoundsProperty(RectProperty):
    
        
    def __init__(self, item):
        RectProperty.__init__(self, "bounds", item, readOnly = False, builtin = True)
        