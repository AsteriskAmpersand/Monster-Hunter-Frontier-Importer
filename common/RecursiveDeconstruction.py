# -*- coding: utf-8 -*-
"""
Created on Thu Apr 04 13:57:02 2019

@author: *&
"""

from collections import OrderedDict
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
    
class vect4(PyCStruct):
    fields = OrderedDict([
            ("x","float"),
            ("y","float"),
            ("z","float"),
            ("w","float"),
            ])
normal = vect4
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
        self.vertices = [vertexId() for i in range(self.count)]
        [v.marshall(data) for v in self.vertices]


class FBlockHeader(PyCStruct):
    fields = OrderedDict([
            ("type","uint32"),
            ("count","uint32"),
            ("size","uint32"),
            ])

class FBlock():
    def __init__(self, parent=None):
        self.Header = FBlockHeader()
        self.Data = None
        self.Parent = parent
    def marshall(self, data):
        print(type(self).__name__)
        types = {
            0x00020000:InitBlock,
            0x00000001:FileBlock,
            0x00000002:MainBlock,
            0x00000004:ObjectBlock,
            0x00000005:FaceBlock,
            0x00030000:trisStripsData,
            0x00040000:trisStripsData,
            0x00050000:byteArrayData,
            0x00060000:byteArrayData,
            0x00070000:vertexData,
            0x00080000:normalsData,
            0x000A0000:uvData,
            0x000B0000:rgbData,
            }
        
        self.Header.marshall(data)
        print(hex(self.Header.type))
        #subData = data[len(self.Header):self.Header.size]
        self.Data = [types[self.Header.type](parent=self) if self.Header.type in types else UnknBlock(self) for _ in range(self.Header.count)]
        [d.marshall(data) for d in self.Data]
    def prettyPrint(self, base = ""):
        name = type(self).__name__
        print(base+name+"-"+str(self.Header.count))
        for l in self.Data:
            l.prettyPrint(base+"\t")
            
class FileBlock(FBlock):pass
class MainBlock(FBlock):pass
class ObjectBlock(FBlock):pass
class FaceBlock(FBlock):pass
class InitBlock(PyCStruct):
    fields = OrderedDict([
            ("data","uint32"),
            ])

class UnknBlock (FBlock):
    def marshall(self, data):
        self.Data = data
    def prettyPrint(self,base = ""):
        pass

class dataContainer():
    def __init__(self, parent):
        self.count = parent.Header.count
    def marshall(self, data):
        self.Data = [self.dataType() for _ in range(self.count)]
        for datum in self.Data:
            datum.marshall(data)     
    def prettyPrint(self, base = ""):
        name = type(self).__name__
        print(base+name)
        

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

if __name__ == "__main__":
    filepath = r"E:\Projects\Frontier\KutKu\0001_0000003C\0001_00000014.fmod"
    f = open(filepath,"rb")
    data = FileLike(f.read())
    f.close()
    frontierFile = FBlock()
    frontierFile.marshall(data)
    frontierFile.prettyPrint()
