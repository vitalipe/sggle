'''
Created on Dec 29, 2011

@author: vitali
'''

from collections import OrderedDict

from PySide.QtCore import QPointF
from PySide.QtCore import QRectF

from validators import TypeCheckValidator
from validators import FloatValadator




def newCustomProperty(name, item): # FIXME: should also pass type info
    return Property(name, item, readOnly = False, builtin = False)




class Property(object):
    

    def __init__(self, name, item, readOnly = False , builtin = True, 
                 validator = TypeCheckValidator(), value = None):
                
        self._name      = name
        self._item      = item 
        self._validator = validator
        self._readOnly  = readOnly
        self._builtin   = builtin
        self._value     = None
        
        
    def name(self):
        return self._name
    
    
    def item(self):
        return self._item
    
    
    def value(self):
        if self._item.scene():
            try:
                return self._customGetValue()
            except NotImplementedError:
                pass
            
        return self._value
    
    
    def setValue(self,value):
        item  = self.item()
        scene = item.scene()
        if scene:
            try:
                self._customSetValue(value)
                if item._directEdit:
                    item.notifyPropertyChanged(self.name())
                    
            except NotImplementedError:  # no custom setter      
                if not item._directEdit:
                    item.notifyPropertyChangeRequest(self.name(), value)
                else:
                    self._value = value
                    item.notifyPropertyChanged(self.name())
        
        else: # not in scene, always use cache
            self._value = value
        
                
    def setValueDirectly(self,value):
        self._item._directEdit = True
        self.setValue(value)
        self._item._directEdit = False
        
        
    def readOnly(self):
        return self._readOnly
    
    
    def builtin(self):
        return self._builtin
    
    
    def validator(self):
        self._syncValidator(self._validator)
        return self._validator
    
    
    def serializeValue(self):
        return self.value() 
    
    
    def deserializeValue(self, value):
                
        validator = self.validator()
        value     = validator.fixupRawValue(value)
        if validator.validateRawValue(value) != validator.Acceptable:
            return False
        
        self.setValueDirectly(value)# this is important because we don't want to generate 
                                    # tons of signals when we load from a file. 
        return True
    
    
    def _customGetValue(self):
        raise NotImplementedError()
    
    
    def _customSetValue(self, value):
        raise NotImplementedError()
    
    
    def __str__(self):
        return str(self.__dict__) 
    
    
    def _syncValidator(self,validator):
        """ use this method to update validator parameters """
        pass
    
    
 
 
class PropertyComponent(Property):
    
    def __init__(self,  parent, name, get, set, validator):
        Property.__init__(self, name, parent.item(),parent.readOnly(), parent.builtin(), validator)
        
        self._setter    = set
        self._getter    = get
        self._parent    = parent
    
    
    def value(self):
        return self._getter()
 
    
    def setValue(self,value):
        return self._setter(value)
    
    
    def _syncValidator(self,validator):
        # notify parent
        self._parent._syncValidator(validator, self.name())

        
        
        

class ComplexProperty(Property):
    
    
    def __init__(self, *args):
        Property.__init__(self, *args)
        
        self._components = OrderedDict()
        self._createComponents()
    
    
    def _createComponents(self):
        raise NotImplementedError()
    
    
    def _addNewComponenet(self, name, get, set, validator):
        self._components[name] = PropertyComponent(self, name, get, set, validator)
        
        
    def _syncValidator(self, validator, componentName=None):
        pass
    
    
    def componentList(self):
        return self._components.values()
    
    
    def component(self, name):
        return self._components.get(name)
    
    
    def serializeValue(self):
        components = {}
        for c in self.componentList():
            components[c.name()] = c.serializeValue()
            
        return components


    def deserializeValue(self, components):
        if set(components.keys()) != set(self._components.keys()):
            return False
        
        for k,v in components.items():
            if self.component(k).deserializeValue(v) == False:
                return False
        
        return True
        
    
    
    
class PointProperty(ComplexProperty):
    
    def __init__(self, name, item,  readOnly = False , builtin = True):
        ComplexProperty.__init__(self, name, item, readOnly, builtin)

    
    def _createComponents(self):
        self._addNewComponenet("x", get=self.x, set=self.setX, validator=FloatValadator())
        self._addNewComponenet("y", get=self.y, set=self.setY, validator=FloatValadator())

        
    def x(self):
        return self.value().x()
    
    
    def setX(self, value):
        v =  QPointF(self.value())
        v.setX(value)
        self.setValue(v)
    
    
    def y(self):
        return self.value().y()
    
    
    def setY(self, value):
        v =  QPointF(self.value())
        v.setY(value)
        self.setValue(v)
    


  
class RectProperty(ComplexProperty):
    
    
    def __init__(self, name, item,  readOnly = False , builtin = True):
        ComplexProperty.__init__(self, name, item, readOnly, builtin)

    
    def _createComponents(self):
        self._addNewComponenet("left"  , get=self.left  , set=self.setLeft  , validator=FloatValadator())
        self._addNewComponenet("top"   , get=self.top   , set=self.setTop   , validator=FloatValadator())
        self._addNewComponenet("right" , get=self.right , set=self.setRight , validator=FloatValadator())
        self._addNewComponenet("bottom", get=self.bottom, set=self.setBottom, validator=FloatValadator())
        
        
    def left(self):
        return self.value().left()
    
    
    def setLeft(self, value):
        v =  QRectF(self.value())
        v.setLeft(value)
        self.setValue(v)
    
    
    
    def top(self):
        return self.value().top()
        
        
    def setTop(self, value):
        v =  QRectF(self.value())
        v.setTop(value)
        self.setValue(v)
    
        
        
    def right(self):
        return self.value().right()
    
    
    def setRight(self, value):
        v =  QRectF(self.value())
        v.setRight(value)
        self.setValue(v)
    
    
    def bottom(self):
        return self.value().bottom()
    
    
    def setBottom(self, value):
        v =  QRectF(self.value())
        v.setBottom(value)
        self.setValue(v)
    
    
    
