bl_info = {
    "name": "Easy PBR Bake",
    "description": "Helper for baking PBR textures from Principled Shader",
    "author": "DwanaGames",
    "version": (0, 0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Render",
    "category": "Render"
}

import bpy
from . epbrb_main_panel import EPBRB_PT_main_panel

classes = ( EPBRB_PT_main_panel )

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()