'''
Created on Sep 30, 2011

@author: vitali
'''


from sys           import argv
from PySide.QtGui  import QApplication


from sggle.ui.mainwindow import MainWindow


def main():
    
    app         =  QApplication(argv)
    mainWindow  =  MainWindow()

    
    mainWindow.show()    
    app.exec_()


if __name__ == '__main__': main()