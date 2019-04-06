# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 01:18:50 2019

@author: AsteriskAmpersand
"""
import sys

from pathlib import Path
sys.path.insert(0, r'..\common')
from FileLike import FileLike
from FBlock import FBlock
from FMod import FModel

if __name__ == "__main__":
    frontier = r"G:\Frontier"
    separator="=========================================="
    for filepath in list(Path(frontier).rglob("*.fmod")):
        print(filepath)    
        Model = FModel(filepath)
        print(separator)
        
"""
from pathlib import Path
frontier = r"G:\Frontier"
for filepath in list(Path(frontier).rglob("*.fmod")):
    filepath = filepath.resolve().as_posix()
    bpy.ops.custom_import.import_mhf_fmod(filepath = filepath)    
    bpy.context.scene.render.image_settings.file_format='JPEG'
    bpy.context.scene.render.filepath = filepath[:-4]+".JPEG"
    bpy.ops.render.opengl(write_still=True)
"""