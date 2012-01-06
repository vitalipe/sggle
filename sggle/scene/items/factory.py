'''
Created on Dec 31, 2011

@author: vitali
'''

import builtin

def newLayerItem(defaults = None):
    layer = builtin.Layer()
    _createItemDefaults(layer, defaults)
    
    return layer

         
def newPixmapItemFromPath(path):
    item =  builtin.TextureItem()
    _createItemDefaults(item, {"texture" : path })
    name =  item.value("texture").baseName()
    item.setValue("name", name)
    
    return item


def newRootItem(defaults = None):
    item =  builtin.SceneRootItem()
    _createItemDefaults(item, defaults)
    
    return item


def _createItemDefaults(item, defaults = None):
    if defaults:
        for key,value in defaults.items():
            if not item.hasProperty(key): # assume custom
                item.addCustomProperty(key)
            item.setValue(key, value)
            

def newItemFromTypeName(typeName):
    try:
        return eval("builtin." + typeName)()
    except AttributeError:
        return None