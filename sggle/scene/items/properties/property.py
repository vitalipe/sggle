'''
Created on Dec 29, 2011

@author: vitali
'''

from validators import AcceptValidator
from validators import FloatValadator


# TODO:
#       clean up:
#                  rect and point property - provide setter, getter table
#                  use template pattern with set/get value
#                      then check for scene: if scene use custom get/set
#                      else: cache
#
#

def newCustomProperty(name, item):
    return Property(name, item, readOnly = False, builtin = False)




class Property(object):
    

    def __init__(self, name, item,  readOnly = False , builtin = True):
                
        self._name     = name
        self._item     = item 
        self._readOnly = readOnly
        self._builtin  = builtin
        
        
    def name(self):
        return self._name
    
    
    def item(self):
        return self._item
    
    
    def value(self):
        return self.item()._getValueFromCache(self.name())
    
    
    def setValue(self,value):
        self.item()._setValueInCache(self.name(), value)
            
        
    def readOnly(self):
        return self._readOnly
    
    
    def builtin(self):
        return self._builtin
    
    
    def validator(self):
        return AcceptValidator()
    
    
    def __str__(self):
        return str(self.__dict__) 
    
    
    
    
class ComponentProperty(Property):    
    
        
    def componentNames(self):
        raise NotImplementedError()


    def value(self, key = None):
        assert key is None or key in self.componentNames()
        
        if key is not None:
            return self.componentValue(key)
        else:
            return self._value()
            
    
    def setValue(self, value=None, **keys):
        assert (len(keys) == 0 and value is not None) or (len(keys) and value is None)
        assert len(keys) == 0 or set(keys).issubset(self.componentNames())

        if len(keys) > 0:
            for k,v in keys.items():
                self.setComponentValue(k, v)
        else:
            self._setValue(value)
    
    
    def validator(self, *keys):
        assert len(keys) == 0 or set(keys).issubset(self.componentNames())
   

    def _validator(self):
        return Property.validator(self)
    
    def _value(self):
        return Property.value(self)
    
    
    def _setValue(self, value):
        return Property.setValue(self, value)
    
     
    def componentValidator(self, key):
        raise NotImplementedError()
    
    
    def componentValue(self, key):
        raise NotImplementedError()
    
    
    def setComponentValue(self, key, value):
        raise NotImplementedError()
    
    
    
    
class PointProperty(ComponentProperty):
    
    
    def __init__(self, name, item,  readOnly = False , builtin = True):
        ComponentProperty.__init__(self, name, item, readOnly, builtin)
        
        self._componentKeys = ("x", "y")
        
        
    def componentNames(self):
        return self._componentKeys
    
    
    def componentValue(self, key):
        assert key in self.componentNames()
        
        if key == "x":
            return self.value().x()
        if key == "y":
            return self.value().y()
    
    
    def setComponentValue(self, key, value):
        
        v = self.value()
        
        if key == "x":  
            v.setX(value)
        if key == "y":  
            v.setY(value)
        
        self.setValue(v)
  
  
    def _validator(self): #FIXME: use Point validator
        return ComponentProperty._validator(self)
    
    
    def componentValidator(self, key):
        return FloatValadator()
  
  
  
  
class RectProperty(ComponentProperty):
    
    
    def __init__(self, name, item,  readOnly = False , builtin = True):
        ComponentProperty.__init__(self, name, item, readOnly, builtin)
        
        self._componentKeys = ("left", "top", "right", "bottom")
        
        
    def componentNames(self):
        return self._componentKeys
    
    
    def componentValue(self, key):
        assert key in self.componentNames()
        
        if key == "left":
            return self.value().left()
        if key == "top":
            return self.value().top()
        if key == "right":
            return self.value().right()
        if key == "bottom":
            return self.value().bottom()
    
    
    def setComponentValue(self, key, value):
        
        v = self.value()
        
        if key == "left":
            v.setLeft(value)
        if key == "top":
            v.setTop(value)
        if key == "right":
            v.setRight(value)
        if key == "bottom":
            v.setBottom(value)
            
        self.setValue(v)


    def componentValidator(self, key):
        return FloatValadator()
    
    
    def _validator(self): #FIXME: use Rect validator
        return ComponentProperty._validator(self)
    
    