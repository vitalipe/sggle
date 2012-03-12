'''
Created on Oct 5, 2011

@author: vitali
'''

from PySide.QtGui import QUndoCommand
import items as items

def newAddItemCommand(scene, item, xy, layer = None, select = False, commandBatch = None):  
    layer   = scene.activeLayer() if not layer else layer
    return newCommand(AddItemCommand(scene, item, layer, xy, select), commandBatch)


def newAddPixmapItemCommand(scene, path, x = 0, y = 0, commandBatch = None):
    pixItem = items.newPixmapItemFromPath(path)
    layer   = scene.activeLayer()
    
    return newCommand(AddItemCommand(scene, pixItem, layer, x,y), commandBatch)


def newDeleteItemCommand(scene, item, commandBatch = None):
    return newCommand(DeleteItemCommand(scene, item), commandBatch)


def newAddLayerCommand(scene):
    layer = items.newLayerItem()
    return AddLayerCommand(scene, layer)


def newAddExistingLayerCommand(scene, layer, commandBatch = None):
        return newCommand(AddLayerCommand(scene, layer), commandBatch)


def newDeleteLayerCommand(scene, layer):
    return DeleteLayerCommand(scene, layer)


def newEditItemPropertyCommand(item, propertyName, value, commandBatch = None):
     return newCommand(ItemPropertyEditCommand(item.property(propertyName), value), commandBatch)


def newEditPropertyCommand(property, value, commandBatch = None):
    return newCommand(ItemPropertyEditCommand(property, value), commandBatch)


def newChangeZValueCommand(item, newZValue, batch =  None):
     return newCommand(ItemChangeZValueCommand(item, newZValue), batch)


def newChangeItemLayerCommand(scene, item, layer, commandBatch = None): # FIXME: Remove
     return newCommand(ChangeItemLayerCommand(scene, item, layer), commandBatch)


def newItemPropertyResetCommand(property, commandBatch = None):
    return newCommand(ItemPropertyResetCommand(property), commandBatch)
                      
    
def newCommandBatch(ordered = True):
    if ordered:
        return OrderedCommandBatch()
    else:
        return UnorderedCommandBatch()


def newCommand(cmd, cmdBatch):
    if cmdBatch:
        cmdBatch.appendCommand(cmd)
    return cmd




class ICommandBatch(QUndoCommand):
    
    def appendCommand(self, command):
        raise NotImplementedError()
    
    def redo(self):
        raise NotImplementedError()
    
    def undo(self):
        raise NotImplementedError()

    def childCount(self):
        raise NotImplementedError()
    
    def mergeWith(self, other): 
        return False # never merge 

            


class OrderedCommandBatch(ICommandBatch):
    
    def __init__(self):
        super(OrderedCommandBatch, self).__init__()
    
        self._commands = []

        
    def appendCommand(self, command):        
        if len(self._commands) and command.id() != -1 and command.id() == self._commands[-1].id():
                    if self._commands[-1].mergeWith(command, force = True):
                        return
        
        self._commands.append(command)
        
    
    def redo(self):
        for cmd in self._commands:
            cmd.redo()
            
            
    def undo(self):
        for cmd in reversed(self._commands):
            cmd.undo()
        
           
    def childCount(self):
        return len(self._commands)
    
    
    
    
class UnorderedCommandBatch(ICommandBatch):
    
    def __init__(self):
        super(UnorderedCommandBatch, self).__init__()
    
        self._commands     = {} # key: _item or id(), value: list of commands
        self._commandCount = 0

        
    def appendCommand(self, command):
        # Yes, this is a major hack, I am using items as keys because most of 
        # the time  we have lots of commands with the same id() on different 
        # items (rotation, scaling, etc...) 
        key    = command._item if hasattr(command, "_item") else command.id()
        values = self._commands.get(key)
        
        if values:
            for parentCommand in values:
                if command.id() != -1 and command.id() == parentCommand.id():
                    if parentCommand.mergeWith(command, force = True):
                        break
            else: # can't merge
                values.append(command)
        else:
            self._commands[key] = [command,]
    
        self._commandCount += 1


    def undo(self):
        for cmd in self.commands():
            cmd.undo()
            
            
    def redo(self):
        for cmd in self.commands():
            cmd.redo()
            
                   
    def commands(self):
        for listOfCommands in self._commands.values():
            for cmd in listOfCommands:
                yield cmd
    
    def childCount(self):
        return self._commandCount
    
    
    
