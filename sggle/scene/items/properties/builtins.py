'''
Created on Dec 29, 2011

@author: vitali
'''

from os.path import join    as joinPath
from os.path import relpath as relativePath
from math    import floor 

from property import Property
from property import PointProperty

from validators import TypeCheckValidator
from validators import DirPathValidator
from validators import NameValidator
from validators import FloatValadator
from validators import IntValadator

import sggle.resources as resources


def newBuiltinProperty(propertyName, item, value=None):
    factories =  {
                   "name"         : NameProperty,
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
                   "camera"       : cameraPositionProperty,
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
        Property.__init__(self, "name", item, hidden = False, builtin = True,
                          validator = NameValidator())
        

    def setValue(self, value):
        validator = self.validator()
        value = validator.fixup(value)
        Property.setValue(self, value)



class ContentRootProperty(Property):
    
    def __init__(self, item):
        Property.__init__(self, "content", item, hidden = False, builtin = True,
                          validator = DirPathValidator())
        



class PositionProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "position", item, hidden = False, builtin = True)
    
    
    def _customSetValue(self, value):
        value.setX(floor(value.x()))
        value.setY(floor(value.y()))
        
        self.item().setPos(value)
        
    
    def _customGetValue(self):
        return self.item().pos()
    
    
    
        
class ScaleProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "scale", item, hidden = True, builtin = True,
                          validator = FloatValadator(0.1, 10.0, 2, None))
    
    
    def _customSetValue(self, value):
        value = floor(value * 100) / 100.0 # limit to two decimal points
        self.item().setScale(value)
    
    
    def _customGetValue(self):
        return self.item().scale()



class RotationProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "rotation", item, hidden = False, builtin = True,
                          validator = IntValadator(0, 359, None))
    
    
    def setValue(self, value):
        Property.setValue(self, value % 360) #FIXME: remove this
    
    
    def _customSetValue(self, value): 
        value = floor(value)
        self.item().setRotation(value)
    
    
    def _customGetValue(self):
        return self.item().rotation()

        
        
        
        
class TextureProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "texture", item, hidden = True , builtin = True)
    
    
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
        PointProperty.__init__(self, "parallax", item, hidden = False, builtin = True)
        
        
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
        Property.__init__(self, "flip_x", item, hidden = False, builtin = True,
                          validator = TypeCheckValidator(bool))
    
    
    def _customSetValue(self, value):    
        self.item().flipX(value)
    
    
    def _customGetValue(self):
        return self.item().xFlipped()
    
        
        
class FlipYProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "flip_y", item, hidden = False, builtin = True,
                          validator = TypeCheckValidator(bool))
    
    
    def _customSetValue(self, value):    
        self.item().flipY(value)
    
    
    def _customGetValue(self):
        return self.item().yFlipped()
        
        
        
        
class OpacityProperty(Property):
    
        
    def __init__(self, item):
        Property.__init__(self, "opacity", item, hidden = False, builtin = True, 
                          validator = FloatValadator(0.1, 1.0, 1, None))
    
    
    def _customSetValue(self, value):
        self.item().setOpacity(value)
    
    
    def _customGetValue(self):
        return self.item().opacity()
   
            
           
class cameraPositionProperty(PointProperty):
    
        
    def __init__(self, item):
        PointProperty.__init__(self, "camera", item, hidden = False, builtin = True)
        
        
    def _syncValidator(self, validator, name=None):
        sceneRect = self.item().scene().sceneRect()
        
        if name == "x":
            minValue = sceneRect.x()
            maxValue = sceneRect.right()
            validator.setRange(minValue,maxValue)
            
        if name == "y":
            minValue = sceneRect.x()
            maxValue = sceneRect.right()
            validator.setRange(minValue,maxValue)
                
                
                
