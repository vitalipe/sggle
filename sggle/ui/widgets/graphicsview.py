'''
Created on Jan 5, 2012

@author: vitali
'''

from PySide.QtGui  import QGraphicsView
from PySide.QtGui  import QPainter




    
def newGraphicsView(): #FIXME: check for openGL support
    view = GraphicsSceneView()   
    #view.setViewport(QGLWidget()) #FIXME: HACK openGL is currently broken on my machine :( 
      
    return view



class GraphicsSceneView(QGraphicsView):
    
    def __init__(self):
        QGraphicsView.__init__(self)
        
        self.setMouseTracking(True) # Send mouse events to scene
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self._zoom     = 100
        self._hasMouse = False
        
        
    def scrollContentsBy(self, dx, dy):
        QGraphicsView.scrollContentsBy(self, dx, dy)
        if hasattr(self.scene(), "adjustParallax"):
            self.scene().adjustParallax(self.center())
        
        
    def zoomPercentage(self):
        return self._zoom
  
              
    def setZoomPercentage(self, percentage):  
        assert percentage > 0
              
        if percentage == self.zoomPercentage():
            return
        
        # set
        newScale = float(percentage) / 100.0
        scale    = 1/(float(self.zoomPercentage()) / 100.0)
        self.scale(scale, scale)
        self.scale(newScale, newScale)
        
        # save
        self._zoom = percentage


    def center(self):
        return self.mapToScene(self.viewport().rect()).boundingRect().center()


    def hasMouse(self):
        return self._hasMouse
    
    
    def enterEvent(self, event):
        self._hasMouse = True
        return super(GraphicsSceneView, self).enterEvent(event)
        
        
    def leaveEvent(self, event):
        self._hasMouse = False
        return super(GraphicsSceneView, self).leaveEvent(event)
