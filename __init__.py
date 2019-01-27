bl_info = {
    "name": "Easy PBR Bake",
    "description": "Helper for baking PBR textures from Principled Shader",
    "author": "DwanaGames",
    "version": (0, 0, 2, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Render",
    "category": "Render"
}

import bpy
from bpy.props import PointerProperty

from .main_panel import EPBRB_PT_main_panel
from .properties import EasyPBRBakeProp
from .easy_pbr_bake import EasyPBRBake
from .albedo_section import EPBRB_PT_albedo_section
from .channels_section import EPBRB_PT_channels_section
from .metallic_section import EPBRB_PT_metallic_section
from .roughness_section import EPBRB_PT_roughness_section
from .ao_section import EPBRB_PT_ao_section
from .normal_section import EPBRB_PT_normal_section

classes = (
    EasyPBRBakeProp,
    EPBRB_PT_main_panel,
    EasyPBRBake,
    EPBRB_PT_albedo_section,
    EPBRB_PT_channels_section,
    EPBRB_PT_metallic_section,
    EPBRB_PT_roughness_section,
    EPBRB_PT_ao_section,
    EPBRB_PT_normal_section
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.easy_pbr_bake_props = PointerProperty(type=EasyPBRBakeProp)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.easy_pbr_bake_props

if __name__ == "__main__":
    register()