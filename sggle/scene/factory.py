'''
Created on Dec 30, 2011

@author: vitali
'''

from scenegroup import SceneGroup
from scene      import EditableScene 
import items

from PySide.QtGui   import QGraphicsScene
from PySide.QtGui   import QUndoGroup
from PySide.QtGui   import QUndoStack

# TODO: merge this module with scene and scenegroup


def newWelcomeScreenScene(): #FIXME: WTF?! this should go to ui/widgets
    scene = QGraphicsScene()
    scene.addText("Welcome ;-)")
    return scene


def newEmptyGraphicsScene():
    scene = EditableScene(QUndoStack())
    scene.setRootItem(items.newRootItem())
    scene.setSceneRect(-50000,-50000,100000,100000) # Huge hard-coded size until I have good 
                                                    # enough reason to change this.
    return scene


def newSceneGroup(parent):
    sceneGroup = SceneGroup(QUndoGroup())
    sceneGroup.setParent(parent)
    
    return sceneGroup