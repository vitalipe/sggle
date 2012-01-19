
import os
from os import path


ROOT_DIR      = path.dirname(__file__)
OUTPUT_PATH   = path.join(ROOT_DIR, "../sggle/resources/assets.py")
QRC_PATH      = path.join(ROOT_DIR, "assets.qrc")
FILE_TYPES    = [ ".png", ".svg"]


def create_qrc_file():
    header = [ "<!DOCTYPE RCC>\n", "<RCC version=\"1.0\">\n", " <qresource>\n" ]
    footer = [ " </qresource>\n", "</RCC>\n" ]
    fnames = []
    
    path.walk(ROOT_DIR, fs_walk, fnames)
    
    f = open(QRC_PATH, "w+")
    f.writelines(header + [ "     <file>" + name + "</file>\n" for name in fnames] + footer)
    f.close()

def  fs_walk(files, parent, fileList):
    parent = path.relpath(parent, ROOT_DIR)
    for fname in fileList:
        if path.splitext(fname)[1] in FILE_TYPES:
            files.append(path.join(parent, fname))
            

def create_assets_file():
    os.system("pyside-rcc " + QRC_PATH + " > " + OUTPUT_PATH)


create_qrc_file()
create_assets_file() 