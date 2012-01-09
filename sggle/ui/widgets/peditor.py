'''
Created on Jan 4, 2012

@author: vitali
'''







from PySide.QtCore import Qt

from PySide.QtGui  import QTreeView
from PySide.QtGui import QItemDelegate
from PySide.QtGui import QLineEdit


       
def newPropertiesEditor(model, dock=None):
    editor = PropertiesView()
    editor.setItemDelegate(PropertiesDelegate())
    editor.setModel(model)
    
    editor.setHeaderHidden(True) 
    editor.setIndentation(30)
    editor.setRootIsDecorated(False)

    if dock is  None:
        return editor
    
    dock.setWindowTitle(" Properties ")
    dock.setWidget(editor)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
 
    return dock

        


class PropertiesView(QTreeView):
    
    def __init__(self):
        QTreeView.__init__(self)
        
        
    def reset(self):
        QTreeView.reset(self)
        self.expandAll()
        for c in range(self.model().columnCount()):
            self.resizeColumnToContents(c)
    
    


class PropertiesDelegate(QItemDelegate):
    
    def __init__(self):
        QItemDelegate.__init__(self)
        
    
    def _indexDataType(self, index):
        return type(index.model().data(index,Qt.EditRole))
        
        
    def createEditor(self, parent, option, index):
        value = index.data(Qt.EditRole)
        model = index.model()
        validator = index.data(role=model.ValidatorRole)
        valueType = type(value)
        
        if valueType is bool:
            editor = QItemDelegate.createEditor(self, parent, option, index)
        
        else:
            editor = QLineEdit(parent)
            editor.setValidator(validator)
            
        return editor
    
        
    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        
        if isinstance(editor, QLineEdit):
            editor.setText(str(value))
        else:
            QItemDelegate.setEditorData(self, editor, index)


    
    def setModelData (self, editor, model, index):
        
        if isinstance(editor, QLineEdit):
            valueType = type(index.data(Qt.EditRole))
            validator = editor.validator()
            value     = valueType(editor.text())

            if validator.validateRawValue(value) == validator.Acceptable:
                model.setData(index, valueType(value))
            
        else:
            QItemDelegate.setModelData(self, editor, model, index)
            
            
    