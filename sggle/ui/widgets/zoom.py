from PySide.QtGui import QComboBox
from PySide.QtGui import QWidget
from PySide.QtGui import QValidator
from PySide.QtGui import QIntValidator
from PySide.QtGui import QHBoxLayout




def newZoomWidget(viewController):
    
    minZoom = viewController.minZoom()
    maxZoom =  viewController.maxZoom()
    step    = viewController.zoomStep() * 5
    
    items = [str(minZoom) + "%"]
    for i in range(step,maxZoom,step):
        items.append(str(i) + "%")
    items.append(str(maxZoom) + "%")

    widget = ZoomWidget(viewController, items)
    
    widget.setEnabled(False)
    widget.setValidator(ZoomValidator(minZoom, maxZoom))
    
    return widget   




class ZoomValidator(QIntValidator):
    
    def __init__(self, minZoom, maxZoom):
        super(ZoomValidator, self).__init__(minZoom, maxZoom, None)
        
        
    def validate(self, text, pos):        
        if text[-1] == "%":
            r = super(ZoomValidator, self).validate(text[:-1], pos-1)
            return (r[0], text, pos)
        else:
            r = super(ZoomValidator, self).validate(text, pos)
            if r[0] == ZoomValidator.Acceptable:
                return (r[0], text + "%",pos+1)
            else:
                return r


    
    
class ZoomWidget(QComboBox):
    
    
    def __init__(self, viewController, items):
        super(ZoomWidget, self).__init__()
        
        self._viewController = viewController
        self.addItems(items)
        
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
        self.insertSeparator(0)
        self.setInsertPolicy(QComboBox.InsertAtTop)
    
        viewController.zoomChanged.connect(self._handleZoomChanged)
        viewController.canZoomInChanged.connect(self._handleEnableDisable)
        
        self.currentIndexChanged.connect(self._updateController)
        
        
    def _handleZoomChanged(self, newZoom, oldZoom):
        self.setEditText(str(newZoom) + "%")
        
        
    def _handleEnableDisable(self, canZoomInOrOutTrigger):
        if canZoomInOrOutTrigger:
            self.setEnabled(True)
        else:
            self.setEnabled(self._viewController.canChangeZoom())
            
    
    def _updateController(self, index):
        # Workaround for PySide bug: (http://bugs.pyside.org/show_bug.cgi?id=967)
        index = self.currentIndex() 
        
        zoom =  self.itemText(index)
        if zoom[-1] == "%":
            zoom = zoom[:-1]
        
        self._viewController.setZoomPercentage(int(zoom))
        
        
