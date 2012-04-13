from PySide.QtGui  import QGraphicsScene 
from PySide.QtSvg  import QGraphicsSvgItem
from PySide.QtCore  import Qt



def newWelcomeScreenScene(): #FIXME: WTF?! this should go to ui/widgets
    scene = QGraphicsScene()
    
    newSceneItem = WelcomeScreenButton(":/icons/scene-new.svg")
    scene.addItem(newSceneItem)

    newSceneItem.scale(3,3)
    newSceneItem.setX(0)
    newSceneItem.setY(0)



    openSceneItem = WelcomeScreenButton(":/icons/scene-open.svg")
    scene.addItem(openSceneItem)
    
    openSceneItem.scale(3,3)
    openSceneItem.setX(300)
    openSceneItem.setY(0)
    
    
    return scene



class WelcomeScreenButton(QGraphicsSvgItem):
    
    def __init__(self, svgFile):
        QGraphicsSvgItem.__init__(self,svgFile)
        
        center = self.boundingRect().center()
        self.setTransformOriginPoint(center.x() , center.y())   
        self.setAcceptHoverEvents(True)
    
        
    def hoverEnterEvent(self, event):
        self.setRotation(10)
        self.setCursor(Qt.PointingHandCursor)
    
    
    def hoverLeaveEvent(self, event):
        self.setRotation(0)
        self.setCursor(Qt.ArrowCursor)

    
    
    
    