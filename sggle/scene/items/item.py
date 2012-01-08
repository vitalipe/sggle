'''
Created on Dec 31, 2011

@author: vitali
'''


from collections   import OrderedDict

from PySide.QtGui  import QTransform       
from PySide.QtGui  import QGraphicsItem

import properties



class SceneItem(object):
  
    ItemXFlipChange     = 100
    ItemXFlipHasChanged = 101
    ItemYFlipChange     = 102
    ItemYFlipHasChanged = 103
    
    itemChangeToPropertyMap =    {        
                                     QGraphicsItem.ItemPositionChange     : "position", 
                                     QGraphicsItem.ItemRotationChange     : "rotation",
                                     QGraphicsItem.ItemScaleChange        : "scale",
                                     QGraphicsItem.ItemZValueChange       : "z_order",
                                     QGraphicsItem.ItemOpacityChange      : "opacity",
                                     ItemXFlipChange                      : "flip_x",
                                     ItemYFlipChange                      : "flip_y",                                    
                                  }
    
    itemHasChangedToPropertyMap = {        
                                     
                                     QGraphicsItem.ItemPositionHasChanged : "position",
                                     QGraphicsItem.ItemRotationHasChanged : "rotation",
                                     QGraphicsItem.ItemScaleHasChanged    : "scale",
                                     QGraphicsItem.ItemZValueHasChanged   : "z_order",
                                     QGraphicsItem.ItemOpacityHasChanged  : "opacity",
                                     ItemXFlipHasChanged                  : "flip_y",
                                     ItemYFlipHasChanged                  : "flip_y",            
                
                                  }
    
    
    def __init__(self):
        object.__init__(self)
        
        self._properties = OrderedDict()
        self._cache      = {}
        self._directEdit = False
        
        self._createBuiltinProperties()
        
         
    def _createBuiltinProperties(self):
        raise NotImplementedError()
           
           
    def typeName(self):
        return self.__class__.__name__
   
   
    def propertyIndex(self, property):
        key = property.name()
        return self._properties.keys().index(key)
   
         
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
        self.property(key).setValue(value, **kv)
    
    
    def addCustomProperty(self, key, value = None):
        property = properties.newCustomProperty(key)
        self._addProperty(property)
    
    
    def hasProperty(self, key):
        return True if self.property(key) else False
    
    
    def removeCustomProperty(self, key):
        self._properties.pop(key)
        self._cache.pop(key)
        
        
    def propertyCount(self):
        return len(self._properties.keys())
    
    
    def copy(self):
        raise NotImplementedError()
  
  
    def serializeProperties(self):
        properties = OrderedDict()
        for key in self._properties.keys():
            properties[key] = self.property(key).serializeValue()
        
        return properties.items()

 
    def deserializeProperties(self, properties):
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
             
 
    def enableDirectEdit(self):
        assert self._directEdit is False
        self._directEdit = True
        
    
    def disableDirectEdit(self):
        assert self._directEdit is True
        self._directEdit = False
        
        
    def itemChange(self, changeType, newValue):
        
        # property has changed
        propertyName = SceneItem.itemHasChangedToPropertyMap.get(changeType)        
        if propertyName is not None:
            self._setValueInCache(propertyName, newValue) # sync cache and notify scene 
            
        # child list changed  
        elif (changeType == QGraphicsItem.ItemChildAddedChange or 
              changeType == QGraphicsItem.ItemChildRemovedChange):
            self.notifyChildListChanges()
            
        # Only request property change
        elif (not self._directEdit):
            propertyName = SceneItem.itemChangeToPropertyMap.get(changeType)        
            if propertyName is not None: # change we care about
                self.notifyPropertyChangeRequest(propertyName, newValue)   
                return  self.value(propertyName)
        
        # change it
        return newValue
    
    
    def flipX(self, flip):
        flip    = self.itemChange(SceneItem.ItemXFlipChange, flip)
        if flip == self.xFlipped():
            return
        
        x,y   = self.transformOriginPoint().toTuple()
        xFlip = -1 if flip else 1
        yFlip = -1 if self.yFlipped() else 1 
        self.setTransform(QTransform().translate(x, y).scale(xFlip,yFlip).translate(-x, -y))
        
        self.itemChange(SceneItem.ItemXFlipHasChanged, flip)
    
    
    def flipY(self, flip):
        flip    = self.itemChange(SceneItem.ItemYFlipChange, flip)
        if flip == self.yFlipped():
            return
              
        x,y   = self.transformOriginPoint().toTuple()
        xFlip = -1 if self.xFlipped() else 1
        yFlip = -1 if flip else 1
        self.setTransform(QTransform().translate(x, y).scale(xFlip,yFlip).translate(-x, -y))
        
        self.itemChange(SceneItem.ItemYFlipHasChanged, flip)

    
    def xFlipped(self):
        return False if self.transform().m11() > 0 else True
    
    
    def yFlipped(self):
        return False if self.transform().m22() > 0 else True
    
    
    def _addProperty(self, property, value = None): #FIXME default value not working
        key = property.name()
        self._properties[key] = property
        self._cache[key]      = value
    
                
    def _setValueInCache(self, key, value):
        self._cache[key] = value
        self.notifyPropertyChanged(key) 

        
        
    def _getValueFromCache(self,key):
        return self._cache[key]
        
    