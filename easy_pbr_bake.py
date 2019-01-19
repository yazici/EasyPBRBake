import bpy
from bpy.types import Operator

class EasyPBRBake(Operator):
    bl_idname = "easy_pbr_bake"
    bl_label = "Bake Textures"
    
    def execute(self, context):
        print('Hola addon')
        return {'FINISHED'}