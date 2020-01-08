# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 23:03:36 2019

@author: AsteriskAmpersand
"""
try:
    from ..fmod.FBlock import FBlock
    from ..common.FileLike import FileLike
except:
    import sys
    sys.path.insert(0, r'..\common')
    sys.path.insert(0, r'..\fmod')
    from FBlock import FBlock
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

class FBoneRemap():
    def __init__(self, BoneRemapBlock):
        self.remapTable = []
        for boneID in BoneRemapBlock.Data:
            self.remapTable.append(boneID.Data.id)
        
    def __getitem__(self,key):
        return self.remapTable[key]

class FMesh():
    def __init__(self, ObjectBlock):
        Objects = iter(ObjectBlock.Data)
        self.Faces = FFaces(next(Objects))
        self.UnknownSingular = FUnkSing(next(Objects))#Material List
        self.UnknownTriData = FTriData(next(Objects))#Material Map
        self.Vertices = FVertices(next(Objects))
        self.Normals = FNormals(next(Objects))
        self.UVs = FUVs(next(Objects))
        self.RGBLike = FRGB(next(Objects))
        self.Weights = FWeights(next(Objects))
        self.BoneRemap = FBoneRemap(next(Objects))
        #boneMap
        #unknownBlock
        
    def traditionalMeshStructure(self):
        return {"vertices":self.Vertices.Vertices, 
                "faces":self.Faces.Faces, 
                "normals":self.Normals.Normals, 
                "uvs":self.UVs.UVs,
                "weights":self.Weights.Weights,
                "boneRemap":self.BoneRemap}
        
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