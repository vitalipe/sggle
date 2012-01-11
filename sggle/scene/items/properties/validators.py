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


class IRawValidator(object):
    
    
    def validateRawValue(self, value):
        raise NotImplementedError()
    
    def fixupRawValue(self, value):
        raise NotImplementedError()
        
        

        
class TypeCheckValidator(QValidator, IRawValidator):
    
    def __init__(self, typeFactory=object): 
        QValidator.__init__(self)
        IRawValidator.__init__(self)        
        self._type = typeFactory
        
    
    def validate(self, input, pos):
        type = self._type
        if type is None:
            return  QValidator.Acceptable
        
        try:
            self._type(input)
            return QValidator.Acceptable

        except TypeError:
            return QValidator.Invalid

    
    def validateRawValue(self, value):
        if isinstance(value, self._type):
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
        
        
    def fixupRawValue(self, value):
        return value # Don't be tempted to convert type. It will break booleans
        


class DirPathValidator(QValidator, IRawValidator):
    
    def __init__(self):
        QValidator.__init__(self)
        IRawValidator.__init__(self)
    
    def validate(self, input, pos):
        
        if os.path.isdir(input):
            return QValidator.Acceptable
        if os.path.isdir(input.rsplit(os.path.sep,1)[0]): #  parent looks ok.
            return QValidator.Intermediate
        
        return QValidator.Invalid
    
    
    def validateRawValue(self, value):
        if self.validate(value, len(value)) != QValidator.Invalid:
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
    
    
    def fixupRawValue(self, value):
        return value
        
    
    
    
class FloatValadator(QDoubleValidator, IRawValidator):
    
    def __init__(self,*args):
        QDoubleValidator.__init__(self, *args)
        IRawValidator.__init__(self)


    def validate(self, input, pos):
        return QDoubleValidator.validate(self, input, pos)


    def validateRawValue(self, value):
        if type(value) is not float:
            return QValidator.Invalid
        min = self.bottom()
        max = self.top()
        if (min <= value <= max):
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
    
    
    def fixupRawValue(self, value):
        try:
            return float(value)
        except:
            return value


class IntValadator(QIntValidator, IRawValidator):

    def __init__(self, *args):
        QIntValidator.__init__(self, *args)
        IRawValidator.__init__(self)


    def validate(self, input, pos):
        return QIntValidator.validate(self, input, pos)


    def validateRawValue(self, value):
        if type(value) is not int:
            return QDoubleValidator.Invalid
        min = self.bottom()
        max = self.top()
        if (min <= value <= max):
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
    
    
    def fixupRawValue(self, value):
        try:
            return int(value)
        except:
            return value



class NameValidator(QRegExpValidator, IRawValidator):
    
    def __init__(self):
        QRegExpValidator.__init__(self, QRegExp("[a-z,A-Z,_]+[a-z,0-9,_]*"), None)
        IRawValidator.__init__(self)


    def fixup(self, input):
        if len(input) == 0:
            return input
        regX = self.regExp()
        if regX.exactMatch(input[0]) == False:
            input = "_" + input[1:]
            
        while regX.exactMatch(input) is False:
                m     = regX.matchedLength()
                input = input.replace(input[m], "")

        return input
    
    
    def validateRawValue(self, value):
        if self.validate(value, len(value)) != QRegExpValidator.Invalid:
            return QRegExpValidator.Acceptable
        else:
            return QRegExpValidator.Invalid
            
    
    
    def fixupRawValue(self, value):
        return self.fixup(value)
  
