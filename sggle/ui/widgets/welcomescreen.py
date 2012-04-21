from PySide.QtGui  import QGraphicsScene 
from PySide.QtSvg  import QGraphicsSvgItem
from PySide.QtCore  import Qt



def newWelcomeScreenScene(actions): 
    scene = QGraphicsScene()
    scene.setSceneRect(0,0,0,0)
    
    
    newSceneItem = WelcomeScreenButton(":/icons/scene-new.svg", actions["scene-new"])
    scene.addItem(newSceneItem)

    newSceneItem.scale(4,4)
    newSceneItem.setX(0)
    newSceneItem.setY(0)



    openSceneItem = WelcomeScreenButton(":/icons/scene-open.svg", actions["scene-open"])
    scene.addItem(openSceneItem)
    
    openSceneItem.scale(4,4)
    openSceneItem.setX(300)
    openSceneItem.setY(0)
    
#    
#    helpSceneItem = WelcomeScreenButton(":/icons/app-quit.svg")
#    scene.addItem(helpSceneItem)
#    
#    helpSceneItem.scale(2,2)
#    helpSceneItem.setX(100)
#    helpSceneItem.setY(100)
#    
    
    return scene



class WelcomeScreenButton(QGraphicsSvgItem):
    
    def __init__(self, svgFile, action):
        QGraphicsSvgItem.__init__(self,svgFile)
        
        self._action = action
        
        center = self.boundingRect().center()
        
        self.setTransformOriginPoint(center.x() , center.y())   
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
    def hoverEnterEvent(self, event):
        self.setRotation(10)
        self.setCursor(Qt.PointingHandCursor)
    
    
    def hoverLeaveEvent(self, event):
        self.setRotation(0)
        self.setCursor(Qt.ArrowCursor)


    def mousePressEvent(self, event):
        self._action.trigger()
    
    
    
    