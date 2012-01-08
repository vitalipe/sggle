'''
Created on Dec 29, 2011

@author: vitali
'''

import os

from PySide.QtCore import QRegExp

from PySide.QtGui  import QValidator 
from PySide.QtGui  import QIntValidator 
from PySide.QtGui  import QDoubleValidator 
from PySide.QtGui  import QRegExpValidator


#FIXME: change to TypeValidator with str(input)
class AcceptValidator(QValidator):
    
    def validate(self, input, pos):
        return QValidator.Acceptable




class DirPathValidator(QValidator):
    
    def validate(self, input, pos):
        
        if os.path.isdir(input):
            return QValidator.Acceptable
        if os.path.isdir(input.rsplit(os.path.sep,1)[0]): # The parent looks ok.
            return QValidator.Intermediate
        
        return QValidator.Invalid
    
    
    
    
class FloatValadator(QDoubleValidator):
    
    def validate(self, input, pos):
        return QDoubleValidator.validate(self, input, pos)




class IntValadator(QIntValidator):
    
    def validate(self, input, pos):
        return QIntValidator.validate(self, input, pos)




#TODO: add flexup metod
class NameValidator(QRegExpValidator):
    
    def __init__(self):
        QRegExpValidator.__init__(self, QRegExp("[a-z,A-Z,_]+[a-z,0-9,_]*"), None)


  
