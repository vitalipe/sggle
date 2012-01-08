'''
Created on Nov 30, 2011

@author: vitali
'''
import formats.scene


def writeScene(sceneObject, fileStream, formatName):
    assert isinstance(fileStream, file)
    assert formatName in formats.knowFileFormats()
    
    format = formats.fromName(formatName)
    
    builder  = format.builder()
    dumper   = format.dumper()
    
    treeRoot = buildTree(formats.scene.ItemAdapter(sceneObject.rootItem()), builder)
    dumper.dump(treeRoot, fileStream)
    
    

def readScene(aFile, formatName):
    assert isinstance(aFile, file)
    assert isinstance(formatName, str)

    format = formats.fromName(formatName)

    parser   = format.parser()
    adapterFactory  = format.adapter

    treeRoot = parser.parse(aFile)
    return buildTree(adapterFactory(treeRoot), formats.scene.SceneTreeBuilder())




def buildTree(rootItem, treeBuilder):
    _buildTree(rootItem, treeBuilder)
    return treeBuilder.build()


def _buildTree(item, treeBuilder):
    if item is None:
        return
    
    treeBuilder.startNode(item.typeName())
    for key, value in item.properties():
        treeBuilder.addProperty(key, value)
    for child in item.childItems():
        _buildTree(child, treeBuilder)
    treeBuilder.closeNode()


    
  
    
        