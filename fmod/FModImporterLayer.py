# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 02:55:27 2019

@author: AsteriskAmpersand
"""

from ..fmod.FMod import FModel
import bpy
import bmesh
import array
import os
from pathlib import Path
from ..blender.BlenderNodesFunctions import principledSetup, diffuseSetup, normalSetup, specularSetup, finishSetup


class FModImporter:
    @staticmethod
    def execute(fmodPath, import_textures):
        bpy.context.scene.render.engine = 'CYCLES'
        fmod = FModel(fmodPath)
        meshes = fmod.traditionalMeshStructure()
        materials = fmod.Materials
        blenderMaterials = {}
        for ix, mesh in enumerate(meshes):
            FModImporter.importMesh(ix, mesh,blenderMaterials)
        if import_textures:
            FModImporter.importTextures(materials, fmodPath,blenderMaterials)
            
    @staticmethod
    def importMesh(ix, mesh, bmats):
        meshObjects = []
        bpy.ops.object.select_all(action='DESELECT')

        #Geometry
        blenderMesh, blenderObject = FModImporter.createMesh("FModMeshpart %03d" % (ix, ), mesh)
        #Normals Handling
        FModImporter.setNormals(mesh["normals"], blenderMesh)
        #UVs
        #for ix, uv_layer in enumerate(meshpart["uvs"]):
        #, mesh["materials"], mesh["faceMaterial"]
        if hasattr(blenderMesh, 'uv_textures'):
            # Blender <2.8
            FModImporter.createTextureLayer(
                blenderMesh, mesh["uvs"], mesh["materials"], mesh["faceMaterial"], bmats
            )
        else:
            # Blender 2.8+
            FModImporter.createTextureLayerFromObj(
                blenderObject, blenderMesh, mesh["uvs"], mesh["materials"], mesh["faceMaterial"], bmats
            )
        
        #Weights
        FModImporter.setWeights(mesh["weights"], mesh["boneRemap"], blenderObject)
        blenderMesh.update()
        meshObjects.append(blenderObject)
        
    @staticmethod
    def createMesh(name, meshpart):
        blenderMesh = bpy.data.meshes.new("%s" % (name, ))
        blenderMesh.from_pydata(meshpart["vertices"], [], meshpart["faces"])
        blenderMesh.update()
        blenderObject = bpy.data.objects.new("%s" % (name, ), blenderMesh)
        try:
            # Blender 2.8+
            bpy.context.collection.objects.link(blenderObject)
        except ValueError:
            # Blender <2.8
            bpy.context.scene.objects.link(blenderObject)
        return blenderMesh, blenderObject

    @staticmethod
    def createTextureLayerFromObj(blenderObj, blenderMesh, uv, materialList, faceMaterials, bmats):
        """General function to create texture, for Blender 2.8+."""
        #if bpy.context.active_object.mode!='OBJECT':
        #    bpy.ops.object.mode_set(mode='OBJECT')
        for material in materialList:
            matname = "FrontierMaterial-%03d" % material
            if material not in bmats:
                mat = bpy.data.materials.new(name=matname)
                bmats[material] = mat
            mat = bmats[material]
            blenderMesh.materials.append(mat)
            #materials.append(mat)
        #blenderMesh.uv_textures.new("UV0")
        blenderObj.data.uv_layers.new(name="UV0")
        blenderMesh.update()
        blenderBMesh = bmesh.new()
        blenderBMesh.from_mesh(blenderMesh)
        uv_layer = blenderBMesh.loops.layers.uv["UV0"]
        blenderBMesh.faces.ensure_lookup_table()
        for face in blenderBMesh.faces:
            for loop in face.loops:
                #BlenderImporterAPI.dbg.write("\t%d\n"%loop.vert.index)
                loop[uv_layer].uv = uv[loop.vert.index]
            #print("%d/%d/%d"%(face.index,len(faceMaterials),len(blenderBMesh.faces)))
            face.material_index = faceMaterials[face.index]
        blenderBMesh.to_mesh(blenderMesh)
        blenderMesh.update()
        return #uvtex
    
    @staticmethod
    def createTextureLayer(blenderMesh, uv, materialList, faceMaterials, bmats):#texFaces):
        #if bpy.context.active_object.mode!='OBJECT':
        #    bpy.ops.object.mode_set(mode='OBJECT')
        for material in materialList:
            matname = "FrontierMaterial-%03d" % material
            if material not in bmats:
                mat = bpy.data.materials.new(name=matname)
                bmats[material] = mat
            mat = bmats[material]
            blenderMesh.materials.append(mat)
            #materials.append(mat)
        blenderMesh.uv_textures.new("UV0")
        blenderMesh.update()
        blenderBMesh = bmesh.new()
        blenderBMesh.from_mesh(blenderMesh)
        uv_layer = blenderBMesh.loops.layers.uv["UV0"]
        blenderBMesh.faces.ensure_lookup_table()
        for face in blenderBMesh.faces:
            for loop in face.loops:
                #BlenderImporterAPI.dbg.write("\t%d\n"%loop.vert.index)
                loop[uv_layer].uv = uv[loop.vert.index]
            #print("%d/%d/%d"%(face.index,len(faceMaterials),len(blenderBMesh.faces)))
            face.material_index = faceMaterials[face.index]
        blenderBMesh.to_mesh(blenderMesh)
        blenderMesh.update()
        return #uvtex

    @staticmethod
    def setNormals(normals, meshpart):
        meshpart.update(calc_edges=True)
        #meshpart.normals_split_custom_set_from_vertices(normals)
        
        clnors = array.array('f', [0.0] * (len(meshpart.loops) * 3))
        meshpart.loops.foreach_get("normal", clnors)
        meshpart.polygons.foreach_set("use_smooth", [True] * len(meshpart.polygons))
        
        #meshpart.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
        meshpart.normals_split_custom_set_from_vertices(normals)
        #meshpart.normals_split_custom_set([normals[loop.vertex_index] for loop in meshpart.loops])
        meshpart.use_auto_smooth = True
        #Setting is True by default on Blender 2.8+
        if hasattr(meshpart, 'show_edge_sharp'):
            # Blender 2.7x
            meshpart.show_edge_sharp = True
        
    @staticmethod
    def setWeights(weights, remap, meshObj):
        for meshBoneIx, group in weights.items():
            groupIx = remap[meshBoneIx]
            groupId = "%03d" % groupIx if isinstance(groupIx, int) else str(groupIx)
            groupName = "Bone.%s" % str(groupId)
            for vertex, weight in group:
                if groupName not in meshObj.vertex_groups:
                    meshObj.vertex_groups.new(name=groupName)#blenderObject Maybe?
                meshObj.vertex_groups[groupName].add([vertex], weight, 'ADD')
            
        
    @staticmethod
    def maximizeClipping():
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10**4

    @staticmethod
    def clearScene():
        for key in list(bpy.context.scene.keys()):
            del bpy.context.scene[key]
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete() 
        for i in bpy.data.images.keys():
            bpy.data.images.remove(bpy.data.images[i])
        return
    
    @staticmethod
    def importTextures(materials, path, bmats):
        def getTexture(ix):
            filepath = FModImporter.prayToGod(path, ix)
            print(ix)
            print(filepath)
            return FModImporter.fetchTexture(filepath)
        
        for ix,mat in bmats.items():
            # Setup
            mat.use_nodes=True
            nodeTree = mat.node_tree
            nodes = nodeTree.nodes
            for node in nodes:
                nodes.remove(node)
            # Preamble
            #ix = int(mat.name.split("-")[1])
            diffuseIx = materials[ix].getDiffuse()
            normalIx = materials[ix].getNormal()
            specularIx = materials[ix].getSpecular()
            # Construction        
            setup = principledSetup(nodeTree) 
            next(setup)
            if diffuseIx is not None:
                diffuseNode = diffuseSetup(nodeTree, getTexture(diffuseIx))
                setup.send(diffuseNode)
            else: setup.send(None)
            #setup.send(None)
            if normalIx is not None:
                normalNode = normalSetup(nodeTree, getTexture(normalIx))
                setup.send(normalNode)
            else: setup.send(None)
            if specularIx is not None:
                specularNode = specularSetup(nodeTree, getTexture(specularIx))
                setup.send(specularNode)
            else: setup.send(None)
            finishSetup(nodeTree,next(setup))
                #FModImporter.assignTexture(mesh, textureData)
            #except:
            #    pass            
            
    @staticmethod
    def assignTexture(meshObject, textureData):
        for uvLayer in meshObject.data.uv_textures:
            for uv_tex_face in uvLayer.data:
                uv_tex_face.image = textureData
        meshObject.data.update()
        
    @staticmethod
    def fetchTexture(filepath):
        if os.path.exists(filepath):
            return bpy.data.images.load(filepath)
        else:
            raise FileNotFoundError("File %s not found"%filepath)
        
    @staticmethod
    def prayToGod(path, ix):
        modelPath = Path(path)
        candidates = [
            modelPath.parent,
            *sorted([f for f in modelPath.parents[1].glob('**/*') if f.is_dir() and f > modelPath.parent]),
            *sorted([f for f in modelPath.parents[1].glob('**/*') if f.is_dir() and f < modelPath.parent])
        ]
        for directory in candidates:
            current = sorted(list(directory.rglob("*.png")))
            if current:
                current.sort()
                return current[min(ix, len(current))].resolve().as_posix()
