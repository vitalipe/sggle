'''
Created on Nov 30, 2011

@author: vitali
'''
import formats.scene


def writeScene(sceneObject, fileStream, formatName):
    assert isinstance(fileStream, file)
    assert formatName in formats.knowFileFormats()
    
    fileFormat = formats.fromName(formatName)
    
    builder  = fileFormat.builder()
    dumper   = fileFormat.dumper()
    
    treeRoot = buildTree(formats.scene.ItemNodeAdapter(sceneObject.rootItem()), builder)
    dumper.dump(treeRoot, fileStream)
    
    

def readScene(fileStream, formatName):
    assert isinstance(fileStream, file)
    assert formatName in formats.knowFileFormats()

    fileFormat = formats.fromName(formatName)

    parser   = fileFormat.parser()
    adapterFactory  = fileFormat.adapter

    treeRoot = parser.parse(fileStream)
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


    
  
    
        