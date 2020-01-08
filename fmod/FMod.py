# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 23:03:36 2019

@author: AsteriskAmpersand
"""
from itertools import cycle
try:
    from ..fmod.FBlock import FBlock
    from ..fmod.FBlock import (FaceBlock, materialList, materialMap, vertexData,
                               normalsData,uvData,rgbData,weightData,boneMapData,
                               UnknBlock)
    from ..common.FileLike import FileLike  
except:
    import sys
    sys.path.insert(0, r'..\common')
    sys.path.insert(0, r'..\fmod')
    from FBlock import FBlock
    from FBlock import (FaceBlock, materialList, materialMap, vertexData,
                               normalsData,uvData,rgbData,weightData,boneMapData,
                               UnknBlock)
    from FileLike import FileLike    

class FFaces():
    def __init__(self, FaceBlock):
        self.Faces = []
        for tristripArray in FaceBlock.Data:
            for tristrip in tristripArray.Data:
                verts=tristrip.Data.vertices
                self.Faces += [[v1.id,v2.id,v3.id][::((w+1)%2)*2-1]
                               for w,(v1, v2, v3) in enumerate(zip(verts[:-2], verts[1:-1], verts[2:]))]
class FUnkSing():
    def __init__(self, UnknownSingularBlock):
        pass

class FTriData():
    def __init__(self, FaceDataBlock):
        self.Data = [faceElement.Data for faceElement in FaceDataBlock.Data]

class FVertices():
    def __init__(self, VertexBlock):
        self.Vertices = [(Vertex.Data.x, Vertex.Data.y, Vertex.Data.z) for Vertex in VertexBlock.Data]
        
class FNormals():
    def __init__(self, NormalsBlock):
        self.Normals = [[Normal.Data.x, Normal.Data.y, Normal.Data.z] for Normal in NormalsBlock.Data]
        
class FUVs():
    def __init__(self, UVBlock):
        self.UVs = [[UV.Data.u, 1-UV.Data.v] for UV in UVBlock.Data]
        
class FRGB():
    def __init__(self,RGBBlock):
        self.RGB = [[rgb.Data.x,rgb.Data.y,rgb.Data.z,rgb.Data.w] for rgb in RGBBlock.Data]

class FWeights():
    def __init__(self, WeightsBlock):
        groups = {}
        for vertID,weights in enumerate(WeightsBlock.Data):
            for weight in weights.weights:
                if weight.boneID not in groups:
                    groups[weight.boneID] = []
                groups[weight.boneID].append((vertID,weight.weightValue/100))
        self.Weights = groups

class FRemap():
    def __init__(self, RemapBlock):
        self.remapTable = []
        for ID in RemapBlock.Data:
            self.remapTable.append(ID.Data.id)
        
    def __getitem__(self,key):
        return self.remapTable[key]
    
    def __iter__(self):
        return iter(self.remapTable)
    
    def __repr__(self):
        return str(self.remapTable)
    
    def __len__(self):
        return len(self.remapTable)

class FBoneRemap(FRemap):
    pass

class FMatList(FRemap):
    pass

class FMatPerTri(FRemap):
    pass

class DummyRemap():
    def __getitem__(self,value):
        return value
class DummyMaterials():
    def __iter__(self):
        return iter([0])
class DummyFaceMaterials():
    def __iter__(self):
        return cycle([0])
    def __getitem__(self,value):
        return 0
class DummyUVs():
    def __iter__(self):
        return cycle([(0,0)])
    def __getitem__(self,value):
        return (0,0)

class FMesh():
    def __init__(self, ObjectBlock):
        Objects = ObjectBlock.Data
        attributes = {FaceBlock:"Faces",materialList:"MaterialList",
                      materialMap:"MaterialMap",vertexData:"Vertices",
                      normalsData:"Normals",uvData:"UVs",
                      rgbData:"RGBLike",weightData:"Weights",
                      boneMapData:"BoneRemap"}#,UnknBlock:"UnknBlock"}
        typeData = {FaceBlock:FFaces,materialList:FMatList,
                      materialMap:FMatPerTri,vertexData:FVertices,
                      normalsData:FNormals,uvData:FUVs,
                      rgbData:FRGB,weightData:FWeights,
                      boneMapData:FBoneRemap}#,UnknBlock:"UnknBlock"}
        defaultData = {"UVs":DummyUVs,"BoneRemap":DummyRemap,
                       "MaterialList":DummyMaterials,"MaterialMap":DummyFaceMaterials}
        for objectBlock in Objects:
            typing = FBlock.typeLookup(objectBlock.Header.type)
            if typing in attributes:
                setattr(self,attributes[typing],typeData[typing](objectBlock))
            if typing is FaceBlock:
                tristripRepetition = self.calcStripLengths(objectBlock)
        if hasattr(self,"MaterialMap"):
            self.MaterialMap = self.decomposeMaterialList(self.MaterialMap,tristripRepetition)
        for attr in defaultData:
            if not hasattr(self,attr):
                setattr(self,attr,defaultData[attr]())
        """
        self.Faces = FFaces(next(Objects))
        self.MaterialList = FMatList(next(Objects))#Material List
        self.MaterialMap = FMatPerTri(next(Objects))#Material Map
        self.Vertices = FVertices(next(Objects))
        self.Normals = FNormals(next(Objects))
        self.UVs = FUVs(next(Objects))
        self.RGBLike = FRGB(next(Objects))
        self.Weights = FWeights(next(Objects))
        self.BoneRemap = FBoneRemap(next(Objects))
        """
        #unknownBlock
    @staticmethod
    def calcStripLengths(faceBlock):
        lengths = []
        for tristripArray in faceBlock.Data:
            for tristrip in tristripArray.Data:
                lengths.append(len(tristrip.Data.vertices)-2)
        return lengths

    @staticmethod
    def decomposeMaterialList(materialList,triStripCounts):
        materialArray = []
        for m,tlen in zip(materialList,triStripCounts):
            materialArray += [m]*tlen
        return materialArray
        
    def traditionalMeshStructure(self):
        return {"vertices":self.Vertices.Vertices, 
                "faces":self.Faces.Faces, 
                "normals":self.Normals.Normals, 
                "uvs":self.UVs.UVs,
                "weights":self.Weights.Weights,
                "boneRemap":self.BoneRemap,
                "materials":self.MaterialList,
                "faceMaterial":self.MaterialMap,}
        
class FModel():
    def __init__(self, FilePath):
        with open(FilePath, "rb") as modelFile:
            frontierFile = FBlock()
            frontierFile.marshall(FileLike(modelFile.read()))
        Meshes = frontierFile.Data[1].Data
        self.Meshparts = [FMesh(Mesh) for Mesh in Meshes]
        frontierFile.prettyPrint()
    
    def traditionalMeshStructure(self):
        return [mesh.traditionalMeshStructure() for mesh in self.Meshparts]