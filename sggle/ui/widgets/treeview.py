'''
Created on Jan 4, 2012

@author: vitali
'''


from PySide.QtCore import Qt
from PySide.QtGui  import QListView
from PySide.QtGui import QTreeView



    
def newLayerList(model, dock=None):
    layerList = DeselectableListView()
    layerList.setModel(model)
    layerList.setSelectionModel(model.selectionModel())

    if dock is None:
        return layerList
    
    dock.setWindowTitle(" Layers ")
    dock.setWidget(layerList)
    dock.setMinimumWidth(150)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    return dock


def newItemTree(model, dock=None):
    itemTree = QTreeView()
    
    itemTree.setSelectionMode(QTreeView.ExtendedSelection)
    itemTree.setDragEnabled(False)
    itemTree.setHeaderHidden(True)
    itemTree.setModel(model)
    itemTree.setSelectionModel(model.selectionModel())
    
    if dock is None:
        return itemTree
    
    dock.setWindowTitle(" Items ")
    dock.setWidget(itemTree)
    dock.setMinimumWidth(150)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    
    return dock
    
    
    
    

    
class DeselectableListView(QListView):
    
    def mousePressEvent(self, event):
        self.clearSelection()
        self.setCurrentIndex(self.model().index(-1, -1))
        QListView.mousePressEvent(self, event)

