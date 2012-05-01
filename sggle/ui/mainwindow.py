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
import dialogs

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
        self.resourceDockWidgets = []
        
        self.setWindowTitle("SGGLE")
        self.setWindowState(Qt.WindowMaximized)
        
        self.setDockOptions(self.AnimatedDocks | self.AllowTabbedDocks | self.VerticalTabs)
        self.setDockNestingEnabled(True)
        
        self._createControllers()
        self._createActions()
        self._createWidgets()
        self._createMenuBars()
        self._createToolBars()
        self._createStatusBar()
 
 
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
        viewToolBar.addWidget(widgets.newZoomWidget(self.viewController))
        viewToolBar.addAction(self.actions["view-zoom-out"])
        viewToolBar.addSeparator()
        viewToolBar.addAction(self.actions["view-center-origin"])
        viewToolBar.addAction(self.actions["view-center-selection-master"])
        
        self.addToolBar(fileToolBar)
        self.addToolBar(editToolBar)
        self.addToolBar(viewToolBar)

 
    def _createControllers(self):
        
        self.fileController  =  controllers.FileController(self.sceneGroup, self)
        self.itemsController =  controllers.ItemsController(self.sceneGroup)
        self.viewController  =  controllers.ViewController(self.sceneGroup)
        self.propertiesController = controllers.PropertiesController(self.sceneGroup)
    
    
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
       
        sceneGroup            = self.sceneGroup
        fileController        = self.fileController
        itemsController       = self.itemsController
        viewController        = self.viewController
        propertiesController  = self.propertiesController

       
        self.addAction("layer-new", 
                       itemsController.addNewLayer, 
                       itemsController.canAddNewLayerChanged,
                       "&Add New Layer")             
             
        self.addAction("layer-delete", 
                       itemsController.deleteActiveLayer, 
                       itemsController.canDeleteActiveLayerChanged, 
                       "&Delete Active Layer")        
        
        self.addAction("layer-duplicate", 
                       itemsController.duplicateActiveLayer, 
                       itemsController.canDuplicateLayerChanged,
                       "Duplicate Layer")      
        
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
        
        self.addAction("selection-select-all", 
                       itemsController.selectAll,
                       itemsController.canSelectAllChanged,
                       "Select All")
        
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
        
        self.addAction("selection-move-layer-above", 
                       itemsController.moveSelectionToLayerAbove,
                       itemsController.canMoveSelectionToLayerAboveChanged,
                       "Move Selection To Layer Above")
        
        self.addAction("selection-move-layer-below", 
                       itemsController.moveSelectionToLayerBelow,
                       itemsController.canMoveSelectionToLayerBelowChanged,
                       "Move Selection To Layer Below")
        
        self.addAction("selection-move-layer-new", 
                       itemsController.moveSelectionToNewLayer,
                       itemsController.canMoveSelectionToNewLayerChanged,
                       "Move Selection To New Layer")
        
        
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
        
        self.addAction("view-center-selection-master", 
                       viewController.centerOnSelectionMaster,
                       viewController.canCenterOnSeletionMasterChanged,
                       "Goto Active Item")
        
        self.addAction("view-center-origin", 
                       viewController.centerOnOrigin,
                       fileController.sceneAvailableChanged,
                       "Goto Origin")
        
        self.addAction("view-center-camera", 
                       viewController.centerOnCamera,
                       fileController.sceneAvailableChanged,
                       "Goto Camera")
        
        self.addCheckableAction("view-grid-show",
                                viewController.setShowGrid,
                                fileController.sceneAvailableChanged,
                                viewController.showGridChanged,
                                "Show Grid"
                                )
        
        self.addCheckableAction("view-grid-snap",
                                viewController.setSnap2Grid,
                                fileController.sceneAvailableChanged,
                                viewController.snap2GridChanged,
                                "Snap To Grid"
                                )
        
        self.addCheckableAction("view-axis-show",
                                viewController.setShowAxis,
                                fileController.sceneAvailableChanged,
                                viewController.showAxisCanged,
                                "Show Axis"
                                )
        
        self.addCheckableAction("view-camera-show",
                                viewController.setShowCamera,
                                fileController.sceneAvailableChanged,
                                viewController.showCameraCanged,
                                "Show Camera Position"
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
                       dialogs.showAboutDialog,
                       None, 
                       "About", 
                       disabled = False)
        
         
        self.addCheckableAction("property-lock",
                                propertiesController.lockSelectedProperty,
                                propertiesController.canLockPropertyChanged,
                                propertiesController.lockSelectedPropertyChanged,
                                "Lock selected property"
                                )
        
        self.addAction("property-unlock-all",
                                propertiesController.unlockAllProperties,
                                propertiesController.canUnlockAllPropertiesChanged,
                                "Unlock all properties"
                                )
        
        self.addAction("property-reset",
                                propertiesController.resetProperty,
                                propertiesController.canResetPropertyChanged,
                                "Reset property"
                                )
        
        self.addAction("property-replicate",
                                propertiesController.replicateSelectedProperty,
                                propertiesController.canReplicateSelectedPropertyChanged,
                                "Replicate property"
                                )
         
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
                                                    actions["layer-duplicate"],
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
        propertiesDock = widgets.newToolbarDockWidget((
                                                    actions["property-unlock-all"],
                                                    actions["property-lock"],
                                                    actions["property-reset"],
                                                    actions["property-replicate"],
                                                     ))
        PropertiesDock = widgets.newPropertiesEditor(sceneGroup.itemPropertiesModel(), propertiesDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, PropertiesDock)
        
        
        self.viewController.setWelcomeScene(widgets.newWelcomeScreenScene(self.actions))
         

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
        layerMenu.addAction(actions["layer-duplicate"])
        layerMenu.addAction(actions["layer-delete"])
        layerMenu.addSeparator()
        stackMenu = layerMenu.addMenu("Stack")
        stackMenu.addAction(actions["layer-move-up"])
        stackMenu.addAction(actions["layer-move-down"])
        stackMenu.addAction(actions["layer-move-top"])
        stackMenu.addAction(actions["layer-move-bottom"])
        
        # Selection menu
        selectionMenu = QMenu("&Seletion", self)
        selectionMenu.addAction(actions["selection-select-all"])
        selectionMenu.addAction(actions["selection-delete"])
        selectionMenu.addSeparator()
        selectionMenu.addAction(actions["selection-move-layer-above"])
        selectionMenu.addAction(actions["selection-move-layer-below"])
        selectionMenu.addAction(actions["selection-move-layer-new"])
        stackMenu = selectionMenu.addMenu("Stack")
        stackMenu.addAction(actions["selection-move-up"])
        stackMenu.addAction(actions["selection-move-down"])
        stackMenu.addAction(actions["selection-move-top"])
        stackMenu.addAction(actions["selection-move-bottom"])
        
        # View Menu
        viewMenu = QMenu("&View", self)
        zoomMenu = viewMenu.addMenu("Zoom") 
        zoomMenu.addAction(actions["view-zoom-in"])
        zoomMenu.addAction(actions["view-zoom-out"])
        zoomMenu.addAction(actions["view-zoom-reset"])
        gotoMenu = viewMenu.addMenu("Goto") 
        gotoMenu.addAction(actions["view-center-selection-master"])
        gotoMenu.addAction(actions["view-center-origin"])
        gotoMenu.addAction(actions["view-center-camera"])

        viewMenu.addSeparator()
        viewMenu.addAction(actions["view-grid-show"])
        viewMenu.addAction(actions["view-axis-show"])
        viewMenu.addAction(actions["view-grid-snap"])
        viewMenu.addSeparator()
        viewMenu.addAction(actions["view-camera-show"])

        # Help menu
        helpMenu = QMenu("&Help", self) 
        helpMenu.addAction(actions["help-about"])


        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(layerMenu)
        menuBar.addMenu(selectionMenu)
        menuBar.addMenu(viewMenu)
        menuBar.addMenu(helpMenu)


    def _createStatusBar(self):
        self.statusBar() # empty status bar 
        

    def closeEvent(self, event):
        if self.fileController.confirmExit():
            event.accept()
        else:
            event.ignore()

            
    def addDockedReourceViewer(self, path):   
        resourcesDock = widgets.newResourceFolderViewer(path, QDockWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, resourcesDock)
        resourcesDock.setFloating(False)
        self.resourceDockWidgets.append(resourcesDock)

        resourcesDock.visibilityChanged.connect(self.cleanupHiddenDocks)

                
    def cleanupHiddenDocks(self):
        hiddenDocks = [ dock for dock in self.resourceDockWidgets if dock.isVisible() == False ]
        for dock in hiddenDocks[:-3]: # leave the last 3 docks alone
            self.resourceDockWidgets.remove(dock)
            self.removeDockWidget(dock)
            
        
        
        


        
    