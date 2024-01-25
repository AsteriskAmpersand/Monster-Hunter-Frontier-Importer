# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 01:10:11 2019

@author: AsteriskAmpersand
"""
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from ..fmod import FSklImporterLayer


class ImportFSKL(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhf_fskl"
    bl_label = "Load MHF FSKL file (.fskl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".fskl"
    filter_glob = StringProperty(default="*.fskl", options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        bpy.ops.object.select_all(action='DESELECT')
        importer = FSklImporterLayer.FSklImporter()
        importer.execute(self.properties.filepath)
        return {'FINISHED'}
    
    
def menu_func_import(self, context):
    self.layout.operator(ImportFSKL.bl_idname, text="MHF FSKL (.fskl)")