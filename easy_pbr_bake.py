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

def get_shader_data(mat_slots):
    data = {}
    original_mats = []
    materials = []
    principled_shaders = []
    emission_shaders = []
    texture_nodes = []
    for ms in mat_slots:
        or_material = ms.material
        original_mats.append(or_material)
        material = or_material.copy()
        materials.append(material)
        nodes = material.node_tree.nodes
        for node in nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial':
                links = node.inputs['Surface'].links
                if len(links) == 0:
                    return data
                if links[0].from_node.bl_idname != 'ShaderNodeBsdfPrincipled':
                    return data
                principled_shaders.append(links[0].from_node)
                emission_node = nodes.new('ShaderNodeEmission')
                material.node_tree.links.new(emission_node.outputs[0], node.inputs['Surface'], verify_limits = True)
                emission_shaders.append(emission_node)
                tex_node = nodes.new('ShaderNodeTexImage')
                nodes.active = tex_node
                texture_nodes.append(tex_node)
                break

    data['OriginalMaterials'] = original_mats
    data['Materials'] = materials
    data['PrincipledShaders'] = principled_shaders
    data['EmissionShaders'] = emission_shaders
    data['TextureNodes'] = texture_nodes
    return data

def get_image(name, scene, clear, clear_color, colorspace):
    """ Return an image to bake to """
    file_path = ext_file_name(scene.epbrb_path + name, 'png')
    image = None
    if clear or not file_exists(file_path):
        image = bpy.data.images.new(name, scene.epbrb_x_res, scene.epbrb_y_res, alpha = False)
        image.generated_color = clear_color
        image.colorspace_settings.name = colorspace
        image.file_format = 'PNG'
        image.filepath_raw = file_path
    else:
        image = bpy.data.images.load(file_path, check_existing = False)
    return image

def get_output_socket(shader, input_name, nodes):
    output_socket = None
    input_socket = shader.inputs[input_name]
    if input_socket.is_linked:
        output_socket = input_socket.links[0].from_socket
    else:
        rgb_node = nodes.new('ShaderNodeRGB')
        output_socket = rgb_node.outputs['Color']
        color_val = None
        if input_socket.type == 'RGBA':
            color_val = input_socket.default_value
        elif input_socket.type == 'VALUE':
            color_val = (input_socket.default_value, input_socket.default_value, input_socket.default_value, 1)
        output_socket.default_value = color_val
    return output_socket

CHANNELS = ['Metallic', 'Roughness']

