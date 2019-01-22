bl_info = {
    "name": "Easy PBR Bake",
    "description": "Helper for baking PBR textures from Principled Shader",
    "author": "DwanaGames",
    "version": (0, 0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Render",
    "category": "Render"
}

import bpy
from bpy.types import Panel
from bpy.props import BoolProperty, StringProperty, IntProperty, FloatVectorProperty, FloatProperty

from .easy_pbr_bake import EasyPBRBake

DEF_NAME = "bake"

def update_autonames(self, context):
    scn = context.scene
    
    if scn.epbrb_autonames:
        name = 'bake' # bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
        scn.epbrb_base_name = name
        scn.epbrb_albedo_name = name + '_albedo'
        scn.epbrb_metallic_name = name + '_metallic'
        scn.epbrb_roughness_name = name + '_roughness'

bpy.types.Scene.epbrb_autonames = BoolProperty(
    name = "Automatic Names", 
    description = "Automatically generate the names for the textures",
    default = True,
    update = update_autonames
)

bpy.types.Scene.epbrb_path = StringProperty(
    name = "Directory Path",
    description = "Directory where all the textures will be saved",
    default = "/tmp\\",
    subtype = 'DIR_PATH'
)

bpy.types.Scene.epbrb_base_name = StringProperty(
    name = "Base Name",
    description = "Base name for the textures when using automatic names",
    default = DEF_NAME
)

bpy.types.Scene.epbrb_x_res = IntProperty(
     name = "Resolution X",
     description = "Texture resolution in horizontal axis",
     default = 1024,
     subtype = 'PIXEL'
)

bpy.types.Scene.epbrb_y_res = IntProperty(
     name = "Resolution Y",
     description = "Texture resolution in vertical axis",
     default = 1024,
     subtype = 'PIXEL'
)

bpy.types.Scene.epbrb_margin = IntProperty(
     name = "Margin",
     description = "Extends the baked result as a post process filter",
     default = 16,
     subtype = 'PIXEL'
)

bpy.types.Scene.epbrb_selected_to_active = BoolProperty(
    name = 'Selected to Active',
    description = 'Bake shading on the surface of selected objects to the active object',
    default = False
)

bpy.types.Scene.epbrb_use_cage = BoolProperty(
    name = 'Cage', 
    description = 'Cast rays to active object from a cage',
    default = False
)

bpy.types.Scene.epbrb_cage_extrusion = FloatProperty(
    name = 'Extrusion',
    description = 'Distance to use for the inward ray cast when using selected to active',
    default = 0.0,
    min = 0.0,
    max = 1.0
)

bpy.types.Scene.epbrb_cage_object = StringProperty(
    name = "Cage Object",
    description = "Object to use as cage instead of calculating the cage from the active object with cage extrusion",
    default = ""
)

########### Albedo #######################
bpy.types.Scene.epbrb_enable_albedo = BoolProperty(
    name = 'Enable Albedo', 
    description = 'Generate albedo texture',
    default = False
)

bpy.types.Scene.epbrb_albedo_name = StringProperty(
    name = "Texture Name",
    description = "Name for the albedo texture file",
    default = DEF_NAME + '_albedo'
)

bpy.types.Scene.epbrb_albedo_clear = BoolProperty(
    name = "Clear Image", 
    description = "Clear albedo image before baking",
    default = True
)

bpy.types.Scene.epbrb_albedo_clear_color = FloatVectorProperty(
    name = 'Clear Color', 
    description = 'Albedo clear color',
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.0, 0.0, 0.0, 1.0),
    subtype = 'COLOR_GAMMA'
)

########### Packed #######################
bpy.types.Scene.epbrb_channel_pack = BoolProperty(
    name = 'Channel Packing', 
    description = 'Pack the metallic, roughness and ao bakes into a single image',
    default = False
)

bpy.types.Scene.epbrb_packed_name = StringProperty(
    name = "Texture Name",
    description = "Name for the channel packed texture file",
    default = DEF_NAME + '_packed'
)

bpy.types.Scene.epbrb_packed_clear = BoolProperty(
    name = "Clear Image", 
    description = "Clear packed image before baking",
    default = True
)

bpy.types.Scene.epbrb_packed_clear_color = FloatVectorProperty(
    name = 'Clear Color', 
    description = 'Packed texture clear color',
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.0, 0.0, 0.0, 1.0),
    subtype = 'COLOR'
)

########### Metallic #######################
bpy.types.Scene.epbrb_enable_metallic = BoolProperty(
    name = 'Enable Metallic', 
    description = 'Generate metallic texture',
    default = False
)

bpy.types.Scene.epbrb_metallic_name = StringProperty(
    name = "Texture Name",
    description = "Name for the metallic texture file",
    default = DEF_NAME + '_metallic'
)

bpy.types.Scene.epbrb_metallic_clear = BoolProperty(
    name = "Clear Image", 
    description = "Clear metallic image before baking",
    default = True
)

