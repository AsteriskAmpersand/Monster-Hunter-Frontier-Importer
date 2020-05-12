# -*- coding: utf-8 -*-
"""
Created on Thu Apr 04 13:57:02 2019

@author: *&
"""

from collections import OrderedDict


try:
    from ..common.Cstruct import PyCStruct
    from ..common.FileLike import FileLike
except:
    import sys
    sys.path.insert(0, r'..\common')
    from Cstruct import PyCStruct
    from FileLike import FileLike

class byte4(PyCStruct):
    fields = OrderedDict([
            ("array","byte[4]"),
            ])
    
class uintField(PyCStruct):
    fields = OrderedDict([
            ("id","uint32"),
            ])
    
class uv(PyCStruct):
    fields = OrderedDict([
            ("u","float"),
            ("v","float"),
            ])

class vect3(PyCStruct):
    fields = OrderedDict([
            ("x","float"),
            ("y","float"),
            ("z","float")
            ])
position = vect3
normal = vect3
class vect4(PyCStruct):
    fields = OrderedDict([
            ("x","float"),
            ("y","float"),
            ("z","float"),
            ("w","float"),
            ])
tangent = vect4

class vertexId(PyCStruct):
    fields = OrderedDict([
            ("id","uint32"),])

class tristrip(PyCStruct):
    fields = OrderedDict([
            ("count","uint32"),
            ])
    def marshall(self, data):
        super().marshall(data)
        self.vertices = [vertexId() for i in range(self.count&0xFFFFFFF)]
        [v.marshall(data) for v in self.vertices]

class weight(PyCStruct):
    fields = OrderedDict([
            ("boneID","uint32"),
            ("weightValue","float"),
            ])

class weightData(PyCStruct):
    fields = OrderedDict([
            ("count","uint32"),
            ])
    def marshall(self, data):
        super().marshall(data)
        self.weights = [weight() for i in range(self.count)]
        [w.marshall(data) for w in self.weights]
    def prettyPrint(self, base = ""):
        #name = type(self).__name__
        #print(base+name)
        pass
    
class boneBlock(PyCStruct):
    fields = OrderedDict([
            ("nodeID","int32"),
            ("parentID","int32"),
            ("leftChild","int32"),
            ("rightSibling","int32"),
            ("vec1","float[4]"),
            ("vec2","float[4]"),
            ("posVec","float[4]"),
            ("null","uint32"),
            ("chainID","uint32"),
            ("unkn2","uint32[46]"),
            ])

class textureData(PyCStruct):
    fields = OrderedDict([
        ("imageID" , "uint32"),
        ("width" , "uint32"),
        ("height" , "uint32"),
        ("unkn", "byte[244]")])
    
class FBlockHeader(PyCStruct):
    fields = OrderedDict([
            ("type","uint32"),
            ("count","int32"),
            ("size","uint32"),
            ])

class FBlock():
    def __init__(self, parent=None):
        self.Header = FBlockHeader()
        self.Data = None
        self.Parent = parent
    def marshall(self, data):       
        self.Header.marshall(data)
        subData = FileLike(data.read(self.Header.size-len(self.Header)))
        self.Data = [self.getType() for _ in range(self.Header.count)]
        [datum.marshall(subData) for datum in self.Data]
    def prettyPrint(self, base = ""):
        name = type(self.getType()).__name__
        print(base+name+":"+" "+str(self.Header.count) + " \t"+hex(self.Header.type))
        for datum in self.Data:
            datum.prettyPrint(base+"\t")
    def getType(self):     
        return self.typeLookup(self.Header.type)()    
    @staticmethod
    def typeLookup(value):
        types = {
            0x00020000:InitBlock,
            0x00000001:FileBlock,
            0x00000002:MainBlock,
            0x00000004:ObjectBlock,
            0x00000005:FaceBlock,
            0x00000009:MaterialBlock,
            0x0000000A:TextureBlock,
            0xC0000000:SkeletonBlock,
            0x40000001:boneBlock,
            0x00030000:trisStripsData,
            0x00040000:trisStripsData,
            0x00050000:materialList,
            0x00060000:materialMap,
            0x00070000:vertexData,
            0x00080000:normalsData,
            0x000A0000:uvData,
            0x000B0000:rgbData,
            0x000C0000:weightData,
            0x00100000:boneMapData,
            }
        return types[value] if value in types else UnknBlock
