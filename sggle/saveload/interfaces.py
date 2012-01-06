'''
Created on Dec 29, 2011

@author: vitali
'''


class INodeAdapter(object):
    
    def typeName(self):
        raise NotImplementedError()
    
    def properties(self):
        raise NotImplementedError()
    
    def childItems(self):
        raise NotImplementedError()



class INodeTreeBuilder():
    
        
    def startNode(self, typeName):
        raise NotImplementedError()
    
    
    def addProperty(self, key, value):
        raise NotImplementedError()
    
    
    def closeNode(self):
        raise NotImplementedError()

    
    def build(self):
        raise NotImplementedError()



class IParser(object):
    
    def __init__(self):
        object.__init__(self)
    
    def parse(self, stream):
        raise NotImplementedError()
    


class IDumper(object):
    
    def dump(self, data, stream):
        raise NotImplementedError()