class ItemChangeZValueCommand(QUndoCommand):
    
    
    def __init__(self, item, newZValue):
        QUndoCommand.__init__(self)
        
        self._item         = item
        self._oldValue     = item.zValue()
        self._newValue     = newZValue
     
        
    def  _setValue(self, value):
        self._item.setZValue(value)

        
    def redo(self):
        self._setValue(self._newValue)
        
                
    def undo(self):
        self._setValue(self._oldValue)
    
        
    def id(self):
        return 100222
    
    
    def mergeWith(self, other, force = False): 
        if self._item is other._item:
            self._newValue = other._newValue
            return True
        else:
            return False
        
        
        
class ItemPropertyResetCommand(QUndoCommand):
    
    
    def __init__(self, property):
        QUndoCommand.__init__(self)
        
        self._oldValue = property.value()
        self._property = property


    def redo(self):
        self._property.reset()
        
        
    def undo(self):  
        self._property.setValueDirectly(self._oldValue)
        
        
        
        
class ItemPropertyEditCommand(QUndoCommand):
    
    
    def __init__(self, property,value):
        QUndoCommand.__init__(self)
        
        self._property  = property
        self._oldValue  = property.value()
        self._newValue  = value
     
        
    def  _setValue(self, value):
        self._property.setValueDirectly(value)

        
    def redo(self):
        self._setValue(self._newValue)
        
                
    def undo(self):
        self._setValue(self._oldValue)
    
        
    def id(self):
        return 1001
    
    
    def mergeWith(self, other, force = False):
        if not force:
            return False
        
        item      = self._property.item()
        otherItem = other._property.item()
        
        if (item is otherItem) and self._property is other._property:
            self._newValue = other._newValue
            return True
        else:
            return False             
        
        

   
class DeleteItemCommand(QUndoCommand):
    
    def __init__(self, scene, item):
        QUndoCommand.__init__(self)
        
        self._scene = scene
        self._item  = item
        self._xy    = item.value("position")
        self._z     = item.zValue()
        self._layer = item.layer()
        
    def redo(self):
        self._scene.removeItem(self._item)
    
    
    def undo(self):
        self._scene.addItem(self._item, self._layer)
        self._item.setZValue(self._z)
        self._item.setValueDirectly("position", self._xy)
    
    
    
    
class AddItemCommand(QUndoCommand):

    def __init__(self,scene, item, layer, xy, select):
        QUndoCommand.__init__(self)
        
        self._scene  = scene
        self._item   = item
        self._layer  = layer
        self._xy     = xy   
        self._select = select     
        
        
    def redo(self):
        item = self._item
        self._scene.addItem(item, self._layer)
        item.setValueDirectly("position", self._xy)
        item.setSelected(self._select)


    def undo(self):
        self._scene.removeItem(self._item)
        
   
   
   
class AddLayerCommand(QUndoCommand):

    def __init__(self,scene, layer):
        QUndoCommand.__init__(self)
        
        self._scene = scene
        self._layer = layer
        self._itemsBatch = newCommandBatch()
        
        for item in layer.childItems():
            pos = item.value("position")
            item.setParentItem(None)
            newAddItemCommand(scene, item, pos, layer = layer, commandBatch=self._itemsBatch)

        
    def redo(self):
        self._scene.addLayer(self._layer)
        self._itemsBatch.redo()
        
        
    def undo(self):
        self._itemsBatch.undo()
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
        self._layer.setZValue(self._z)
        self._deleteItemsBatch.undo()
        

        
  
class ChangeItemLayerCommand(QUndoCommand): # FIXME: Remove

    def __init__(self,scene, item, layer):
        QUndoCommand.__init__(self)
        
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
                
 
 
