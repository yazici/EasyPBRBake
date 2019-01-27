import bpy
from bpy.types import Panel

from .main_panel import EPBRB_PT_main_panel

class EPBRB_PT_metallic_section(Panel):
    bl_label = 'Metallic'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_idname  = 'EPBRB_PT_metallic_section'
    bl_parent_id = 'EPBRB_PT_main_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return not context.scene.easy_pbr_bake_props.pack_channels
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.easy_pbr_bake_props

        layout.active = props.enable_metallic

        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(props, 'metallic_name')
        if props.autonames:
            row.enabled = False
        else:
            row.enabled = True
        layout.prop(props, 'metallic_clear')
        if props.metallic_clear:
            layout.prop(props, 'metallic_clear_color')
    
    def draw_header(self, context):
        layout = self.layout
        props = context.scene.easy_pbr_bake_props
        layout.prop(props, 'enable_metallic', text="")