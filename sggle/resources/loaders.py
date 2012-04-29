'''
Created on Dec 31, 2011

@author: vitali
'''

from PySide.QtCore import QFileInfo
from PySide.QtGui import QIcon

from os import getcwd 
from weakref import WeakValueDictionary

from resource import PixmapResource


class CachedPixmapLoader(object):
    
    def __init__(self):
        object.__init__(self)
        
        self._cache  = WeakValueDictionary()
    
    
    def _loadFromCache(self, key):
        return self._cache.get(key)
    
    
    def _addToCache(self, k, v):
        self._cache[k] = v
        
        
    def load(self, path):
        # cache hit
        pixmap = self._loadFromCache(path)
        if pixmap is not None:
            return pixmap
        
        # cache miss
        pixmap =  PixmapResource(QFileInfo(path))
        if pixmap.isNull():
            pixmap.load(":/missing_texture")
        else:
            self._addToCache(path, pixmap)
            
        return pixmap
    



class PreviewIconLoader(object):
    
    def __init__(self, pixmapLoader):
        object.__init__(self)
        
        self._pixmapLoader = pixmapLoader


    def load(self, path):
        pixmap = self._pixmapLoader.load(path)
        return QIcon(pixmap)




class ResourceLoader(object):
    
    _instance = None
    
    @staticmethod
    def instance():
        if ResourceLoader._instance is None:
            pixmapLoader  = CachedPixmapLoader()
            previewLoader = PreviewIconLoader(pixmapLoader)
            ResourceLoader._instance = ResourceLoader(pixmap      = pixmapLoader, 
                                                      previewIcon = previewLoader)
        
        return ResourceLoader._instance
        
    
    def __init__(self, **loaders):
        object.__init__(self)
        
        for loaderName in loaders.keys():
            self.__setattr__(loaderName, loaders[loaderName])
        
    