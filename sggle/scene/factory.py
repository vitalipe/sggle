'''
Created on Dec 30, 2011

@author: vitali
'''

from scenegroup import SceneGroup
from scene      import EditableScene 

from PySide.QtGui  import QGraphicsScene
from PySide.QtGui   import QUndoGroup




def newWelcomeScreenScene():
    scene = QGraphicsScene()
    scene.addText("Welcome :)")
    return scene


def newEmptyGraphicsScene():
    scene = EditableScene()
    scene.setSceneRect(-5000,-5000,10000,10000) 
    return scene


def newSceneGroup(parent):
    undoGroup = QUndoGroup()
    sceneGroup = SceneGroup(undoGroup)
    sceneGroup.setParent(parent)
    
    return sceneGroup