bpy.types.Scene.epbrb_metallic_clear_color = FloatVectorProperty(
    name = 'Clear Color', 
    description = 'Metallic clear color',
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.0, 0.0, 0.0, 1.0),
    subtype = 'COLOR'
)

########### Roughness #######################
bpy.types.Scene.epbrb_enable_roughness = BoolProperty(
    name = 'Enable Roughness', 
    description = 'Generate roughness texture',
    default = False
)

bpy.types.Scene.epbrb_roughness_name = StringProperty(
    name = "Texture Name",
    description = "Name for the roughness texture file",
    default = DEF_NAME + '_roughness'
)

bpy.types.Scene.epbrb_roughness_clear = BoolProperty(
    name = "Clear Image", 
    description = "Clear roughness image before baking",
    default = True
)

bpy.types.Scene.epbrb_roughness_clear_color = FloatVectorProperty(
    name = 'Clear Color', 
    description = 'Roughness clear color',
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.0, 0.0, 0.0, 1.0),
    subtype = 'COLOR'
)

class EPBRB_PT_main_panel(Panel):
    bl_label = 'Easy PBR Bake'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_idname  = 'EPBRB_PT_main_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.engine == 'CYCLES'
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.prop(scn, 'epbrb_autonames')
        layout.prop(scn, 'epbrb_path')
        
        row = layout.row()
        row.prop(scn, 'epbrb_base_name')
        if scn.epbrb_autonames:
            row.active = False
            row.enabled = False
        else:
            row.active = True
            row.enabled = True

        layout.prop(scn, 'epbrb_x_res')
        layout.prop(scn, 'epbrb_y_res')
        
        layout.prop(scn, 'epbrb_margin')
        layout.prop(scn, 'epbrb_selected_to_active')
        row = layout.row()
        row.prop(scn, 'epbrb_cage_extrusion', text = 'Ray Distance')
        if scn.epbrb_selected_to_active:
            row.active = True
            row.enabled = True
        else:
            row.active = False
            row.enabled = False
        
        layout.prop(scn, 'epbrb_channel_pack')
        
        layout.operator('easy_pbr.bake')
        
        layout.prop(scn, 'epbrb_enable_albedo')
        row = layout.row()
        row.prop(scn, 'epbrb_albedo_name')
        if scn.epbrb_autonames:
            row.active = False
            row.enabled = False
        else:
            row.active = True
            row.enabled = True
        layout.prop(scn, 'epbrb_albedo_clear')
        if scn.epbrb_albedo_clear:
            layout.prop(scn, 'epbrb_albedo_clear_color')
            
        if scn.epbrb_channel_pack:
            layout.prop(scn, 'epbrb_enable_metallic')
            layout.prop(scn, 'epbrb_enable_roughness')
            row = layout.row()
            row.prop(scn, 'epbrb_packed_name')
            if scn.epbrb_autonames:
                row.active = False
                row.enabled = False
            else:
                row.active = True
                row.enabled = True
            layout.prop(scn, 'epbrb_packed_clear')
            if scn.epbrb_packed_clear:
                layout.prop(scn, 'epbrb_packed_clear_color')
        else:
            layout.prop(scn, 'epbrb_enable_metallic')
            row = layout.row()
            row.prop(scn, 'epbrb_metallic_name')
            if scn.epbrb_autonames:
                row.active = False
                row.enabled = False
            else:
                row.active = True
                row.enabled = True
            layout.prop(scn, 'epbrb_metallic_clear')
            if scn.epbrb_metallic_clear:
                layout.prop(scn, 'epbrb_metallic_clear_color')
            
            layout.prop(scn, 'epbrb_enable_roughness')
            row = layout.row()
            row.prop(scn, 'epbrb_roughness_name')
            if scn.epbrb_autonames:
                row.active = False
                row.enabled = False
            else:
                row.active = True
                row.enabled = True
            layout.prop(scn, 'epbrb_roughness_clear')
            if scn.epbrb_roughness_clear:
                layout.prop(scn, 'epbrb_roughness_clear_color')

class EPBRB_PT_albedo_section(Panel):
    bl_label = 'Albedo'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_idname  = 'EPBRB_PT_albedo_section'
    bl_parent_id = 'EPBRB_PT_main_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(scn, 'epbrb_albedo_name')
        if scn.epbrb_autonames:
            row.active = False
            row.enabled = False
        else:
            row.active = True
            row.enabled = True
        layout.prop(scn, 'epbrb_albedo_clear')
        if scn.epbrb_albedo_clear:
            layout.prop(scn, 'epbrb_albedo_clear_color')
        
        
    def draw_header(self, context):
        layout = self.layout
        scn = context.scene
        layout.prop(scn, 'epbrb_enable_albedo', text="")
        
classes = (
    EasyPBRBake,
    EPBRB_PT_main_panel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()