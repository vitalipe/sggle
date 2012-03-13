'''
Created on Dec 29, 2011

@author: vitali
'''

from .. interfaces import INodeAdapter
from .. interfaces import INodeTreeBuilder
from .. error      import ParseError


import sggle.scene.items  as items 
import sggle.scene        as scene




class ItemNodeAdapter(INodeAdapter):
    
    def __init__(self, item):
        INodeAdapter.__init__(self)
        
        self._item = item
                
        
    def typeName(self):
        return self._item.typeName()
    
    
    def properties(self):
        return self._item.serializeProperties()
    
    
    def childItems(self):
        return [ ItemNodeAdapter(child) for child in self._item.childItems() ]

    


class SceneTreeBuilder(INodeTreeBuilder):
    
    def __init__(self):

        self._scene  = None
        self._stack  = []
        
        
    def _current(self):
        return self._stack[-1] if self._stack else None

    
    def startNode(self, typeName):        
        if not self._scene:
            self._scene = scene.newEmptyGraphicsScene()
            item        = self._scene.rootItem()
        
        else:    
            item = items.newItemFromTypeName(typeName)
            if len(self._stack) > 1:
                self._scene.addItem(item)
            else:
                self._scene.addLayer(item)             
        self._stack.append(item)
    
    
    def addProperty(self, key, value):
        item  = self._current()
        
        if not item.hasProperty(key): # assume custom
            raise ParseError("custom properties are not supported yet :( ")

        if item.property(key).deserializeValue(value) == False:
            raise ParseError("""Deserialization Failed. Bad value: %s """ % (str(value))) 
    
    
    def closeNode(self):
        self._stack.pop(-1)
    
    
    def build(self):
        scene = self._scene
        self._scene = None
        return scene
