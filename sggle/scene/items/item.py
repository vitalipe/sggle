'''
Created on Dec 31, 2011

@author: vitali
'''

from collections   import OrderedDict

from PySide.QtCore import QPointF
from PySide.QtCore import Qt

from PySide.QtGui  import QTransform       
from PySide.QtGui  import QGraphicsItem
from PySide.QtGui  import QStyle

from properties import newCustomProperty
from properties import newBuiltinProperty  
from properties.property import ComplexProperty  
    

class BaseItem(object):
  

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
        assert (value is None) != (len(kv) == 0) # xor 
        p = self.property(key)
            
        if value is not None:
            p.setValue(value)
        else:
            for k,v in kv.items():
                p.component(k).setValue(v)
    
    
    def addCustomProperty(self, key, value = None):
        property = newCustomProperty(self, key)
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
        
        # copy children 
        for child in self.childItems(): 
            child.copy().setParentItem(item) 

        return item
  
  
    def serializeProperties(self):
        properties = OrderedDict()
        for key in self._properties.keys():
            properties[key] = self.property(key).serializeValue()
        
        return properties.items()
    
    
    def notifyChildListChanges(self):
        if self.scene():
            self.scene().listOfItemsChanged.emit(self)
    
    
    def notifyPropertyChanged(self, propertyName):
        if self.scene():
            self.scene().notifyItemPropertyChanged(self, propertyName) 
    
    
    def notifyPropertyChangeRequest(self, propertyName, value):
        if self.scene():
            self.scene().notifyItemPropertyChangeRequest(self, propertyName, value)
        
             
    def setValueDirectly(self, key, value=None, **kv):
        p = self.property(key)
        if value:
            p.setValueDirectly(value)
        if kv:
            for k,v in kv.items():
                p.component(k).setValue(v)         

        
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
                property = self.property(propertyName)
                if not property.locked():
                    if isinstance(property, ComplexProperty):
                        for component in property.componentList():
                            if component.locked(): # reset
                                component.setComponentInComplexValue(newValue)          
                    self.notifyPropertyChangeRequest(propertyName, newValue)  
                     
                return  property.value() # return the old value
        
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




class SceneItem(BaseItem):
    
       
    ItemXFlipChange     = 100
    ItemXFlipHasChanged = 101
    ItemYFlipChange     = 102
    ItemYFlipHasChanged = 103
    
    
    def __init__(self):
        BaseItem.__init__(self)
                
        self._xFlipped     = False
        self._yFlipped     = False
        self._highlighted  = False

       
    def flipX(self, flip):
        flip    = self.itemChange(SceneItem.ItemXFlipChange, flip)
        if flip == self.xFlipped():
            return
        
        self._flipX()
        
        self._xFlipped = not self._xFlipped
        self.itemChange(SceneItem.ItemXFlipHasChanged, flip)
    
    
    def flipY(self, flip):
        flip    = self.itemChange(SceneItem.ItemYFlipChange, flip)
        if flip == self.yFlipped():
            return
              
        self._flipY()
        
        self._yFlipped = not self._yFlipped
        self.itemChange(SceneItem.ItemYFlipHasChanged, flip)


    def xFlipped(self):
        return self._xFlipped
        
    
    def yFlipped(self):
        return self._yFlipped
 
 
    def paint(self, painter, option, widget = None):
        selected = True if (option.state  &  QStyle.State_Selected) else False
        option.state &= (~QStyle.State_Selected)  # disable default frame                                          
        
        super(SceneItem, self).paint(painter, option, widget)
        
        # hover effect
        if self._highlighted:
            painter.save()
            painter.setOpacity(0.2)
            painter.fillRect(self.boundingRect(), Qt.red)
            painter.restore()
            
        
    def hoverEnterEvent(self, event):
        if self.flags() & self.ItemIsSelectable:
            self._highlighted = True
            self.update()   
    
    
    def hoverLeaveEvent(self, event):
        self._highlighted = False
        self.update()   
    
    
    def _flipX(self):
        x,y   = self.transformOriginPoint().toTuple()
        t     = self.transform()
        
        t.translate(x, y)
        t.setMatrix(t.m11()* (-1), t.m12(), t.m13(), 
                    t.m21(), t.m22() , t.m23(), 
                    t.m31(), t.m32(), t.m33())
        t.translate(-x, -y)
        self.setTransform(t)
        
        
    def _flipY(self):
        x,y   = self.transformOriginPoint().toTuple()
        t     = self.transform()
        
        t.translate(x, y)
        t.setMatrix(t.m11(), t.m12(), t.m13(), 
                    t.m21(), t.m22() * (-1), t.m23(), 
                    t.m31(), t.m32(), t.m33())
        t.translate(-x, -y)
        self.setTransform(t)
        
        
    def _adjustOrigin(self): # translate to center
        center = self.boundingRect().center()
        
        # New QTransform should prevent the item from sliding left, 
        # when we call this method multiple times
        self.setTransform(QTransform().translate(-1 * center.x(), -1 * center.y()))
        self.setTransformOriginPoint(center.x() , center.y())   
        
        # adjust flip
        if self.xFlipped():
            self._flipX()
            
        if self.yFlipped():
            self._flipY()

       
    def _createBuiltinProperties(self):
        self._addProperty(newBuiltinProperty("name"     , self, "item"))
        self._addProperty(newBuiltinProperty("position" , self, QPointF(0,0)), QGraphicsItem.ItemPositionChange)
        self._addProperty(newBuiltinProperty("rotation" , self,  0),           QGraphicsItem.ItemRotationChange)
        self._addProperty(newBuiltinProperty("scale"    , self,  1.0),         QGraphicsItem.ItemScaleChange)
        self._addProperty(newBuiltinProperty("flip_x"   , self,  False),       SceneItem.ItemXFlipChange)
        self._addProperty(newBuiltinProperty("flip_y"   , self,  False),       SceneItem.ItemYFlipChange)
        self._addProperty(newBuiltinProperty("opacity"  , self,  1.0),         QGraphicsItem.ItemOpacityChange)

    
