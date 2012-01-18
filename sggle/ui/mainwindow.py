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
        toolBar.addAction(self.actions["new"])
        toolBar.addAction(self.actions["save"])
        toolBar.addAction(self.actions["open"])
        
        self.addToolBar(toolBar)
        
 
    def _createControllers(self):
        
        self.editController  =  controllers.SceneEditController(self.sceneGroup)
        self.fileController  =  controllers.FileController(self.sceneGroup)
        self.itemsController =  controllers.ItemsController(self.sceneGroup)
        self.viewController  =  controllers.ViewController(self.sceneGroup, 
                                                           scene.newWelcomeScreenScene())

        
    def _scene(self):
        return self.sceneGroup.activeScene()
    
    
    def _createActions(self):
       
        sceneGroup      = self.sceneGroup
        editController  = self.editController
        fileController  = self.fileController
        itemsController = self.itemsController
        viewController  = self.viewController

       
       
        # New Layer
        addLayerAction = QAction("&Add New Layer", self)
        addLayerAction.triggered.connect(editController.addNewLayer)
        addLayerAction.setDisabled(True)
        callback = lambda n,o: addLayerAction.setEnabled(True if n  else False)
        sceneGroup.activeSceneChanged.connect(callback)
        self.actions["newLayer"] = addLayerAction
        
        
        # Delete Layer
        deleteLayerAction = QAction("&Delete Active Layer", self)
        deleteLayerAction.triggered.connect(editController.deleteActiveLayer)
        deleteLayerAction.setDisabled(True)
        callback = lambda n: deleteLayerAction.setEnabled(True if n  else False)
        sceneGroup.activeLayerChanged.connect(callback)
        self.actions["deleteLayer"] = deleteLayerAction
        
        
        
        moveUpLayerAction = QAction("Move Up Layer", self)
        moveUpLayerAction.triggered.connect(itemsController.moveLayerUp)
        moveUpLayerAction.setDisabled(True)
        itemsController.canMoveLayerUpChanged.connect(moveUpLayerAction.setEnabled)
        self.actions["moveUpLayer"] =  moveUpLayerAction
        
        
        moveDownLayerAction = QAction("Move Down Layer", self)
        moveDownLayerAction.triggered.connect(itemsController.moveLayerDown)
        moveDownLayerAction.setDisabled(True)
        itemsController.canMoveLayerDownChanged.connect(moveDownLayerAction.setEnabled)
        self.actions["moveDownLayer"] =  moveDownLayerAction
        
        
        moveLayerToTopAction = QAction("Move Layer To Top", self)
        moveLayerToTopAction.triggered.connect(itemsController.moveLayerToTop)
        moveLayerToTopAction.setDisabled(True)
        itemsController.canMoveLayerUpChanged.connect(moveLayerToTopAction.setEnabled)
        self.actions["moveLayerToTop"] =  moveLayerToTopAction
        

        moveLayerToBottomAction = QAction("Move Layer To Bottom", self)
        moveLayerToBottomAction.triggered.connect(itemsController.moveLayerToBottom)
        moveLayerToBottomAction.setDisabled(True)
        itemsController.canMoveLayerDownChanged.connect(moveLayerToBottomAction.setEnabled)
        self.actions["moveLayerToBottom"] =  moveLayerToBottomAction
        
        
        # Delete Selected Items
        deleteSelectionAction = QAction("Delete &Selection", self)
        deleteSelectionAction.triggered.connect(editController.deleteSelectedItems)
        deleteSelectionAction.setDisabled(True)
        callback = lambda : deleteSelectionAction.setEnabled(True if self._scene().selectedItems()  else False)
        sceneGroup.selectionChanged.connect(callback)
        self.actions["deleteSelection"] =  deleteSelectionAction
        
        
        moveUpSelectionAction = QAction("Move Up Selection", self)
        moveUpSelectionAction.triggered.connect(itemsController.moveItemSelectionUp)
        moveUpSelectionAction.setDisabled(True) 
        itemsController.canMoveSelectionUpChanged.connect(moveUpSelectionAction.setEnabled)
        self.actions["moveUpSelection"] =   moveUpSelectionAction
        
        
        moveDownSelectionAction = QAction("Move Down Selection", self)
        moveDownSelectionAction.triggered.connect(itemsController.moveItemSelectionDown)
        moveDownSelectionAction.setDisabled(True) 
        itemsController.canMoveSelectionDownChanged.connect(moveDownSelectionAction.setEnabled)
        self.actions["moveDownSelection"] =   moveDownSelectionAction
        
        
        moveSelectionToTopAction = QAction("Move Selection To Top", self)
        moveSelectionToTopAction.triggered.connect(itemsController.moveItemSelectionToTop)
        moveSelectionToTopAction.setDisabled(True) 
        itemsController.canMoveSelectionUpChanged.connect(moveSelectionToTopAction.setEnabled)
        self.actions["moveSelectionToTop"] =   moveSelectionToTopAction
        
        
        moveSelectionToBottomAction = QAction("Move Selection To Bottom", self)
        moveSelectionToBottomAction.triggered.connect(itemsController.moveItemSelectionToBottom)
        moveSelectionToBottomAction.setDisabled(True) 
        itemsController.canMoveSelectionDownChanged.connect(moveSelectionToBottomAction.setEnabled)
        self.actions["moveSelectionToBottom"] =   moveSelectionToBottomAction
        
        
        
        # Redo 
        redoAction = sceneGroup.undoGroup().createRedoAction(self)
        self.actions["redo"] =  redoAction
        
        
        # Undo
        undoAction = sceneGroup.undoGroup().createUndoAction(self)
        self.actions["undo"] =  undoAction
 
 
        # copy
        copyAction = QAction("&Copy", self)
        copyAction.triggered.connect(editController.copySelectionToClipboard)
        copyAction.setDisabled(True)
        callback = lambda : copyAction.setEnabled(True if self._scene().selectedItems()  else False)
        sceneGroup.selectionChanged.connect(callback)
        self.actions["copy"] =  copyAction
        
        # cut
        cutAction = QAction("&Cut", self)
        cutAction.triggered.connect(editController.cutSelectionToClipboard)
        cutAction.setDisabled(True)
        callback = lambda : cutAction.setEnabled(True if self._scene().selectedItems()  else False)
        sceneGroup.selectionChanged.connect(callback)
        self.actions["cut"] =  cutAction        
        
        # paste
        pasteAction = QAction("&Paste", self)
        pasteAction.triggered.connect(editController.pasteFromClipboard)
        pasteAction.setDisabled(True)
        editController.clipboardDataAvailableChanged.connect(pasteAction.setEnabled)
        self.actions["paste"] =  pasteAction

        # ZoomIn
        zoomInAction = QAction("Zoom &In", self)
        zoomInAction.triggered.connect(viewController.zoomIn)
        zoomInAction.setDisabled(True)
        viewController.canZoomInChanged.connect(zoomInAction.setEnabled)
        self.actions["zoomIn"] =  zoomInAction
        
        # ZoomOut
        zoomOutAction = QAction("Zoom &Out", self)
        zoomOutAction.triggered.connect(viewController.zoomOut)
        zoomOutAction.setDisabled(True)
        viewController.canZoomOutChanged.connect(zoomOutAction.setEnabled)
        self.actions["zoomOut"] =  zoomOutAction

        # Reset Zoom
        resetZoomAction = QAction("&Reset Zoom", self)
        resetZoomAction.triggered.connect(viewController.resetZoom)
        resetZoomAction.setDisabled(True)
        viewController.zoomChanged.connect(lambda z: resetZoomAction.setEnabled(True if z != 100 else False))
        self.actions["resetZoom"] =  resetZoomAction
        
        
        # Center On Selection
        centerSelecetionAction = QAction("Center On Selection", self)
        centerSelecetionAction.triggered.connect(viewController.centerOnSelectionMaster)
        centerSelecetionAction.setDisabled(True)
        callback = lambda: centerSelecetionAction.setEnabled(True if self._scene().selectedItems()  else False)
        sceneGroup.selectionChanged.connect(callback)
        self.actions["centerSelecetion"] =  centerSelecetionAction
        
        # Center on Origin
        centerOriginAction = QAction("Center On Origin", self)
        centerOriginAction.triggered.connect(viewController.centerOnOrigin)
        centerOriginAction.setDisabled(True)
        sceneGroup.activeSceneChanged.connect(lambda n: centerOriginAction.setEnabled(True if n else False))
        self.actions["centerOrigin"] =  centerOriginAction

  
        # New
        newAction = QAction("&New", self)
        newAction.triggered.connect(fileController.new)
        newAction.setIcon(QIcon(":/icons/new"))
        self.actions["new"] = newAction
        
        # Save
        saveAction = QAction("&Save", self)
        saveAction.setIcon(QIcon(":/icons/save"))
        saveAction.triggered.connect(fileController.saveActiveScene)
        self.actions["save"] = saveAction
        
        # Save As
        saveAction = QAction("&Save As", self)
        saveAction.setIcon(QIcon(":/icons/saveas"))
        saveAction.triggered.connect(fileController.saveActiveSceneAs)
        self.actions["saveAs"] = saveAction
        
        # Open
        openAction = QAction("&Open", self)
        openAction.setIcon(QIcon(":/icons/open"))
        openAction.triggered.connect(fileController.openScene)
        self.actions["open"] = openAction
        
        
        
        # Quit
        quitAction = QAction("&Quit", self)
        quitAction.triggered.connect(self.close)
        self.actions["quit"] = quitAction
 
 
 
        # keys:
        addLayerAction.setShortcut(ActionKeySequences.addNewLayerSeqence)
        deleteLayerAction.setShortcut(ActionKeySequences.deleteActiveLayerSeqence)
        deleteSelectionAction.setShortcut(ActionKeySequences.deleteSelectedItemsSeqence)
        redoAction.setShortcut(ActionKeySequences.redoSequence)
        undoAction.setShortcut(ActionKeySequences.undoSequence)
        newAction.setShortcut(ActionKeySequences.newSequence)
        copyAction.setShortcut(ActionKeySequences.copySequence)
        cutAction.setShortcut(ActionKeySequences.cutSequence)
        pasteAction.setShortcut(ActionKeySequences.pasteSequence)
        
        zoomInAction.setShortcut(ActionKeySequences.zoomInSequence)
        zoomOutAction.setShortcut(ActionKeySequences.zoomOutSequence)
        centerSelecetionAction.setShortcut(ActionKeySequences.centerSelecetionSequence)


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
        fileMenu.addAction(actions["new"])
        fileMenu.addAction(actions["save"])
        fileMenu.addAction(actions["saveAs"])
        fileMenu.addAction(actions["open"])
        fileMenu.addAction(actions["quit"])
        menuBar.addMenu(fileMenu)


            
        # Edit Menu
        editMenu = QMenu("&Edit", self) 
        editMenu.addAction(actions["newLayer"])
        editMenu.addAction(actions["deleteLayer"])
        editMenu.addAction(actions["moveUpLayer"])
        editMenu.addAction(actions["moveDownLayer"])
        editMenu.addAction(actions["moveLayerToTop"])
        editMenu.addAction(actions["moveLayerToBottom"])
        editMenu.addAction(actions["deleteSelection"])
        editMenu.addAction(actions["moveUpSelection"])
        editMenu.addAction(actions["moveDownSelection"])
        editMenu.addAction(actions["moveSelectionToTop"])
        editMenu.addAction(actions["moveSelectionToBottom"])


        
        editMenu.addAction(actions["redo"])
        editMenu.addAction(actions["undo"])
        editMenu.addAction(actions["copy"])
        editMenu.addAction(actions["cut"])
        editMenu.addAction(actions["paste"])
        menuBar.addMenu(editMenu)
        
        
        # View Menu
        viewMenu = QMenu("&View", self) 
        viewMenu.addAction(actions["zoomIn"])
        viewMenu.addAction(actions["zoomOut"])
        viewMenu.addAction(actions["resetZoom"])
        viewMenu.addAction(actions["centerSelecetion"])
        viewMenu.addAction(actions["centerOrigin"])


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



        
    