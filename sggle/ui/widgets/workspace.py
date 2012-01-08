'''
Created on Jan 4, 2012

@author: vitali
'''

from PySide.QtGui  import QTabBar 
from PySide.QtGui  import QWidget
from PySide.QtGui  import QVBoxLayout




def newWorkspace(sceneView, sceneGroup, fileController):
    tabs      = MainTabBar()
    workspace = Workspace(tabs, sceneView)

    #FIXME: move all this into a controller
    tabs.currentChanged.connect(lambda i: sceneGroup.setActiveScene(sceneGroup.scene(i)))
    sceneGroup.activeSceneChanged.connect(lambda s: tabs.setCurrentIndex(sceneGroup.index(s)) if s else -1)
    tabs.tabMoved.connect(sceneGroup.swapIndexs)
    
    sceneGroup.sceneWasAdded.connect(lambda i, name: tabs.addTab(name))
    sceneGroup.sceneWasRemoved.connect(tabs.removeTab)
        
    tabs.tabCloseRequested.connect(fileController.closeScene)
    
    setTabTitle = (lambda i,p: 
                   tabs.setCurrentTabTitle(i.value("name")) 
                   if p == "name" and i == sceneGroup.activeScene().rootItem() else None) 
    sceneGroup.itemPropertyWasChanged.connect(setTabTitle)    
        
    return workspace


class Workspace(QWidget):
    
    def __init__(self, tabs, sceneView):
        QWidget.__init__(self)
        
        self._tabs      = tabs
        self._sceneView = sceneView
        
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
        
        
    def _setDefaults(self): 
        self.setMovable(True)
        self.setTabsClosable(True)
        
        
    def tabRemoved(self, index):
        if self.count() < 2:
            self.hide()
    
    
    def tabInserted(self, index):
        if self.count() > 1:
            self.show()
    
    #FIXME: workspace should provide this interface
    def setCurrentTabTitle(self, text):
        i = self.currentIndex()
        self.setTabText(i, text)


    