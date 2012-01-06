'''
Created on Dec 29, 2011

@author: vitali
'''

from .. interfaces import INodeAdapter
from .. interfaces import INodeTreeBuilder

import sggle.scene.items  as items 
import sggle.scene        as scene



#FIXME: Do I need this class?
class ItemAdapter(INodeAdapter):
    
    def __init__(self, item):
        INodeAdapter.__init__(self)
        
        self._item = item
                
        
    def typeName(self):
        return self._item.typeName()
    
    
    def properties(self):
        return self._item.properties()
    
    
    def childItems(self):
        return [ ItemAdapter(child) for child in self._item.childItems() ]

    


class SceneTreeBuilder(INodeTreeBuilder):
    
    def __init__(self):

        self._scene  = None
        self._stack  = []
        
        
    def _current(self):
        return self._stack[-1] if self._stack else None

    
    def startNode(self, typeName):        
        if not self._scene:
            self._scene = scene.newEmptyGraphicsScene()
            item        = self._scene.properties()
        
        else:    
            item = items.newItemFromTypeName(typeName)
            if len(self._stack) > 1:
                self._scene.addItem(item)
            else:
                self._scene.addLayer(item)             
        item.enableDirectEdit() #FIXME: I don't like this!
        self._stack.append(item)
    
    
    def addProperty(self, key, value):
        item  = self._current()
        
        if not item.hasProperty(key): # assume custom
            item.addCustomProperty(key)
        item.setValue(key, value)
    
    
    def closeNode(self):
        self._current().disableDirectEdit()
        self._stack.pop(-1)
    
    
    def build(self):
        scene = self._scene
        self._scene = None
        return scene
