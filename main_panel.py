import bpy
from bpy.types import Panel

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
        props = context.scene.easy_pbr_bake_props

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(props, 'autonames')
        layout.prop(props, 'dir_path')
        
        layout.prop(props, 'base_name')

        layout.prop(props, 'x_res')
        layout.prop(props, 'y_res')
        
        layout.prop(props, 'margin')
        layout.prop(props, 'selected_to_active')
        row = layout.row()
        row.prop(props, 'cage_extrusion', text = 'Ray Distance')
        if props.selected_to_active:
            row.enabled = True
        else:
            row.enabled = False
        
        layout.prop(props, 'pack_channels')
        
        layout.operator('object.easy_pbr_bake')