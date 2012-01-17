'''
Created on Jan 4, 2012

@author: vitali
'''

from PySide.QtGui  import QTabBar 
from PySide.QtGui  import QWidget
from PySide.QtGui  import QVBoxLayout




def newWorkspace(sceneView, fileController):
    tabs      = MainTabBar()
    workspace = Workspace(tabs, sceneView)

        
    tabs.currentChanged.connect(fileController.setActiveScene)
    tabs.tabCloseRequested.connect(fileController.closeScene)
    tabs.tabMoved.connect(fileController.swapSceneIndexOrder)
    
    fileController.sceneAdded.connect(tabs.addTab)
    fileController.sceneRemoved.connect(tabs.removeTab)
    fileController.activeSceneNameChanged.connect(tabs.setCurrentTabTitle)
    
    fileController.cleanStateChanged.connect(tabs.setCleanState)
    
    
        
    return workspace


class Workspace(QWidget):

    
    def __init__(self, tabs, sceneView):
        QWidget.__init__(self)
        
        self._tabs      = tabs
        self._sceneView = sceneView
        self
        
        self._setupLayout()
    
        
    def _setupLayout(self):
        layout    = QVBoxLayout()
        
        layout.addWidget(self._tabs)
        layout.addWidget(self._sceneView)  
        self.setLayout(layout)
        self._tabs.hide()     
        
        
    
    
class MainTabBar(QTabBar):
    
    def __init__(self):
        QTabBar.__init__(self)
        self._setDefaults()
        
        self._clean       = False
        
        
    def _setDefaults(self): 
        self.setMovable(True)
        self.setTabsClosable(True)
        
        
    def tabRemoved(self, index):
        if self.count() < 2:
            self.hide()
    
    
    def tabInserted(self, index):
        if self.count() > 1:
            self.show()
            

    def setCurrentTabTitle(self, text):
        i = self.currentIndex()
        self.setTabText(i, text if self._clean else text + " *")
    
        
    def currentTabTitle(self):
        return  self.tabText(self.currentIndex())
    
    
    def setCleanState(self, clean):
        self._clean = clean
        self.setCurrentTabTitle(self.currentTabTitle().strip(" *"))

         


    