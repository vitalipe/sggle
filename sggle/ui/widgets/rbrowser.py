'''
Created on Jan 4, 2012

@author: vitali
'''


from os.path import expanduser


from PySide.QtCore import Signal
from PySide.QtCore import QDir
from PySide.QtCore import Qt
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
   

   
def newResourceBrowser(dock=None):
    rBrowser = ResourceBrowser(ResourceTabWidget(), OpenTabButton(), TextureFolderViewer)
    rBrowser.openNewTab(expanduser("~"))
    
    if dock is None:
        return rBrowser
    
    dock.setAllowedAreas(Qt.BottomDockWidgetArea)
    dock.setWindowTitle("Resources")
    dock.setWidget(rBrowser)
    
    _setupDynamicDockFeatures(dock)
    
    return dock


def _setupDynamicDockFeatures(dock):
    dockedFeatures   = (dock.DockWidgetVerticalTitleBar | 
                        dock.DockWidgetFloatable        |
                        dock.DockWidgetMovable          | 
                        dock.DockWidgetClosable)
    
    floatingFeatures = (dock.DockWidgetFloatable |
                        dock.DockWidgetMovable   |
                        dock.DockWidgetClosable)
    
    configDockFeatures = lambda f: dock.setFeatures(floatingFeatures if f else dockedFeatures)
    configDockFeatures(False)
    
    dock.topLevelChanged.connect(configDockFeatures)


class ResourceBrowser(QWidget):
    
    def __init__(self, tabWidget, openTabButton, folderViewFactory):
        QWidget.__init__(self)
        
        self._tabWidget          = tabWidget
        self._openTabButton      = openTabButton
        self._folderViewFactory  = folderViewFactory
        self._dirRoot            = QDir.home().path()

        self._connectSignals()
        self._setLayout()    


    def openNewTab(self, path):
        self._tabWidget.addTab(self._folderViewFactory(path), path)
    
    
    def displayFileDialog(self):
    
        path =  QFileDialog.getExistingDirectory(self, "Select Directory", self._dirRoot,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    
        if path:
            self.openNewTab(path)          
            # remember directory 
            parent = QDir(path)
            parent.cdUp()
            self._dirRoot = parent.absolutePath()                                       


    def _setLayout(self):      
        topLayout = QHBoxLayout()
        topLayout.addWidget(self._tabWidget)
        self._tabWidget.setCornerWidget(self._openTabButton)

        self.setLayout(topLayout)
        
        
    def _connectSignals(self):
        self._tabWidget.tabCloseRequested.connect(self._handleTabCloseRequested)
        self._openTabButton.clicked.connect(self.displayFileDialog)

    
    def _handleTabCloseRequested(self, index):
        if self._tabWidget.count() > 1:
            self._tabWidget.removeTab(index)

    
        
        
class ResourceTabWidget(QTabWidget):
    
    def __init__(self):
        QTabWidget.__init__(self)
        
        self.setElideMode(Qt.ElideLeft)
        self.setMovable(True)
        self.setTabsClosable(True)
        

class OpenTabButton(QPushButton):
    
    def __init__(self, parent=None):
        QPushButton.__init__(self, "", parent)
        
        iconPixmap = QPixmap(":/icons/resource-folder-add")
        
        self.setIcon(iconPixmap)
        self.setMaximumSize((iconPixmap.size()))        
        self.setFlat(True)




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