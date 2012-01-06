'''
Created on Dec 29, 2011

@author: vitali
'''


from .. interfaces import IParser 
from .. interfaces import IDumper 
from .. interfaces import INodeAdapter
from .. interfaces import INodeTreeBuilder


def parser():
    return JsonParser()

def dumper():
    return JsonDumper()

def builder():
    return JsonTreeBuilder()

def adapter(element, contentRoot = None):
    return JsonItemAdapter(element, contentRoot)




class JsonParser(IParser):
    pass


class JsonDumper(IDumper):
    pass


class JsonItemAdapter(INodeAdapter):
        
    def __init__(self, jsonElement):
        INodeAdapter.__init__(self)
        
        self._element = jsonElement
        
    def typeName(self):
        return self._element["typeName"]
    
    def properties(self):
        return self._element["properties"].items() #FIXME: DES
    
    def childItems(self):
        return [ JsonItemAdapter(child) for child in self._element["children"] ]


class JsonTreeBuilder(INodeTreeBuilder):
    pass