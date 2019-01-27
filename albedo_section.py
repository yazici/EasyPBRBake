import bpy
from bpy.types import Panel

from .main_panel import EPBRB_PT_main_panel

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
        props = context.scene.easy_pbr_bake_props

        layout.active = props.enable_albedo

        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(props, 'albedo_name')
        if props.autonames:
            row.enabled = False
        else:
            row.enabled = True
        layout.prop(props, 'albedo_clear')
        if props.albedo_clear:
            layout.prop(props, 'albedo_clear_color')
    
    def draw_header(self, context):
        layout = self.layout
        props = context.scene.easy_pbr_bake_props
        layout.prop(props, 'enable_albedo', text="")