'''
Created on Oct 20, 2011

@author: vitali
'''

from PySide.QtCore import QPointF
from PySide.QtCore import QRectF
from PySide.QtCore import QAbstractItemModel
from PySide.QtCore import QAbstractListModel
from PySide.QtCore import QModelIndex
from PySide.QtCore import Qt
from PySide.QtGui import  QIcon

from PySide.QtGui import QItemSelectionModel
from PySide.QtGui import QItemSelection




class ItemPropertiesModel(QAbstractItemModel):

    NameColumn   = 0
    SepColumn    = 1
    ValueColumn  = 2
    
    ValidatorRole = 128
    
    def __init__(self, sceneGroup):
        QAbstractItemModel.__init__(self)
        
        self._item           = None
        self._sceneGroup     = sceneGroup
        self._decorationIcon = QIcon(":/icons/open") #FIXME: different icon
        
        sceneGroup.activeSceneChanged.connect(self._updateItem)
        sceneGroup.activeLayerChanged.connect(self._updateItem)
        sceneGroup.selectionMasterChanged.connect(self._updateItem)
        
        sceneGroup.itemPropertyWasChanged.connect(lambda i,v: self._notifyPropertyChanged(v)
                                                   if i is self._item else None)   
        self._updateItem()
        
        
    def _notifyPropertyChanged(self, propertyName):
        row       = self._item._properties.keys().index(propertyName)
        indexFrom = self.createIndex(row,ItemPropertiesModel.ValueColumn)
        indexTo   = self.createIndex(row+1,ItemPropertiesModel.ValueColumn)

        self.dataChanged.emit(indexFrom, indexTo)
        
        
    def _updateItem(self):
        if self._sceneGroup.activeScene() is None:
            return None
        
        funcs = [
                 self._sceneGroup.activeScene().selectionMaster,
                 self._sceneGroup.activeScene().activeLayer,
                 self._sceneGroup.activeScene().rootItem 
                 ]
        
        for f in funcs:
            item = f()
            if item: 
                break     

        self._setItem(item)
        
                
    def _setItem(self, item):
        oldItem = self._item
        if item is oldItem:
            return
        
        self._item = item
        self.reset() 
    
    
    # FIXME:
    def _filterDisplayData(self, data):

        if isinstance(data, QPointF):
            return "(%d, %d)" % (data.x(), data.y())
        if isinstance(data, QRectF):
            return "[%dx%d]" % (data.width(),data.height())
        
        return str(data)

        
        
    def index(self, row, col, parentIndex = QModelIndex()):
        if not self.hasIndex(row, col, parentIndex):
            return QModelIndex()
        
        if parentIndex.isValid(): # value component
            property = self._item.property(parentIndex.row())
            return self.createIndex(row, col, property) 

        # property
        return self.createIndex(row, col) 
    
    
    def parent(self, index):
        
        if index.internalPointer() is None: # property
            return QModelIndex()

        else:# value component
            parentProperty = index.internalPointer()
            row = self._item.propertyIndex(parentProperty)
            return self.createIndex(row, 0)
            
            
    #FIXME: refactor
    def data(self, index, role=Qt.DisplayRole):
        
        if not index.isValid():
            return None
        
        #FIXME: Decoration place holder
        if role == Qt.DecorationRole and index.column() == ItemPropertiesModel.NameColumn:
            return self._decorationIcon
        
        if role == ItemPropertiesModel.ValidatorRole:
            if index.parent().isValid():
                p = index.internalPointer()
                p = p.componentList()[index.row()]
                return p.validator()
            else:
                return self._item.property(index.row()).validator()

        if role != Qt.EditRole and role != Qt.DisplayRole:
            return None
        
        row = index.row() 
        col = index.column()
        if index.parent().isValid():
            property = index.internalPointer()
            component = property.componentList()[row]
            if col == ItemPropertiesModel.NameColumn:
                return component.name()
            if col == ItemPropertiesModel.ValueColumn:
                return component.value()
            if col == ItemPropertiesModel.SepColumn:
                return ":"
        
        if index.parent().isValid() == False:
            return self._propertyData(index, role) 
    
    
    def _propertyData(self, index, role=Qt.DisplayRole):
       
        row       = index.row()
        col       = index.column()
        property  = self._item.property(row)
        
        if col == ItemPropertiesModel.NameColumn:
            cell = property.name()
        if col == ItemPropertiesModel.ValueColumn:
            cell = property.value()
        if col == ItemPropertiesModel.SepColumn:
            cell = ":"
    
        if role == Qt.EditRole:
            return cell
        
        if role == Qt.DisplayRole:
            return self._filterDisplayData(cell)
               
        # Unsupported role
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """ """    
        
        col        = index.column()
        
        if col != ItemPropertiesModel.ValueColumn or role != Qt.EditRole:
            return False
        
        if index.parent().isValid():
            property = index.internalPointer()
            component = property.componentList()[index.row()]
            component.setValue(value)
        else:
            property   = self._item.property(index.row())
            property.setValue(value)
            
        return True


    def insertRows(self, row, count, parent = QModelIndex() ):
        return False 
    
    
    def rowCount(self, index=QModelIndex()):
        
        if self._item is None:
            return 0
        
        if not index.isValid():
            return self._item.propertyCount()

        if not index.parent().isValid(): # get number of components
            p = self._item.property(index.row())
            if hasattr(p, "componentList"):
                return len(p.componentList())
            else:
                return 0
        
        else: # components can't have children
            return 0
      
      
    def columnCount(self, parentIndex = QModelIndex()):
            return 3

    
    def headerData(self, selection, orientation, role=Qt.DisplayRole):
        return None
    
    
    def flags(self, index):
        
        if not index.isValid():
            return 0
       
        col   = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable 
        
        if col == ItemPropertiesModel.ValueColumn and self.rowCount(index) == 0:
            if index.parent().isValid():
                p = index.internalPointer()
            else:
                p = self._item.property(index.row())
            if p.readOnly() == False:
                flags |= Qt.ItemIsEditable
        
        return flags 