class EasyPBRBake(Operator):
    bl_idname = "easy_pbr.bake"
    bl_label = "Bake Textures"

    def execute(self, context):
        scn = context.scene
        obj = context.active_object

        # Get data from materials
        data = get_shader_data(obj.material_slots)
        if not data:
            self.report({'ERROR'}, 'Incorrect materials setup')
            return {'FINISHED', 'CANCELLED'}
        principled_shaders = data['PrincipledShaders']
        emission_shaders = data['EmissionShaders']

        # Replace materials
        materials = data['Materials']
        for i, ms in enumerate(obj.material_slots):
            ms.material = materials[i]

        texture_nodes = data['TextureNodes']

        # Bake albedo
        if scn.epbrb_enable_albedo:
            print('Baking albedo texture')

            image = get_image(scn.epbrb_albedo_name, scn, scn.epbrb_albedo_clear, scn.epbrb_albedo_clear_color, 'sRGB')

            # Set active texture in materials
            for tn in texture_nodes:
                tn.image = image

            # Connect Base Color to Emit shader
            for i, ms in enumerate(obj.material_slots):
                albedo_output = get_output_socket(principled_shaders[i], 'Base Color', ms.material.node_tree.nodes)
                ms.material.node_tree.links.new(albedo_output, emission_shaders[i].inputs['Color'], verify_limits = True)

            # Bake
            bpy.ops.object.bake(type = 'EMIT', width = scn.epbrb_x_res, height = scn.epbrb_y_res,
                                use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)

            # Save and clear image
            image.save()
            bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)

        # Metallic, roughness, ao
        if scn.epbrb_channel_pack:
            if scn.epbrb_enable_metallic or scn.epbrb_enable_roughness:
                # Bake packed textures
                print('Baking metallic, roughness channels')

                image = get_image(scn.epbrb_packed_name, scn, scn.epbrb_packed_clear, scn.epbrb_packed_clear_color, 'Linear')

                # Set active texture in materials
                for tn in texture_nodes:
                    tn.image = image

                # Connect channels
                for i, ms in enumerate(obj.material_slots):
                    combine_node = ms.material.node_tree.nodes.new('ShaderNodeCombineRGB')
                    ms.material.node_tree.links.new(combine_node.outputs['Image'], emission_shaders[i].inputs['Color'], verify_limits = True)
                    if scn.epbrb_enable_metallic:
                        metallic_output = get_output_socket(principled_shaders[i], 'Metallic', ms.material.node_tree.nodes)
                        ms.material.node_tree.links.new(metallic_output, combine_node.inputs[0], verify_limits = True)
                    if scn.epbrb_enable_roughness:
                        roughness_output = get_output_socket(principled_shaders[i], 'Roughness', ms.material.node_tree.nodes)
                        ms.material.node_tree.links.new(roughness_output, combine_node.inputs[1], verify_limits = True)

                # Bake
                bpy.ops.object.bake(type = 'EMIT', width = scn.epbrb_x_res, height = scn.epbrb_y_res,
                                    use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                    cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)

                # Save and clear image
                image.save()
                bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
        else:
            # Bake metallic
            if scn.epbrb_enable_metallic:
                print('Baking metallic texture')

                image = get_image(scn.epbrb_metallic_name, scn, scn.epbrb_metallic_clear, scn.epbrb_metallic_clear_color, 'Linear')

                # Set active texture in materials
                for tn in texture_nodes:
                    tn.image = image

                # Connect Base Color to Emit shader
                for i, ms in enumerate(obj.material_slots):
                    metallic_output = get_output_socket(principled_shaders[i], 'Metallic', ms.material.node_tree.nodes)
                    ms.material.node_tree.links.new(metallic_output, emission_shaders[i].inputs['Color'], verify_limits = True)

                # Bake
                bpy.ops.object.bake(type = 'EMIT', width = scn.epbrb_x_res, height = scn.epbrb_y_res,
                                    use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                    cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)

                # Save and clear image
                image.save()
                bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)

            # Bake roughness
            if scn.epbrb_enable_roughness:
                print('Baking roughness texture')

                image = get_image(scn.epbrb_roughness_name, scn, scn.epbrb_roughness_clear, scn.epbrb_roughness_clear_color, 'Linear')

                # Set active texture in materials
                for tn in texture_nodes:
                    tn.image = image

                # Connect Base Color to Emit shader
                for i, ms in enumerate(obj.material_slots):
                    roughness_output = get_output_socket(principled_shaders[i], 'Roughness', ms.material.node_tree.nodes)
                    ms.material.node_tree.links.new(roughness_output, emission_shaders[i].inputs['Color'], verify_limits = True)

                # Bake
                bpy.ops.object.bake(type = 'EMIT', width = scn.epbrb_x_res, height = scn.epbrb_y_res,
                                    use_clear = False, margin = scn.epbrb_margin, use_selected_to_active = scn.epbrb_selected_to_active,
                                    cage_extrusion = scn.epbrb_cage_extrusion, cage_object = scn.epbrb_cage_object)

                # Save and clear image
                image.save()
                bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)

        # Restore and clean materials
        or_materials = data['OriginalMaterials']
        for i, ms in enumerate(obj.material_slots):
            ms.material = or_materials[i]
            bpy.data.materials.remove(materials[i], do_unlink = True, do_id_user = True, do_ui_user = True)

        return {'FINISHED'}