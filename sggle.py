#!/usr/bin/env python


from sys           import argv
from PySide.QtGui  import QApplication

from sggle.ui.mainwindow import MainWindow
from sggle import __version__

def main():
    
    app         =  QApplication(argv)
    mainWindow  =  MainWindow("SGGLE  v" +  __version__)

    
    mainWindow.show()    
    app.exec_()


if __name__ == '__main__': main()