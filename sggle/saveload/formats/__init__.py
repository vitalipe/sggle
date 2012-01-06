
import _xml
import _json

_knownFileFormats = {}


def knowFileFormats():
    return _knownFileFormats.keys()

def fromName(name):
    return _knownFileFormats[name]

def registerFileFormat(name, fileFormat):
    assert isinstance(name, (str,unicode))
    assert name not in knowFileFormats()

    _knownFileFormats[name] = fileFormat
    
    
# register known formats:
registerFileFormat("xml" , _xml)
registerFileFormat("json", _json)



