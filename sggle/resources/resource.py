'''
Created on Dec 31, 2011

@author: vitali
'''

from PySide.QtGui import QPixmap


class Resource(object):
    
    def __init__(self, fileInfo):
        object.__init__(self)
        
        self._info = fileInfo
    
        
    def path(self):
        return self._info.absoluteFilePath()
    

    def baseName(self):
        return self._info.baseName()
    
    def fileName(self):
        return self._info.fileName()
    
    def __str__(self):
        return self.fileName()    


    

class PixmapResource(Resource, QPixmap):
    

    def __init__(self, fileInfo):
        Resource.__init__(self, fileInfo)
        QPixmap.__init__(self, self.path())
        