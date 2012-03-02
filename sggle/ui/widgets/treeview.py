'''
Created on Jan 4, 2012

@author: vitali
'''


from PySide.QtCore import Qt
from PySide.QtGui  import QListView
from PySide.QtGui import QTreeView


    
def newLayerList(model, dock=None):
    layerList = UnselectableListView()
    layerList.setModel(model)
    layerList.setSelectionModel(model.selectionModel())

    if dock is None:
        return layerList
    
    dock.setWindowTitle(" Layers ")
    dock.setWidget(layerList)
    
    dock.setMinimumWidth(230)
    dock.setMaximumHeight(150)  
    
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    return dock


def newItemTree(model, dock=None):
    itemTree = QTreeView()
    
    itemTree.setSelectionMode(QTreeView.ExtendedSelection)
    itemTree.setDragEnabled(False)
    itemTree.setHeaderHidden(True)
    itemTree.setRootIsDecorated(False)
    itemTree.setModel(model)
    itemTree.setSelectionModel(model.selectionModel())
    
    if dock is None:
        return itemTree
    
    dock.setWindowTitle(" Items ")
    dock.setWidget(itemTree)
    
    dock.setMinimumWidth(230)
    dock.setMinimumHeight(150)  
    
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    
    return dock
    
    
    
    

    
class UnselectableListView(QListView):
    
    def mousePressEvent(self, event):
        self.clearSelection()
        self.setCurrentIndex(self.model().index(-1, -1))
        
        QListView.mousePressEvent(self, event)

