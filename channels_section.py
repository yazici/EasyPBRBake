import bpy
from bpy.types import Panel

from .main_panel import EPBRB_PT_main_panel

class EPBRB_PT_channels_section(Panel):
    bl_label = 'Packed Channels'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_idname  = 'EPBRB_PT_channels_section'
    bl_parent_id = 'EPBRB_PT_main_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return context.scene.easy_pbr_bake_props.pack_channels

    def draw(self, context):
        layout = self.layout
        props = context.scene.easy_pbr_bake_props

        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(props, 'packed_name')
        if props.autonames:
            row.enabled = False
        else:
            row.enabled = True

        layout.prop(props, 'enable_metallic', text="Metallic")
        layout.prop(props, 'enable_roughness', text="Roughness")
        layout.prop(props, 'enable_ao', text="Ambient Occlusion")

        if props.enable_ao:
            box = layout.box()
            box.prop(props, 'ao_samples', text = 'AO Samples')
            box.prop(props, 'ao_distance', text = 'AO Distance')

        layout.prop(props, 'packed_clear')
        if props.packed_clear:
            layout.prop(props, 'packed_clear_color')
