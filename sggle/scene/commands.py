'''
Created on Oct 5, 2011

@author: vitali
'''

from PySide.QtGui import QUndoCommand
import items as items

def newAddItemCommand(scene, item, x = 0, y = 0, commandBatch = None):  
    layer   = scene.activeLayer()
    return AddItemCommand(scene, item, layer, x,y, commandBatch)


def newAddPixmapItemCommand(scene, path, x = 0, y = 0):
    pixItem = items.newPixmapItemFromPath(path)
    layer   = scene.activeLayer()
    
    return AddItemCommand(scene, pixItem, layer, x,y)


def newDeleteItemCommand(scene, item, batch = None):
    return DeleteItemCommand(scene, item, batch)


def newAddLayerCommand(scene):
    layer = items.newLayerItem()
    return AddLayerCommand(scene, layer)


def newDeleteLayerCommand(scene, layer):
    return DeleteLayerCommand(scene, layer)


def newEditItemPropertyCommand(item, property, value, commandBatch = None):
    return ItemPropertyEditCommand(item, property, value, commandBatch)


def newChangeItemLayerCommand(scene, item, layer):
    return ChangeItemLayerCommand(scene, item, layer)


def newCommandBatch():
    return QUndoCommand()



    
class ItemPropertyEditCommand(QUndoCommand):
    
    
    def __init__(self, item, property, value, parent = None):
        QUndoCommand.__init__(self, parent)
        
        self._item         = item
        self._propertyName = property
        self._oldValue     = item.value(property)
        self._newValue     = value
     
        
    def  _setValue(self, value):
        self._item.setValueDirectly(self._propertyName, value)

        
    def redo(self):
        self._setValue(self._newValue)
        
                
    def undo(self):
        self._setValue(self._oldValue)
        
           
    def mergeWith(self, other):
        return False
        
        

   
class DeleteItemCommand(QUndoCommand):
    
    def __init__(self, scene, item, parentCommand = None):
        QUndoCommand.__init__(self, parentCommand)
        
        self._scene = scene
        self._item  = item
        self._xy    = item.value("position")
        self._z     = item.zValue()
        self._layer = scene.activeLayer()
        
    def redo(self):
        self._scene.removeItem(self._item)
    
    
    def undo(self):
        self._scene.addItem(self._item, self._layer)
        self._item.setValueDirectly("z_order", self._z)
        self._item.setValueDirectly("position", self._xy)
    
    
    
    
class AddItemCommand(QUndoCommand):

    def __init__(self,scene, item, layer, x = 0, y = 0, parent = None):
        QUndoCommand.__init__(self, parent)
        
        self._scene = scene
        self._item  = item
        self._layer = layer
        self._xy    = (x,y)        
        
        
    def redo(self):
        self._scene.addItem(self._item, self._layer, self._xy[0], self._xy[1])


    def undo(self):
        self._scene.removeItem(self._item)
        
        
    
class AddLayerCommand(QUndoCommand):

    def __init__(self,scene, layer):
        QUndoCommand.__init__(self)
        
        self._scene = scene
        self._layer = layer        
        
        
    def redo(self):
        self._scene.addLayer(self._layer)


    def undo(self):
        self._scene.removeLayer(self._layer)
        
        
   
   
class DeleteLayerCommand(QUndoCommand):

    def __init__(self,scene, layer):
        QUndoCommand.__init__(self)
        
        self._scene = scene
        self._layer = layer
        self._z     = layer.zValue()
        self._deleteItemsBatch = newCommandBatch()
        
        for item in layer.childItems():
            newDeleteItemCommand(scene, item, self._deleteItemsBatch)
        
        
    def redo(self):
        self._deleteItemsBatch.redo()
        self._scene.removeLayer(self._layer)


    def undo(self):
        self._scene.addLayer(self._layer)
        self._layer.setValueDirectly("z_order", self._z)
        self._deleteItemsBatch.undo()
        
                

  
class ChangeItemLayerCommand(QUndoCommand):

    def __init__(self,scene, item, layer, parentCommand):
        QUndoCommand.__init__(self, parentCommand)
        
        self._scene     = scene
        self._item      = item
        self._newLayer  = layer 
        self._oldLayer  = item.layer()       
        
    
    def _move(self, layer):
        self._scene.removeItem(self._item)
        self._scene.addItem(self._item, layer)
        
    
    def redo(self):
        self._move(self._newLayer)


    def undo(self):
        self._move(self._oldLayer)
                
 
 
