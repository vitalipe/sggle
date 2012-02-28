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
        
    def __init__(self, name, item, hidden = False , builtin = True, 
                 validator = TypeCheckValidator(), value = None):
                
        self._name      = name
        self._item      = item 
        self._validator = validator
        self._hidden    = hidden
        self._builtin   = builtin
        self._value     = None
        self._locked    = False
        
        
    def name(self):
        return self._name
    
    
    def item(self):
        return self._item
    
    
    def value(self):
        if self._item.scene():
            return self._customGetValue()
            
        return self._value
    
    
    def setValue(self,value):
        item  = self.item()
        scene = item.scene()
        if scene:
            self._customSetValue(value)
            if item._directEdit:
                item.notifyPropertyChanged(self.name())
        
        else: # not in scene, always use cache
            self._value = value
        
                
    def setValueDirectly(self,value):
        self._item._directEdit = True
        self.setValue(value)
        self._item._directEdit = False
        
        
    def hidden(self):
        return self._hidden
    
    
    def locked(self):
        return self._locked
    
        
    def setLocked(self, locked):
        self._locked = locked
        
        
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
        return self._value
    
    
    def _customSetValue(self, value):
        item = self.item()
        
        if item._directEdit:
            self._value = value
        else:
            item.notifyPropertyChangeRequest(self.name(), value)
    
    
    def __str__(self):
        return str(self.__dict__) 
    
    
    def _syncValidator(self,validator):
        """ use this method to update validator parameters """
        pass
    
    
 
 
class PropertyComponent(Property):
    
    def __init__(self,  parent, name, get, set, validator):
        Property.__init__(self, name, parent.item(),parent.hidden(), parent.builtin(), validator)
        
        self._setter    = set
        self._getter    = get
        self._parent    = parent
    
    
    def value(self):
        return self._getter(self._parent.value())


    def setValue(self, componentValue):
        value = self._parent.value()
        self._setter(value, componentValue)
        self._parent.setValue(value)


    def setComponentInComplexValue(self, complexValue):
        self._setter(complexValue, self.value())
        return complexValue

       
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
        
        
    def locked(self):
        for component in self.componentList():
            if component.locked() == False:
                return False
        return True
            
            
    def setLocked(self, locked):
        super(ComplexProperty,self).setLocked(locked)
        for component in self.componentList():
            component.setLocked(locked)

        
    
class PointProperty(ComplexProperty):
    
    def __init__(self, name, item,  hidden = False , builtin = True):
        ComplexProperty.__init__(self, name, item, hidden, builtin)

    
    def _createComponents(self):
        self._addNewComponenet("x", get=(lambda p: QPointF.x(p)),
                                    set=(lambda p,c: QPointF.setX(p, c)),
                                    validator=FloatValadator())
        self._addNewComponenet("y", get=(lambda p: QPointF.y(p)),
                                    set=(lambda p,c: QPointF.setY(p, c)),
                                    validator=FloatValadator())


