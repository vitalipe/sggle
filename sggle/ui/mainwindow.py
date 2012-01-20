'''
Created on Nov 8, 2011

@author: vitali
'''
from sys import exit
from PySide.QtCore import Qt


from PySide.QtGui import QMainWindow
from PySide.QtGui import QDockWidget
from PySide.QtGui import QAction
from PySide.QtGui import QMenu
from PySide.QtGui import QKeySequence
from PySide.QtGui import QMessageBox
from PySide.QtGui import QToolBar
from PySide.QtGui import QIcon



import widgets
import controllers

import sggle.scene as scene


# FIXME: Move to config 
class ActionKeySequences(object):
    
    undoSequence  = QKeySequence("Ctrl+z")
    redoSequence  = QKeySequence("Ctrl+y")
    newSequence   = QKeySequence("Ctrl+n")
    saveSequence  = QKeySequence("Ctrl+s")
    openSequence  = QKeySequence("Ctrl+o")
    closeSequence = QKeySequence("Ctrl+w")
    copySequence  = QKeySequence("Ctrl+c")
    cutSequence   = QKeySequence("Ctrl+x")
    pasteSequence = QKeySequence("Ctrl+v")
    
    zoomInSequence            = QKeySequence("ctrl++")
    zoomOutSequence           = QKeySequence("ctrl+-")
    centerSelecetionSequence  = QKeySequence("Ctrl+i")


    
    deleteSelectedItemsSeqence = QKeySequence("Delete")
    deleteActiveLayerSeqence   = QKeySequence("Shift+Delete")
    addNewLayerSeqence         = QKeySequence("Insert")

    
    


