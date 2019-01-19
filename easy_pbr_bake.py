import bpy
from bpy.types import Operator

def file_exists(file_path):
    try:
        file = open(file_path,'r')
        file.close()
        return True
    except:
        return False

def ext_file_name(file_name, ext):
    parts = file_name.split('.')
    if len(parts) > 1:
        if parts[len(parts) - 1] != ext:
            return file_name + '.' + ext
        else:
            return file_name
    else:
        return file_name + '.' + ext

def get_shader_nodes(mat_slots):
    shaders = []
    for ms in mat_slots:
        nodes = ms.material.node_tree.nodes
        for node in nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial':
                links = node.inputs['Surface'].links
                if links[0].from_node.bl_idname != 'ShaderNodeBsdfPrincipled':
                    return []
                shaders.append(links[0].from_node.name)
    return shaders
    

class EasyPBRBake(Operator):
    bl_idname = "easy_pbr.bake"
    bl_label = "Bake Textures"
    
    def execute(self, context):
        scn = context.scene
        obj = context.active_object
                
        # Get principled shader's nodes names        
        shaders = get_shader_nodes(obj.material_slots)
        if shaders == []:
            self.report({'ERROR'}, 'Incorrect materials setup')
            return {'FINISHED', 'CANCELLED'}
        
        # Bake albedo
        if scn.epbrb_enable_albedo:
            print('Baking albedo texture')
            
            # Get image to bake to
            name = scn.epbrb_albedo_name
            file_path = ext_file_name(scn.epbrb_path + name, 'png')
            image = None
            if scn.epbrb_albedo_clear or not file_exists(file_path):
                image = bpy.data.images.new(name, scn.epbrb_x_res, scn.epbrb_y_res, alpha = False)
                image.generated_color = scn.epbrb_albedo_clear_color
                image.colorspace_settings.name = 'sRGB'
                image.file_format = 'PNG'
                image.filepath_raw = file_path
            else:
                image = bpy.data.images.load(file_path, check_existing = False)
                            
            # Copy and change materials
            mat_dict = {}
            for ms in obj.material_slots:
                or_mat = ms.material
                mat = or_mat.copy()
                ms.material = mat
                mat_dict[ms.name] = or_mat
            
            # Set active texture of materials
            for ms in obj.material_slots:
                nodes = ms.material.node_tree.nodes
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = image
                ms.material.node_tree.nodes.active = tex_node

            # Bake
            bpy.ops.object.bake(type = 'DIFFUSE', width = scn.epbrb_x_res, height = scn.epbrb_y_res, pass_filter = {'COLOR'},
                                use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)
            
            # Restore materials
            for ms in obj.material_slots:
                mat = ms.material
                ms.material = mat_dict[ms.name]
                bpy.data.materials.remove(mat, do_unlink = True, do_id_user = True, do_ui_user = True)

            # Save and clear image
            image.save()
            bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
        
        # Bake metallic
        if scn.epbrb_enable_metallic:
            print('Baking metallic texture')
            
            # Get image to bake to
            name = scn.epbrb_metallic_name
            file_path = ext_file_name(scn.epbrb_path + name, 'png')
            image = None
            if scn.epbrb_metallic_clear or not file_exists(file_path):
                image = bpy.data.images.new(name, scn.epbrb_x_res, scn.epbrb_y_res, alpha = False)
                image.generated_color = scn.epbrb_metallic_clear_color
                image.colorspace_settings.name = 'Linear'
                image.file_format = 'PNG'
                image.filepath_raw = file_path
            else:
                image = bpy.data.images.load(file_path, check_existing = False)
                            
            # Copy and change materials
            mat_dict = {}
            for ms in obj.material_slots:
                or_mat = ms.material
                mat = or_mat.copy()
                ms.material = mat
                mat_dict[ms.name] = or_mat
            
            # Set active texture of materials
            for ms in obj.material_slots:
                nodes = ms.material.node_tree.nodes
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = image
                ms.material.node_tree.nodes.active = tex_node
            
            # Connect metallic channel
            nslot = 0
            for ms in obj.material_slots:
                nodes = ms.material.node_tree.nodes
                shader = nodes[shaders[nslot]]
                roughness_input = None
                if shader.inputs['Metallic'].is_linked:
                    roughness_input = shader.inputs['Metallic'].links[0].from_socket
                else:
                    rgb_node = ms.material.node_tree.nodes.new('ShaderNodeRGB')
                    roughness_input = rgb_node.outputs['Color']
                    r_val = shader.inputs['Metallic'].default_value
                    roughness_input.default_value = (r_val, r_val, r_val, 1)
                base_color = shader.inputs['Base Color']
                ms.material.node_tree.links.new(roughness_input, base_color, verify_limits = True)
                    
                nslot += 1

            # Bake
            bpy.ops.object.bake(type = 'DIFFUSE', width = scn.epbrb_x_res, height = scn.epbrb_y_res, pass_filter = {'COLOR'},
                                use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)
            
            # Restore materials
            for ms in obj.material_slots:
                mat = ms.material
                ms.material = mat_dict[ms.name]
                bpy.data.materials.remove(mat, do_unlink = True, do_id_user = True, do_ui_user = True)

            # Save and clear image
            image.save()
            bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
        
        # Bake roughness
        if scn.epbrb_enable_roughness:
            print('Baking roughness texture')
            
            # Get image to bake to
            name = scn.epbrb_roughness_name
            file_path = ext_file_name(scn.epbrb_path + name, 'png')
            image = None
            if scn.epbrb_roughness_clear or not file_exists(file_path):
                image = bpy.data.images.new(name, scn.epbrb_x_res, scn.epbrb_y_res, alpha = False)
                image.generated_color = scn.epbrb_roughness_clear_color
                image.colorspace_settings.name = 'Linear'
                image.file_format = 'PNG'
                image.filepath_raw = file_path
            else:
                image = bpy.data.images.load(file_path, check_existing = False)
                            
            # Copy and change materials
            mat_dict = {}
            for ms in obj.material_slots:
                or_mat = ms.material
                mat = or_mat.copy()
                ms.material = mat
                mat_dict[ms.name] = or_mat
            
            # Set active texture of materials
            for ms in obj.material_slots:
                nodes = ms.material.node_tree.nodes
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = image
                ms.material.node_tree.nodes.active = tex_node
            
            # Connect roughness channel
            nslot = 0
            for ms in obj.material_slots:
                nodes = ms.material.node_tree.nodes
                shader = nodes[shaders[nslot]]
                roughness_input = None
                if shader.inputs['Roughness'].is_linked:
                    roughness_input = shader.inputs['Roughness'].links[0].from_socket
                else:
                    rgb_node = ms.material.node_tree.nodes.new('ShaderNodeRGB')
                    roughness_input = rgb_node.outputs['Color']
                    r_val = shader.inputs['Roughness'].default_value
                    roughness_input.default_value = (r_val, r_val, r_val, 1)
                base_color = shader.inputs['Base Color']
                ms.material.node_tree.links.new(roughness_input, base_color, verify_limits = True)
                    
                nslot += 1

            # Bake
            bpy.ops.object.bake(type = 'DIFFUSE', width = scn.epbrb_x_res, height = scn.epbrb_y_res, pass_filter = {'COLOR'},
                                use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)
            
            # Restore materials
            for ms in obj.material_slots:
                mat = ms.material
                ms.material = mat_dict[ms.name]
                bpy.data.materials.remove(mat, do_unlink = True, do_id_user = True, do_ui_user = True)

            # Save and clear image
            image.save()
            bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)

        
        return {'FINISHED'}