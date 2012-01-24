'''
Created on Jan 24, 2012

@author: vitali
'''

from PySide.QtGui import QWidget
from PySide.QtGui import QDockWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QToolBar
from PySide.QtCore import Qt
from PySide.QtCore import QSize


def newToolbarDockWidget(actions):
    dock = ToolbarDockWidget()
    
    if len(actions):
        toolbar = QToolBar()
        for a in actions:
            toolbar.addAction(a) if a else toolbar.addSeparator()
        
        toolbar.setIconSize(QSize(16,16))
        dock.setToolBar(toolbar)
    
    return dock
    
    
class ToolbarDockWidget(QDockWidget):
    
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)
        
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0,0,0,0)
        self._layout.setSpacing(0)
        
        widget       = QWidget()
        widget.setLayout(self._layout)
        QDockWidget.setWidget(self, widget)


    def setToolBar(self, toolbar):
        self._layout.insertWidget(1, toolbar)
    
    
    def setWidget(self, widget):
        self._layout.insertWidget(0, widget)
    
    
    
    