
from PySide.QtGui import QMessageBox
from PySide.QtGui import QPixmap
from PySide.QtGui import QIcon


from sggle import __version__





def showAboutDialog():
        dialog = AboutDialogBox()
        dialog.exec_()
    
    
def showExitDialog(unsavedScenesCount):
    msgText = [ 
                "There",
                "are" if unsavedScenesCount > 1 else "is ",
                str(unsavedScenesCount),
                "unsaved",
                "scenes." if unsavedScenesCount > 1 else "scene.",
                "Quit anyway?"
              ]
    
    return QMessageBox.question(None, "Quit SGGLE", " ".join(msgText),
                                QMessageBox.Discard | QMessageBox.Cancel, 
                                QMessageBox.Cancel)

    

    
class Response(object):
    
    Cancel  = QMessageBox.Cancel
    Discard = QMessageBox.Discard
    
    
    
    
class AboutDialogBox(QMessageBox):
    
    def __init__(self):
        super(AboutDialogBox, self).__init__()
        
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(":icons/about"))
        self.setIconPixmap(QPixmap(":icons/about"))
        self.setText("SGGLE [" +  __version__  + "]")
        self.setStandardButtons(QMessageBox.Close)
        
        
        
        