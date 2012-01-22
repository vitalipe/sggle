'''
Created on Dec 31, 2011

@author: vitali
'''

from os.path import splitext
import builtin


def newLayerItem():
    return builtin.Layer()    

         
def newPixmapItemFromPath(path):
    item =  builtin.TextureItem()
    item.setValueDirectly("texture", path)
    item.setValueDirectly("name", splitext(path)[0])

    return item


def newRootItem():
    return builtin.SceneRoot()    


def newItemFromTypeName(typeName):
    try:
        return eval("builtin." + typeName)()
    except AttributeError:
        return None