class ItemTreeModel(QAbstractItemModel):
    """ Provide tree model interface for the current active layer """

    ItemRole    =  100
 
 
    def __init__(self, sceneGroup):
        QAbstractItemModel.__init__(self)
    
        self._sceneGroup     = sceneGroup
        self._selectionModel = ItemSelectionModel(sceneGroup, self) 
        self._layer          = None
        
        sceneGroup.activeSceneChanged.connect(self._handleActiveLayerOrSceneChanged)
        sceneGroup.activeLayerChanged.connect(self._handleActiveLayerOrSceneChanged)
        sceneGroup.listOfItemsChanged.connect(lambda p: self.reset() if p is self._root() else None)
        sceneGroup.itemPropertyWasChanged.connect(self._handleItemPropertyWasChanged)

    
    def _root(self):
        return self._layer
        
        
    def _handleItemPropertyWasChanged(self, item, name):
        if item.parentItem() is self._root() and name == "name":
            self.reset()
            self.selectionModel().updateFromScene()
        
        
    def _handleActiveLayerOrSceneChanged(self):
        if self._sceneGroup.activeScene():
            newLayer = self._sceneGroup.activeScene().activeLayer()        
        else:
            newLayer = None
            
        self._layer = newLayer
        self.reset()
        self.selectionModel().updateFromScene()


    def index(self, row, col, parentIndex = QModelIndex()):
        
        if not self.hasIndex(row, col, parentIndex):
            return QModelIndex()
        
        parent = parentIndex.internalPointer() if parentIndex.isValid() else self._root()
        item   = parent.childItems()[row]    

        return self.createIndex(row, col, item) 
    
    
    def data(self, index, role=Qt.DisplayRole):
        
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole or role ==  Qt.EditRole:
            return index.internalPointer().value("name")
        
        if role == ItemTreeModel.ItemRole:
            return index.internalPointer()
        
        return None
        

    def setData(self, index, value, role=Qt.EditRole):
        return False
    
    
    def parent(self, childIndex):
        
        if not childIndex.isValid():
            return QModelIndex()
        
        parentItem = childIndex.internalPointer().parentItem()
        if parentItem:
            return self.createIndex(0, 0, parentItem)
        else:
            return QModelIndex()        


    def flags(self, index):
        
        if not index.isValid():
            return 0
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled #| Qt.ItemIsDropEnabled 
    
    
    def columnCount(self, parentIndex):
        return 1
    
    
    def rowCount(self, parentIndex):
        
        if parentIndex.isValid():
            childItems = parentIndex.internalPointer().childItems()
        elif self._root():
            childItems = self._root().childItems()
        else:
            childItems = []    
        
        return len(childItems)
       
       
    def indexFromItem(self, item):
        
        parent = item.parentItem()
        row    = parent.childItems().index(item)
        
        return self.createIndex(row, 0, item) 
        
       
    def selectionModel(self):
        assert self._selectionModel # Catch crash
        return self._selectionModel
    
        
    def headerData(self, section, orientation,  role=Qt.DisplayRole):
        #if role == Qt.DisplayRole and self._root():
        #    if self._root():
        #        return self._root().value("name")
        pass
            
        

