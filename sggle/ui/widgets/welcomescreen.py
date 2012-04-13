from PySide.QtGui  import QGraphicsScene 





def newWelcomeScreenScene(): #FIXME: WTF?! this should go to ui/widgets
    scene = QGraphicsScene()
    scene.addText("Welcome ;-)")
    return scene