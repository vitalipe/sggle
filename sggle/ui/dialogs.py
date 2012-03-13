
from os.path import expanduser
from os.path import splitext

from PySide.QtGui import QMessageBox
from PySide.QtGui import QFileDialog
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

    
def showCloseSceneDialog(sceneName):
        return QMessageBox.question(None, "Close " + sceneName,
                                    "Save changes before closing?", 
                                    QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel,
                                    QMessageBox.Cancel)
    
    
def showSaveSceneAsDialog(fileTypes):
        global _lastSaveLocation
        
        filters   = ";;".join([ f + " (*." + f + ")" for f in fileTypes])
        result    = QFileDialog.getSaveFileName(None, "Save Scene As", _lastSaveLocation, filters)
        
        if not result[0]: # canceled by user
            return ["",""]
        else:
            fileName       = result[0]
            chosenFileType = (result[1].split())[0]
          
        # append extension only if necessary
        if splitext(fileName)[1].strip(".") not in fileTypes:   
            fileName += ("." + chosenFileType) 
        
        _lastSaveLocation = fileName
        return [fileName, chosenFileType]


def showOpenSceneDialog(fileTypes):
    global _lastLoadLocation

    filters  = " ".join([ "*." + f for f in fileTypes])
    result   = QFileDialog.getOpenFileName(None, "Open Scene", _lastLoadLocation, filters)
    fileName = result[0]
    fileType = splitext(fileName)[1].strip(".")
        
    if not fileName: # canceled by user
        return ["", ""]
    else:
        _lastLoadLocation = fileName
        return [fileName, fileType]


def showErrorDialog(title, msg, exception = None):
    QMessageBox.critical(None, title, msg)


class Response(object):
    
    Cancel  = QMessageBox.Cancel
    Discard = QMessageBox.Discard
    Save    = QMessageBox.Save 
    
    
    
    
class AboutDialogBox(QMessageBox):
    
    def __init__(self):
        super(AboutDialogBox, self).__init__()
        
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(":icons/about"))
        self.setIconPixmap(QPixmap(":icons/about"))
        self.setText("SGGLE [" +  __version__  + "]")
        self.setStandardButtons(QMessageBox.Close)
        
        


_lastSaveLocation = expanduser("~")
_lastLoadLocation = expanduser("~")