class FileBlock(FBlock):
    pass
class MainBlock(FBlock):
    pass
class ObjectBlock(FBlock):
    pass
class FaceBlock(FBlock):
    pass
class SkeletonBlock(FBlock):
    pass
class SimpleFBlock(FBlock):
    def getType(self):
        return self.ftype()
    def prettyPrint(self,base = ""):
        pass

class materialHeader(PyCStruct):
    fields = OrderedDict([
            ("unkn1" , "uint32"),
            ("unkn2" , "uint32"),
            ("blockSize" , "uint32"),
            ("unkn3" , "float"),
            ("unkn4" , "float"),
            ("unkn5" , "float"),
            ("unkn6" , "float"),
            ("unkn7" , "float"),
            ("unkn8" , "float"),
            ("unkn9" , "float"),
            ("float0", "float"),
            ("float1" , "float"),
            ("float2" , "float"),
            ("float3" , "float"),
            ("textureCount" ,"uint32"),
            ("unkn11" , "float"),
            ("unkn12" , "uint32"),])
    
class materialChannelMapping(PyCStruct):
    def __init__(self,blocksize):
        if blocksize > 272:
            self.fields = OrderedDict([
                        ("unkn" , "uint32[%s]"%(blocksize-80)),
                        ("TextureLinkDif" , "uint32"),
                        ("TextureLinkNor" , "uint32"),
                        ("TextureLinkSpe" , "uint32"),])
        else:
            self.fields = OrderedDict([
                        ("unkn" , "byte[%s]"%(blocksize-72)),
                        ("TextureLinkDif" , "uint32"),])
        super().__init__()

class textureIndex(PyCStruct):
    fields = OrderedDict([("index","uint32")])
    
class materialData(PyCStruct):
    fields = OrderedDict([
            #("unkn1" , "uint32"),
            #("unkn2" , "uint32"),
            #("blockSize" , "uint32"),
            ("unkn3" , "float[3]"),
            ("unkn6" , "float"),
            ("unkn7" , "float[3]"),
            ("float4" , "float[4]"),
            ("unkn8", "uint32"),
            ("unkn9" , "float"),
            ("textureCount" , "uint32"),
            ("unkn" , "byte[200]"),])
    def marshall(self,data):
        super().marshall(data)
        #print()
        #for prop in self.fields:
        #    print("%s: %s"%(prop,getattr(self,prop)))
        self.textureIndices = [textureIndex() for i in range(self.textureCount)]
        list(map(lambda x: x.marshall(data),self.textureIndices))
    """
    def marshall(self,data):
        self.Header = materialHeader()
        self.Header.marshall(data)
        self.Channels = materialChannelMapping(self.Header.blockSize)
        self.Channels.marshall(data)
        return self"""

class TextureBlock(SimpleFBlock):
    ftype = textureData
    
class MaterialBlock(SimpleFBlock):
    ftype = materialData

class InitData(PyCStruct):
    fields = {"data":"uint32"}
        
class InitBlock (FBlock):        
    def marshall(self, data):
        self.Data = InitData()
        self.Data.marshall(data)
    def prettyPrint(self, base=""):
        pass
        
class UnknBlock (FBlock):
    def marshall(self, data):
        self.Data = data
    def prettyPrint(self, base = ""):
        pass

class dataContainer():
    def marshall(self, data):
        self.Data = self.dataType()
        self.Data.marshall(data)     
    def prettyPrint(self, base = ""):
        #name = type(self).__name__
        #print(base+name)
        pass
class trisStripsData(dataContainer):
    dataType = tristrip
class byteArrayData(dataContainer):
    dataType = byte4
class materialList(dataContainer):
    dataType = uintField
class materialMap(dataContainer):
    dataType = uintField
class boneMapData(dataContainer):
    dataType = uintField
class vertexData(dataContainer):  
    dataType = position
class normalsData(dataContainer):  
    dataType = normal
class uvData(dataContainer):  
    dataType = uv
class rgbData(dataContainer):  
    dataType = vect4