class MainWindow(QMainWindow):
  
  
    def __init__(self):
        QMainWindow.__init__(self)
           
        self.sceneGroup  = scene.newSceneGroup(self)
        self.actions     = {}
         
        self.setWindowState(Qt.WindowMaximized)
        
        self._createControllers()
        self._createActions()
        self._createWidgets()
        self._createMenuBars()
        self._createToolBars()        
 
    def _createToolBars(self):
        
        toolBar = QToolBar("tools", self)
        toolBar.setFloatable(False)
        toolBar.addAction(self.actions["scene-new"])
        toolBar.addAction(self.actions["scene-save"])
        toolBar.addAction(self.actions["scene-open"])
        
        self.addToolBar(toolBar)
        
 
    def _createControllers(self):
        
        self.fileController  =  controllers.FileController(self.sceneGroup)
        self.itemsController =  controllers.ItemsController(self.sceneGroup)
        self.viewController  =  controllers.ViewController(self.sceneGroup, 
                                                           scene.newWelcomeScreenScene())

        
    def _scene(self):
        return self.sceneGroup.activeScene()
    
    
    def addAction(self, name, callback, trigger, displayName = None, disabled = True):
        displayName = displayName if displayName else name
        
        action = QAction(displayName, self)
        action.setDisabled(disabled)
        if callback: action.triggered.connect(callback)
        if trigger:  trigger.connect(action.setEnabled)
        self.actions[name] = action
        
    
    def _createActions(self):
       
        sceneGroup      = self.sceneGroup
        fileController  = self.fileController
        itemsController = self.itemsController
        viewController  = self.viewController

       
        self.addAction("layer-new", 
                       itemsController.addNewLayer, 
                       itemsController.canAddNewLayerChanged, # check for scene
                       "&Add New Layer", 
                       disabled = True)
             
             
        self.addAction("layer-delete", 
                       itemsController.deleteActiveLayer, 
                       itemsController.canDeleteActiveLayerChanged, 
                       "&Delete Active Layer", 
                       disabled = True)
        
        
        self.addAction("layer-move-up", 
                       itemsController.moveLayerUp,
                       itemsController.canMoveLayerUpChanged,
                       "Move Up Layer", 
                       disabled = True)
        
        
        self.addAction("layer-move-down", 
                       itemsController.moveLayerDown,
                       itemsController.canMoveLayerDownChanged,
                       "Move Down Layer", 
                       disabled = True)
        
        
        self.addAction("layer-move-top", 
                       itemsController.moveLayerToTop,
                       itemsController.canMoveLayerUpChanged,
                       "Move Layer To Top", 
                       disabled = True)
        
        
        self.addAction("layer-move-bottom", 
                       itemsController.moveLayerToBottom,
                       itemsController.canMoveLayerDownChanged,
                       "Move Layer To Bottom", 
                       disabled = True)
        
        
        self.addAction("selection-delete", 
                       itemsController.deleteSelectedItems,
                       itemsController.canDeleteItemSelectionChanged,
                       "Delete &Selection", 
                       disabled = True)
        
        
        self.addAction("selection-move-up", 
                       itemsController.moveItemSelectionUp,
                       itemsController.canMoveSelectionUpChanged,
                       "Move Up Selection", 
                       disabled = True)
        
        
        self.addAction("selection-move-down", 
                       itemsController.moveItemSelectionDown,
                       itemsController.canMoveSelectionDownChanged,
                       "Move Down Selection", 
                       disabled = True)

        
        self.addAction("selection-move-top", 
                       itemsController.moveItemSelectionToTop,
                       itemsController.canMoveSelectionUpChanged,
                       "Move Selection To Top", 
                       disabled = True)


        self.addAction("selection-move-bottom", 
                       itemsController.moveItemSelectionToBottom,
                       itemsController.canMoveSelectionDownChanged,
                       "Move Selection To Bottom", 
                       disabled = True)
        
        
        self.addAction("edit-undo", 
                       sceneGroup.undoGroup().undo,
                       sceneGroup.undoGroup().canUndoChanged,
                       "Undo", 
                       disabled = True)
        
        
        self.addAction("edit-redo", 
                       sceneGroup.undoGroup().redo,
                       sceneGroup.undoGroup().canRedoChanged,
                       "Redo", 
                       disabled = True)
        
        
        self.addAction("edit-copy", 
                       itemsController.copyToClipboard, 
                       itemsController.canCopyChanged,
                       "&Copy", 
                       disabled = True)
        
        
        self.addAction("edit-cut", 
                       itemsController.cutToClipboard, 
                       itemsController.canCopyChanged,
                       "Cut", 
                       disabled = True)
        
        
        self.addAction("edit-paste", 
                       itemsController.pasteFromClipboard,
                       itemsController.canPasteChanged,
                       "&Paste", 
                       disabled = True)
     
     
        self.addAction("view-zoom-in", 
                       viewController.zoomIn,
                       viewController.canZoomInChanged,
                       "Zoom &In", 
                       disabled = True)
        
        self.addAction("view-zoom-out", 
                       viewController.zoomOut,
                       viewController.canZoomOutChanged,
                       "Zoom &Out", 
                       disabled = True)
                
                
        self.addAction("view-zoom-reset", 
                       viewController.resetZoom,
                       viewController.canResetZoomChanged,
                       "&Reset Zoom", 
                       disabled = True)
        
        
        self.addAction("view-center-selection", 
                       viewController.centerOnSelectionMaster,
                       None, #FIXME:
                       "Center On Selection", 
                       disabled = True)
        
        
        self.addAction("view-center-origin", 
                       viewController.centerOnOrigin,
                       None, #FIXME:
                       "Center On Origin", 
                       disabled = True)


        self.addAction("scene-new", 
                       fileController.new,
                       None,
                       "New", 
                       disabled = False)
        
        self.addAction("scene-close", 
                       fileController.closeActiveScene,
                       fileController.sceneAvailableChanged,
                       "Close", 
                       disabled = True)
        
        
        self.addAction("scene-save", 
                       fileController.saveActiveScene,
                       fileController.cleanStateChanged,
                       "Save", 
                       disabled = True)
        
        
        self.addAction("scene-save-as", 
                       fileController.saveActiveSceneAs,
                       fileController.sceneAvailableChanged,
                       "Save As", 
                       disabled = True)
        
        self.addAction("scene-open", 
                       fileController.openScene,
                       None, 
                       "Open", 
                       disabled = False)
        
        
        self.addAction("app-quit", 
                       self.close,
                       None, 
                       "Quit", 
                       disabled = False)
 


    def _createWidgets(self):
        
        sceneGroup  = self.sceneGroup
        
        self._sceneView      = widgets.newGraphicsView()
        self._workspace      = widgets.newWorkspace(self._sceneView, self.fileController)
 
        self.viewController.setView(self._sceneView)
        self.setCentralWidget(self._workspace)

        
        # Layer list
        layersDock = widgets.newLayerList(sceneGroup.layerListModel(), QDockWidget())  
        self.addDockWidget(Qt.LeftDockWidgetArea, layersDock)
        
        # Item tree 
        itemsDock  = widgets.newItemTree(sceneGroup.activeItemsTreeModel(), QDockWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, itemsDock)
        
        #Properties Editor 
        PropertiesDock = widgets.newPropertiesEditor(sceneGroup.itemPropertiesModel(), QDockWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, PropertiesDock)
        
        # Resource browser
        resourcesDock   = widgets.newResourceBrowser(QDockWidget())
        self.addDockWidget(Qt.BottomDockWidgetArea, resourcesDock)
        
        
    def _createMenuBars(self):
        assert self.actions
        
        menuBar = self.menuBar()
        actions = self.actions
        
        
        # File Menu
        fileMenu =  QMenu("&File", self)
        fileMenu.addAction(actions["scene-new"])
        fileMenu.addAction(actions["scene-save"])
        fileMenu.addAction(actions["scene-save-as"])
        fileMenu.addAction(actions["scene-open"])
        fileMenu.addAction(actions["scene-close"])
        fileMenu.addAction(actions["app-quit"])
        menuBar.addMenu(fileMenu)


            
        # Edit Menu
        editMenu = QMenu("&Edit", self) 
        editMenu.addAction(actions["layer-new"])
        editMenu.addAction(actions["layer-delete"])
        editMenu.addAction(actions["layer-move-up"])
        editMenu.addAction(actions["layer-move-down"])
        editMenu.addAction(actions["layer-move-top"])
        editMenu.addAction(actions["layer-move-bottom"])
        editMenu.addAction(actions["selection-delete"])
        editMenu.addAction(actions["selection-move-up"])
        editMenu.addAction(actions["selection-move-down"])
        editMenu.addAction(actions["selection-move-top"])
        editMenu.addAction(actions["selection-move-bottom"])


        
        editMenu.addAction(actions["edit-undo"])
        editMenu.addAction(actions["edit-redo"])
        editMenu.addAction(actions["edit-copy"])
        editMenu.addAction(actions["edit-cut"])
        editMenu.addAction(actions["edit-paste"])
        menuBar.addMenu(editMenu)
        
        
        # View Menu
        viewMenu = QMenu("&View", self) 
        viewMenu.addAction(actions["view-zoom-in"])
        viewMenu.addAction(actions["view-zoom-out"])
        viewMenu.addAction(actions["view-zoom-reset"])
        viewMenu.addAction(actions["view-center-selection"])
        viewMenu.addAction(actions["view-center-origin"])


        menuBar.addMenu(viewMenu)
        
        
    def _unsavedScenes(self):
        dirtyScenes = []
        for s in  self.sceneGroup.sceneList():
            if not s.undoStack().isClean():
                dirtyScenes.append(s)
        return dirtyScenes
        
    
    def closeEvent(self, event):
        dirtyCount = len(self._unsavedScenes())  
        if dirtyCount:
            msgText = [ 
                       "There",
                       "are" if dirtyCount > 1 else "is ",
                       str(dirtyCount),
                       "unsaved",
                       "scenes." if dirtyCount > 1 else "scene.",
                       "Quit anyway?"
                       ]
            
            result = QMessageBox.question(self, "Quit SGGLE", " ".join(msgText),
                                            QMessageBox.Discard | QMessageBox.Cancel, 
                                            QMessageBox.Cancel)
            
            if result != QMessageBox.Discard:
                event.ignore()
        else:
            event.accept()



        
    