class LayerListModel(QAbstractListModel):
    
    #Custom roles
    LayerRole  = 42 # ;-)
    
    
    def __init__(self, sceneGroup):
        QAbstractListModel.__init__(self)
        
        self._sceneGroup     = sceneGroup
        self._selectionModel = LayerSelectionModel(sceneGroup, self)
        
        
        sceneGroup.activeSceneChanged.connect(self.reset)
        sceneGroup.listOfLayersChanged.connect(self.reset)
        sceneGroup.itemPropertyWasChanged.connect(self._handleItemPropertyWasChanged)
     
    def _handleItemPropertyWasChanged(self, item, property):
        if item in self._layers():
            self.reset()
            self.selectionModel().updateFromScene()
     
        
    def _layers(self):
        scene = self._sceneGroup.activeScene()
        if scene:
            return scene.layers()
        else:
            return []
        
        
    def rowCount(self, parentIndex):
        return len(self._layers())
    
    
    def data(self, index, role=Qt.DisplayRole):
        
        if not index.isValid():
            return None
        
        layer  = self._layers()[index.row()]         
        
        if role == Qt.DisplayRole or role ==  Qt.EditRole:
            return layer.value("name")
        if role == LayerListModel.LayerRole:
            return layer
        
        return None
    
    
    def selectionModel(self):
        assert self._selectionModel
        return self._selectionModel



        
class ItemSelectionModel(QItemSelectionModel):
    
    def __init__(self, sceneGroup, model):
        QItemSelectionModel.__init__(self, model)
        
        self._sceneGroup = sceneGroup
        
        self._sceneGroup.selectionChanged.connect(self.updateFromScene)
        self.selectionChanged.connect(self.updateFromView)
        
        
    def updateFromScene(self):
        items = self._sceneGroup.activeScene().selectedItems()
        selection = QItemSelection()
        
        for item in items:
            index = self.model().indexFromItem(item)
            selection.select(index, index)
            
        self.select(selection, QItemSelectionModel.ClearAndSelect)
    
    
    def updateFromView(self, selected, deselected):
        selectedIndexes   = selected.indexes()
        deselectedIndexes = deselected.indexes() 
        scene             = self._sceneGroup.activeScene()
        
        scene.blockSignals(True)
                
        for index in deselectedIndexes:
            item = index.data(role=ItemTreeModel.ItemRole)
            item.setSelected(False)
        
        for index in selectedIndexes:
            item = index.data(role=ItemTreeModel.ItemRole)
            item.setSelected(True)
            
        scene.blockSignals(False)
        scene.selectionChanged.emit()
            



class LayerSelectionModel(QItemSelectionModel):
    
    def __init__(self, sceneGroup, model):
        QItemSelectionModel.__init__(self, model)
        
        self._sceneGroup = sceneGroup
        
        self._sceneGroup.activeLayerChanged.connect(self.updateFromScene)
        self.currentChanged.connect(self.updateSceneFromView)
        
    def reset(self):
        QItemSelectionModel.reset(self)
        self.updateFromScene()
            
            
    def updateFromScene(self):
        activeLayer = self._sceneGroup.activeScene().activeLayer()        
        
        if activeLayer is None:
            self.setCurrentIndex(self.model().index(-1, -1), QItemSelectionModel.ClearAndSelect)
            return
        
        layers = self._sceneGroup.activeScene().layers()
        row    = layers.index(activeLayer)
        index = self.model().index(row, 0)
        self.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    
    def updateSceneFromView(self, seletedIndex):
        layer = seletedIndex.data(role=LayerListModel.LayerRole)
        self._sceneGroup.activeScene().setActiveLayer(layer)
            
        
        
        

        
        
        