'''
Created on Jan 4, 2012

@author: vitali
'''

from PySide.QtCore import Qt
from PySide.QtCore import QDir
from PySide.QtCore import QFileInfo
from PySide.QtCore import QSize

from PySide.QtGui  import QWidget
from PySide.QtGui  import QHBoxLayout
from PySide.QtGui  import QPixmap
from PySide.QtGui  import QPushButton
from PySide.QtGui  import QFileDialog
from PySide.QtGui  import QTabWidget


from PySide.QtGui import QListView
from PySide.QtGui import QFileSystemModel
from PySide.QtGui import QFileIconProvider

   
import sggle.resources as resources
   


def newResourceFolderViewer(path, dock=None):
    view = TextureFolderViewer(path)
    
    if dock:
        dock.setWindowTitle(path)
        dock.setWidget(view)
        return dock
    else:
        return view






class TextureFolderViewer(QListView):
    
    def __init__(self, rootDir): 
        QListView.__init__(self)
    
        self._setDefaults()    
        self.setModel(ResourceFolderModel.newTextureFolderModel())
        self.setRootDir(rootDir)
    
    
    def _setDefaults(self):
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setLayoutMode(QListView.Batched)
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(64,64))
        self.setGridSize(QSize(64,64))
        self.setDragDropMode(QListView.DragOnly)
        
        
    def setRootDir(self, path):
        rootIndex = self.model().setRootPath(path)
        self.setRootIndex(rootIndex)
        



class ResourceFolderModel(QFileSystemModel):
 
    @staticmethod
    def newTextureFolderModel():
        return ResourceFolderModel("*.png", "*.bmp", "*.gif", "*.jpg")
        
        
    def __init__(self, *nameFilters):
        QFileSystemModel.__init__(self)
        
        self._setDefaults()
        self.setNameFilters(nameFilters)
        
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole: #hide filenames                                                                  
            return ""
        return QFileSystemModel.data(self, index, role)


    def _setDefaults(self):
        self.setReadOnly(True)
        self.setFilter(QDir.Files)
        self.setNameFilterDisables(False)
        self.setIconProvider(PreviewIconProvider.instance())

        
    def mimeData(self, indexes): 
        index    = indexes[0]
        filePath = self.filePath(index)  #FIXME: old PyQt4 bug does not apply anymore          
        # PyQt4 bug gives me seg fault when I create instance QMimeData object 
        data     = QFileSystemModel.mimeData(self, indexes)
        data.setText(filePath)
        return data
    
        
        
        
class PreviewIconProvider(QFileIconProvider):
    
    _instance = None
    
    @staticmethod
    def instance():
        if PreviewIconProvider._instance is None:
            PreviewIconProvider._instance = PreviewIconProvider(resources.loader.previewIcon)
        return PreviewIconProvider._instance
        
    
    def __init__(self, iconPreviewLoader):
        QFileIconProvider.__init__(self)

        self._previewLoader = iconPreviewLoader
    
    
    def icon(self, data):
        if isinstance(data, QFileInfo) and data.isFile(): # Create preview
                filePath = data.absoluteFilePath()
                return self._previewLoader.load(filePath)
        
        return QFileIconProvider.icon(self, data)