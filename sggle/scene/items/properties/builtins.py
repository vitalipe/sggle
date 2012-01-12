'''
Created on Dec 29, 2011

@author: vitali
'''

from os.path import join    as joinPath
from os.path import relpath as relativePath

from property import Property
from property import PointProperty
from property import RectProperty

from validators import TypeCheckValidator
from validators import DirPathValidator
from validators import NameValidator
from validators import FloatValadator
from validators import IntValadator

import sggle.resources as resources


def newBuiltinProperty(propertyName, item, value=None):
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
    if factory is None:
        return None
    
    p = factory(item)
    if value is not None:
        p.setValue(value)
    return p



class NameProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "name", item, readOnly = False, builtin = True,
                          validator = NameValidator())
        

    def setValue(self, value):
        validator = self.validator()
        value = validator.fixup(value)
        Property.setValue(self, value)



class ContentRootProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "content", item, readOnly = False, builtin = True,
                          validator = DirPathValidator())
        


class ZOrderProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "z_order", item, readOnly = False, builtin = True,
                          validator = FloatValadator(0, 100, 2, None))


    def _customSetValue(self, value):
        self.item().setZValue(value)

        
    def _customGetValue(self):
        return self.item().zValue()
        

        
        
        
class PositionProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "position", item, readOnly = False, builtin = True)
    
    
    def _customSetValue(self, value):
        self.item().setPos(value)
        
    
    def _customGetValue(self):
        return self.item().pos()
    
    
    
        
class ScaleProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "scale", item, readOnly = False, builtin = True,
                          validator = FloatValadator(0.1, 10.0, 2, None))
    
    
    def _customSetValue(self, value):    
        self.item().setScale(value)
    
    
    def _customGetValue(self):
        return self.item().scale()



class RotationProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "rotation", item, readOnly = False, builtin = True,
                          validator = IntValadator(0, 359, None))
    
    
    def setValue(self, value):
        Property.setValue(self, value % 360) #FIXME: remove this
    
    
    def _customSetValue(self, value):    
        self.item().setRotation(value)
    
    
    def _customGetValue(self):
        return self.item().rotation()

        
        
        
        
class TextureProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "texture", item, readOnly = True , builtin = True)
    
    
    def setValue(self, value):
        if not isinstance(value, resources.resource.PixmapResource): 
            value   = resources.loader.pixmap.load(value) #FIXME: this API is ugly!!   
        self._value = value     
        Property.setValue(self, value) 


    def _customSetValue(self, value):
        self.item().setPixmap(value) 


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
        self.setValueDirectly(joinPath(contentRoot, value))
        
        
    
class ParallaxProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "parallax", item, readOnly = False, builtin = True)
        
        
    def _syncValidator(self, validator, key=None):
        if key is not None:
            validator.setRange(0.0, 100.0, 1)
        
        
    def _customSetValue(self, value):
        PointProperty._customSetValue(self, value)
        views = self.item().scene().views()
        if len(views) == 0:
            return
        
        x,y = views[0].center().toTuple()
        self.item()._adjustParallax(x,y)
        
            
    

        
class FlipXProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "flip_x", item, readOnly = False, builtin = True,
                          validator = TypeCheckValidator(bool))
    
    
    def _customSetValue(self, value):    
        self.item().flipX(value)
    
    
    def _customGetValue(self):
        return self.item().xFlipped()
    
        
        
class FlipYProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "flip_y", item, readOnly = False, builtin = True,
                          validator = TypeCheckValidator(bool))
    
    
    def _customSetValue(self, value):    
        self.item().flipY(value)
    
    
    def _customGetValue(self):
        return self.item().yFlipped()
        
        
        
        
class OpacityProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "opacity", item, readOnly = False, builtin = True, 
                          validator = FloatValadator(0.1, 1.0, 1, None))
    
    
    def _customSetValue(self, value):
        self.item().setOpacity(value)
    
    
    def _customGetValue(self):
        return self.item().opacity()
   
            
           
class OriginProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "origin", item, readOnly = False, builtin = True)
        
        
    def _syncValidator(self, validator, name=None):
        pass #FIXME:
    
    
class BoundsProperty(RectProperty):
    
        
    def __init__(self, item):
        RectProperty.__init__(self, "bounds", item, readOnly = False, builtin = True)
        