'''
Created on Dec 31, 2011

@author: vitali
'''


from collections   import OrderedDict

from PySide.QtGui  import QTransform       
from PySide.QtGui  import QGraphicsItem

import properties



    
 
    
    


class SceneItem(object):
  

    def __init__(self):
        object.__init__(self)
        
        self._properties              = OrderedDict()
        self._itemChangeToPropertyMap = {}
        self._directEdit              = False
        
        self._createBuiltinProperties()
        
         
    def _createBuiltinProperties(self):
        raise NotImplementedError()
    
    
    def typeName(self):
        return self.__class__.__name__
   
   
    def propertyIndex(self, propertyName):
        return self._properties.keys().index(propertyName)
   
         
    def property(self, key):
        if isinstance(key, int):
            return self.property(self._properties.keys()[key]) 
        return self._properties.get(key)
   
    
    def properties(self):
        properties = OrderedDict()
        for key in self._properties.keys():
            properties[key] = self.value(key)
        
        return properties.items()
    
    
    def value(self, key):
        return  self.property(key).value()
    
    
    def setValue(self,key,value=None, **kv):
        assert (value is None) != (len(kv) == 0) # value xor kv
        p = self.property(key)
            
        if value is not None:
            p.setValue(value)
        else:
            for k,v in kv.items():
                p.component(k).setValue(v)
    
    
    def addCustomProperty(self, key, value = None):
        property = properties.newCustomProperty(self, key)
        self._addProperty(property)
    
    
    def hasProperty(self, key):
        return True if self.property(key) else False
    
    
    def removeCustomProperty(self, key):
        self._properties.pop(key)
        self._cache.pop(key)
        
        
    def propertyCount(self):
        return len(self._properties.keys())
    
    
    def copy(self):
        item = type(self)()
        for key,value in self.properties():
            if not item.hasProperty(key): # assume custom
                item.addCustomProperty(key)
            item.setValue(key, value)

        return item
  
  
    def serializeProperties(self): # FIXME: remove
        properties = OrderedDict()
        for key in self._properties.keys():
            properties[key] = self.property(key).serializeValue()
        
        return properties.items()

 
    def deserializeProperties(self, properties): # FIXME: remove
        for k,v in properties:
            self.value(k).deserializeValue(v)
    
    
    def notifyChildListChanges(self):
        if self.scene():
            self.scene().listOfItemsChanged.emit(self)
    
    
    def notifyPropertyChanged(self, property):
        if self.scene():
            self.scene().itemPropertyWasChanged.emit(self, property) 
    
    
    def notifyPropertyChangeRequest(self, property, value):
        if self.scene():
            self.scene().itemPropertyChangeRequest.emit(self, property, value)
        
             
    def setValueDirectly(self, key, value=None, **kv):
        self._directEdit = True
        self.setValue(key, value, **kv)
        self._directEdit = False
        
        
    def itemChange(self, changeType, newValue):
        
        if changeType == QGraphicsItem.ItemSceneChange:
            if self.scene() is not None:
                self._syncToCache()
            return newValue
        
        if changeType == QGraphicsItem.ItemSceneHasChanged:
            if self.scene() is not None:
                self._syncFromCache()
            return newValue
        
        # child list changed  
        elif (changeType == QGraphicsItem.ItemChildAddedChange or 
              changeType == QGraphicsItem.ItemChildRemovedChange):
            self.notifyChildListChanges()
        
        elif changeType == QGraphicsItem.ItemZValueHasChanged:
            p = self.parentItem()
            if p:
                p.notifyChildListChanges() 
            
        # send request 
        elif (not self._directEdit):
            propertyName = self._propertyFromCahngeTypeLookup(changeType)      
            if propertyName is not None: # change we care about
                self.notifyPropertyChangeRequest(propertyName, newValue)   
                return  self.value(propertyName)
        
        # apply change directly
        return newValue
    
              
    def _registerPropertyUpdate(self, propertyName, changeType):
        self._itemChangeToPropertyMap[changeType] = propertyName
    
    
    def _propertyFromCahngeTypeLookup(self,changeType):
        return self._itemChangeToPropertyMap.get(changeType)
 
 
    def _addProperty(self, property, changeTypeId=None):
        key = property.name()
        self._properties[key] = property
        if changeTypeId is not None:
            self._registerPropertyUpdate(key, changeTypeId)
    
        
    def _syncToCache(self):
        for p in self._properties.values():
            p._value = p.value()
        
        
    def _syncFromCache(self):
        for p in self._properties.values():
            if p._value is not None:
                p.setValueDirectly(p._value)
