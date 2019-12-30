# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 21:50:00 2019

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

class FBone():
    def __init__(self,fbone):
        for field in fbone.Data[0].fields:
            setattr(self,field,getattr(fbone.Data[0],field))

class FSkeleton():
    def __init__(self, FilePath):
        with open(FilePath, "rb") as modelFile:
            frontierFile = FBlock()
            frontierFile.marshall(FileLike(modelFile.read()))
        Bones = frontierFile.Data[1:]
        self.Skeleton = {}
        for fileBone in Bones:
            fbone = FBone(fileBone)
            self.Skeleton[fbone.nodeID]=fbone
    
    def skeletonStructure(self):
        return self.Skeleton