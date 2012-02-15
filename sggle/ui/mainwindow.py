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
from PySide.QtGui import QPixmap



import widgets
import controllers

import sggle.scene as scene
from sggle import __version__

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
        
        self.setWindowTitle("SGGLE  v" +  __version__)
        self.setWindowState(Qt.WindowMaximized)
        
        self.setDockOptions(self.AnimatedDocks | self.AllowTabbedDocks | self.VerticalTabs)
        self.setDockNestingEnabled(True)
        
        self._createControllers()
        self._createActions()
        self._createWidgets()
        self._createMenuBars()
        self._createToolBars()        
 
 
    def _createToolBars(self):
        
        fileToolBar = QToolBar("File", self)
        fileToolBar.addAction(self.actions["resource-folder-add"])
        fileToolBar.addSeparator()
        fileToolBar.addAction(self.actions["scene-new"])
        fileToolBar.addAction(self.actions["scene-open"])
        fileToolBar.addAction(self.actions["scene-save"])

        
        editToolBar = QToolBar("Edit", self)
        editToolBar.addAction(self.actions["edit-undo"])
        editToolBar.addAction(self.actions["edit-redo"])
        editToolBar.addSeparator()
        editToolBar.addAction(self.actions["edit-cut"])
        editToolBar.addAction(self.actions["edit-copy"])
        editToolBar.addAction(self.actions["edit-paste"])

        viewToolBar = QToolBar("View", self)
        viewToolBar.addAction(self.actions["view-zoom-in"])
        viewToolBar.addAction(self.actions["view-zoom-reset"])
        viewToolBar.addAction(self.actions["view-zoom-out"])
        viewToolBar.addSeparator()
        viewToolBar.addAction(self.actions["view-center-origin"])
        viewToolBar.addAction(self.actions["view-center-selection"])
        
        self.addToolBar(fileToolBar)
        self.addToolBar(editToolBar)
        self.addToolBar(viewToolBar)

 
    def _createControllers(self):
        
        self.fileController  =  controllers.FileController(self.sceneGroup, self)
        self.itemsController =  controllers.ItemsController(self.sceneGroup)
        self.viewController  =  controllers.ViewController(self.sceneGroup, 
                                                           scene.newWelcomeScreenScene())

        
    def _scene(self):
        return self.sceneGroup.activeScene()
    
    
    def addAction(self, name, callback, trigger, displayName = None, 
                  disabled = True, reverseTrigger = False):
        
        displayName = displayName if displayName else name
        action      = QAction(displayName, self)
        
        action.setDisabled(disabled)
        
        if callback: action.triggered.connect(callback)
        if trigger:  trigger.connect(action.setEnabled if not reverseTrigger else action.setDisabled)
                
        self.actions[name] = action
    
        
    def addCheckableAction(self, name, callback, enableTrigger, checkTrigger, displayName = None,
                           disabled = True, reverseTrigger = False, checked = False):
        
        displayName    = displayName if displayName else name
        action         = QAction(displayName, self)
        enableCallback = action.setEnabled if not reverseTrigger else action.setDisabled
        
        action.setDisabled(disabled)
        action.setCheckable(True)
        action.setChecked(checked)
        
        if callback:       action.triggered.connect(lambda : callback(action.isChecked()))
        if enableTrigger:  enableTrigger.connect(enableCallback)        
        if checkTrigger:   checkTrigger.connect(action.setChecked)
        
        self.actions[name] = action

        
    def _createActions(self):
       
        sceneGroup      = self.sceneGroup
        fileController  = self.fileController
        itemsController = self.itemsController
        viewController  = self.viewController

       
        self.addAction("layer-new", 
                       itemsController.addNewLayer, 
                       itemsController.canAddNewLayerChanged, # check for scene
                       "&Add New Layer")             
             
        self.addAction("layer-delete", 
                       itemsController.deleteActiveLayer, 
                       itemsController.canDeleteActiveLayerChanged, 
                       "&Delete Active Layer")        
        
        self.addAction("layer-move-up", 
                       itemsController.moveLayerUp,
                       itemsController.canMoveLayerUpChanged,
                       "Move Up Layer")        
        
        self.addAction("layer-move-down", 
                       itemsController.moveLayerDown,
                       itemsController.canMoveLayerDownChanged,
                       "Move Down Layer")        
        
        self.addAction("layer-move-top", 
                       itemsController.moveLayerToTop,
                       itemsController.canMoveLayerUpChanged,
                       "Move Layer To Top")
        
        
        self.addAction("layer-move-bottom", 
                       itemsController.moveLayerToBottom,
                       itemsController.canMoveLayerDownChanged,
                       "Move Layer To Bottom")
        
        self.addAction("selection-delete", 
                       itemsController.deleteSelectedItems,
                       itemsController.canDeleteItemSelectionChanged,
                       "Delete &Selection") 
        
        self.addAction("selection-move-up", 
                       itemsController.moveItemSelectionUp,
                       itemsController.canMoveSelectionUpChanged,
                       "Move Up Selection")
        
        self.addAction("selection-move-down", 
                       itemsController.moveItemSelectionDown,
                       itemsController.canMoveSelectionDownChanged,
                       "Move Down Selection")
        
        self.addAction("selection-move-top", 
                       itemsController.moveItemSelectionToTop,
                       itemsController.canMoveSelectionUpChanged,
                       "Move Selection To Top")

        self.addAction("selection-move-bottom", 
                       itemsController.moveItemSelectionToBottom,
                       itemsController.canMoveSelectionDownChanged,
                       "Move Selection To Bottom")
        
        
        self.addAction("edit-undo", 
                       sceneGroup.undoGroup().undo,
                       sceneGroup.undoGroup().canUndoChanged,
                       "Undo")
        
        
        self.addAction("edit-redo", 
                       sceneGroup.undoGroup().redo,
                       sceneGroup.undoGroup().canRedoChanged,
                       "Redo")
        
        
        self.addAction("edit-copy", 
                       itemsController.copyToClipboard, 
                       itemsController.canCopyChanged,
                       "&Copy")
        
        
        self.addAction("edit-cut", 
                       itemsController.cutToClipboard, 
                       itemsController.canCopyChanged,
                       "Cut")
        
        self.addAction("edit-paste", 
                       itemsController.pasteFromClipboard,
                       itemsController.canPasteChanged,
                       "&Paste")
     
     
        self.addAction("view-zoom-in", 
                       viewController.zoomIn,
                       viewController.canZoomInChanged,
                       "Zoom &In")
        
        self.addAction("view-zoom-out", 
                       viewController.zoomOut,
                       viewController.canZoomOutChanged,
                       "Zoom &Out")
                
        self.addAction("view-zoom-reset", 
                       viewController.resetZoom,
                       viewController.canResetZoomChanged,
                       "&Reset Zoom")
        
        self.addAction("view-center-selection", 
                       viewController.centerOnSelectionMaster,
                       viewController.canCenterOnSeletionMasterChanged,
                       "Goto Selection")
        
        
        self.addAction("view-center-origin", 
                       viewController.centerOnOrigin,
                       viewController.canCenterOnOriginChanged,
                       "Goto Origin")
        
        self.addCheckableAction("view-grid-show",
                                viewController.setShowGrid,
                                fileController.sceneAvailableChanged,
                                viewController.showingGridChanged,
                                "Show Grid"
                                )
        
        self.addAction("scene-new", 
                       fileController.newScene,
                       None,
                       "New Scene", 
                       disabled = False)
        
        self.addAction("scene-close", 
                       fileController.closeActiveScene,
                       fileController.sceneAvailableChanged,
                       "Close Scene")
        
        
        self.addAction("scene-save", 
                       fileController.saveActiveScene,
                       fileController.cleanStateChanged,
                       "Save Scene",
                       reverseTrigger = True)
        
        self.addAction("scene-save-as", 
                       fileController.saveActiveSceneAs,
                       fileController.sceneAvailableChanged,
                       "Save Scene As")
        
        self.addAction("scene-open", 
                       fileController.openScene,
                       None, 
                       "Open Scene", 
                       disabled = False)
        
        self.addAction("app-quit", 
                       self.close,
                       None, 
                       "Quit", 
                       disabled = False)
        
        self.addAction("resource-folder-add", 
                       fileController.openResourceFolder,
                       None, 
                       "Open Content Folder", 
                       disabled = False)
        
        self.addAction("help-about", 
                       self.aboutDialog,
                       None, 
                       "About", 
                       disabled = False)
         
        # load icons
        for actionName, action in self.actions.items():
            action.setIcon(QIcon(":/icons/actions/" + actionName))
            action.setIconVisibleInMenu(True)


    def _createWidgets(self):
        
        sceneGroup  = self.sceneGroup
        actions     = self.actions
        
        self._sceneView      = widgets.newGraphicsView()
        self._workspace      = widgets.newWorkspace(self._sceneView, self.fileController)
 
        self.viewController.setView(self._sceneView)
        self.setCentralWidget(self._workspace)

        
        # Layer list
        layersDock = widgets.newToolbarDockWidget((
                                                   (actions["layer-new"],
                                                    actions["layer-delete"],
                                                    None, # separator
                                                    actions["layer-move-top"],
                                                    actions["layer-move-up"],
                                                    actions["layer-move-down"],
                                                    actions["layer-move-bottom"])))
        widgets.newLayerList(sceneGroup.layerListModel(), layersDock)  
        self.addDockWidget(Qt.LeftDockWidgetArea, layersDock)
        
        # Item tree 
        itemsDock = widgets.newToolbarDockWidget((
                                                   (actions["selection-delete"],
                                                    None, # separator
                                                    actions["selection-move-top"],
                                                    actions["selection-move-up"],
                                                    actions["selection-move-down"],
                                                    actions["selection-move-bottom"])))
        widgets.newItemTree(sceneGroup.activeItemsTreeModel(), itemsDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, itemsDock)
        
        #Properties Editor 
        PropertiesDock = widgets.newPropertiesEditor(sceneGroup.itemPropertiesModel(), QDockWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, PropertiesDock)
        

    def _createMenuBars(self):
        assert self.actions
        
        menuBar = self.menuBar()
        actions = self.actions
        
        # File Menu
        fileMenu =  QMenu("&File", self)
        fileMenu.addAction(actions["scene-new"])
        fileMenu.addAction(actions["scene-open"])
        fileMenu.addSeparator()
        fileMenu.addAction(actions["resource-folder-add"])
        fileMenu.addSeparator()
        fileMenu.addAction(actions["scene-save"])
        fileMenu.addAction(actions["scene-save-as"])
        fileMenu.addSeparator()
        fileMenu.addAction(actions["scene-close"])
        fileMenu.addAction(actions["app-quit"])
            
        # Edit Menu
        editMenu = QMenu("&Edit", self) 
        editMenu.addAction(actions["edit-undo"])
        editMenu.addAction(actions["edit-redo"])
        editMenu.addSeparator()
        editMenu.addAction(actions["edit-copy"])
        editMenu.addAction(actions["edit-cut"])
        editMenu.addAction(actions["edit-paste"])

        # Layer menu
        layerMenu = QMenu("&Layer", self)
        layerMenu.addAction(actions["layer-new"])
        layerMenu.addAction(actions["layer-delete"])
        layerMenu.addSeparator()
        layerMenu.addAction(actions["layer-move-up"])
        layerMenu.addAction(actions["layer-move-down"])
        layerMenu.addAction(actions["layer-move-top"])
        layerMenu.addAction(actions["layer-move-bottom"])
        
        # Selection menu
        selectionMenu = QMenu("&Seletion", self)
        selectionMenu.addAction(actions["selection-delete"])
        selectionMenu.addSeparator()
        selectionMenu.addAction(actions["selection-move-up"])
        selectionMenu.addAction(actions["selection-move-down"])
        selectionMenu.addAction(actions["selection-move-top"])
        selectionMenu.addAction(actions["selection-move-bottom"])
        
        # View Menu
        viewMenu = QMenu("&View", self) 
        viewMenu.addAction(actions["view-zoom-in"])
        viewMenu.addAction(actions["view-zoom-out"])
        viewMenu.addAction(actions["view-zoom-reset"])
        viewMenu.addSeparator()
        viewMenu.addAction(actions["view-center-selection"])
        viewMenu.addAction(actions["view-center-origin"])
        viewMenu.addSeparator()
        viewMenu.addAction(actions["view-grid-show"])


        # Help menu
        helpMenu = QMenu("&Help", self) 
        helpMenu.addAction(actions["help-about"])



        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(layerMenu)
        menuBar.addMenu(selectionMenu)
        menuBar.addMenu(viewMenu)
        menuBar.addMenu(helpMenu)

        
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
            
            
    def addDockedReourceViewer(self, path):        
        resourcesDock = widgets.newResourceFolderViewer(path, QDockWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, resourcesDock)
        resourcesDock.setFloating(True)


    def aboutDialog(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("About")
        dialog.setWindowIcon(self.actions["help-about"].icon())
        dialog.setIconPixmap(QPixmap(":icons/about"))
        dialog.setText("SGGLE [" +  __version__  + "]")
        dialog.setStandardButtons(QMessageBox.Close)
        dialog.exec_()
        


        
    