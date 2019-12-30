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
        types = {
            0x00020000:InitBlock,
            0x00000001:FileBlock,
            0x00000002:MainBlock,
            0x00000004:ObjectBlock,
            0x00000005:FaceBlock,
            0xC0000000:SkeletonBlock,
            0x40000001:boneBlock,
            0x00030000:trisStripsData,
            0x00040000:trisStripsData,
            0x00050000:byteArrayData,
            0x00060000:byteArrayData,
            0x00070000:vertexData,
            0x00080000:normalsData,
            0x000A0000:uvData,
            0x000B0000:rgbData,
            0x000C0000:weightData,
            }
        return types[self.Header.type]() if self.Header.type in types else UnknBlock()

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
class vertexData(dataContainer):  
    dataType = position
class normalsData(dataContainer):  
    dataType = normal
class uvData(dataContainer):  
    dataType = uv
class rgbData(dataContainer):  
    dataType = vect4