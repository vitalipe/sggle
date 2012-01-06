'''
Created on Dec 29, 2011

@author: vitali
'''


from os.path import join    as joinPath
from os.path import relpath as relativePath


from PySide.QtCore import QPointF
from PySide.QtCore import QRectF



from .. interfaces import IParser 
from .. interfaces import IDumper 
from .. interfaces import INodeAdapter
from .. interfaces import INodeTreeBuilder

from .. import errors

import sggle.resources as resources
import xml.etree.ElementTree as xml


def parser():
    return XmlElementTreeParser()

def dumper():
    return XmlElementTreeDumper()

def builder():
    return XmlTreeBuilder()

def adapter(element, contentRoot = None):
    return XmlItemAdapter(element, contentRoot)



class XmlElementTreeParser(IParser):
    
    def __init__(self):
        IParser.__init__(self)

    
    def parse(self, stream):
        try:
            xmlTree = xml.parse(stream)
        except xml.ParseError:
            raise errors.LoadError()
        
        return xmlTree.getroot()
 

class XmlElementTreeDumper(IDumper):
    
    def __init__(self):
        IDumper.__init__(self)
  
  
    def dump(self, rootElement, stream):
        xml.ElementTree(rootElement).write(stream)




class XmlItemAdapter(INodeAdapter):

    def __init__(self, element, contentRoot = None):
        INodeAdapter.__init__(self)
        
        self._element     = element
        self._contentRoot = contentRoot
        
        if contentRoot is None: # root item
            self._initContentRoot()


    def _initContentRoot(self):
        for k,v in self.properties():
            if k == "content":
                self._contentRoot = v
                break
        else: #FIXME: warn
            self._contentRoot = ""
            
    def _containsSubElements(self, subElement, *keys):

        if len(subElement.getchildren()) != len(keys):
            return False
        
        for key in keys:
            if subElement.find(key) is None:
                return False
            
        return True
    
    
    def _deserialize(self, element, contentRoot = None):
        
        if len(element.getchildren()): 
            # QRectF
            if (self._containsSubElements(element, "x", "y","w", "h")):
                x = self._deserialize(element.find("x"))
                y = self._deserialize(element.find("y"))
                w = self._deserialize(element.find("w"))
                h = self._deserialize(element.find("h"))
                return QRectF(x,y,w,h)
            
            # QPointF
            elif (self._containsSubElements(element, "x", "y")):
                x = self._deserialize(element.find("x"))
                y = self._deserialize(element.find("y"))
                return QPointF(x,y)
             
            else:   
                raise TypeError(element)
        
        try:
            value = eval(element.text)
        except SyntaxError:
            raise TypeError(element.text)
        
        if isinstance(value, (str,unicode)) and value[0] == ":":
            path  = joinPath(contentRoot, value[1:])
            value = resources.loader.pixmap.load(path) 
            
        return value
       
    def typeName(self):
        return self._element.tag
    
    
    def properties(self):
        propertyElements = self._element.find("properties")
        
        properties = {}
        for element in propertyElements:
            properties[element.tag] = self._deserialize(element, self._contentRoot)
                
        return properties.items()
    
    
    def childItems(self):
        childrenRoot = self._element.find("children")
        contentRoot  = self._contentRoot
        if childrenRoot is not None:
            return [ XmlItemAdapter(child, contentRoot) for child in childrenRoot.getchildren() ]
        else:
            return []




class XmlTreeBuilder(INodeTreeBuilder):
    
      
    def __init__(self):
        
        self._root  = None
        self._stack = [] 
        self._contentRoot = None
 
        
    def _srerialize(self, key, value, contentRoot = None):
        element = xml.Element(key)
  
        if isinstance(value, QPointF):
            for k,v in [ ("x",value.x()), ("y",value.y()) ]:
                element.append(self._srerialize(k, v))
                
        elif isinstance(value, resources.resource.PixmapResource):
            element.text = '"' + ":" + relativePath(value.path(),contentRoot) + '"'
            
        elif isinstance(value, QRectF):
            for k,v in [ ("x",value.x()), ("y",value.y()), 
                        ("w",value.width()), ("h", value.height()) ]:
                element.append(self._srerialize(k, v))
            
        else:
            if isinstance(value, (str, unicode)): 
                element.text = ('"' + value + '"')  # extra quotes for eval()
            else:
                element.text = str(value)
                    
        return element
        
        
    def _current(self):
        return self._stack[-1] if self._stack else None
    
    
    def _newItemElement(self, typeName):
        element      = xml.Element(typeName)
        eProperties  = xml.Element("properties")
        eChildren    = xml.Element("children")
        
        element.append(eProperties)
        element.append(eChildren)
        element.childern     = eChildren
        element.properties = eProperties
        
        return element

        
    def startNode(self, typeName):
        assert not self._root
        element = self._newItemElement(typeName)

        if self._current() is not None:
            self._current().childern.append(element)
        self._stack.append(element)
    
    
    def addProperty(self, key, value):
        if key == "content" and len(self._stack) == 1:
            self._contentRoot = value
            
        self._current().properties.append(self._srerialize(key, value, self._contentRoot))
    
    
    def closeNode(self):
        assert self._stack
        
        element = self._stack.pop(-1)
        if not self._stack:
            self._root = element

    
    def build(self):
        assert self._root is not None
        assert not self._stack
        
        root = self._root
        self._root = None
        
        return root
