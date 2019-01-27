import bpy
from bpy.types import Operator

class EasyPBRBake(Operator):
    bl_idname = "object.easy_pbr_bake"
    bl_label = "Bake Textures"

    original_mats = []
    materials = []
    principled_shaders = []
    emission_shaders = []
    texture_nodes = []

    def set_bake_materials(self, mat_slots):
        """ Create new materials from the original ones and add necessary shader nodes """
        for ms in mat_slots:
            or_material = ms.material
            self.original_mats.append(or_material)
            material = or_material.copy()
            self.materials.append(material)
            nodes = material.node_tree.nodes
            for node in nodes:
                if node.bl_idname == 'ShaderNodeOutputMaterial':
                    links = node.inputs['Surface'].links
                    if len(links) == 0:
                        return False
                    if links[0].from_node.bl_idname != 'ShaderNodeBsdfPrincipled':
                        return False
                    self.principled_shaders.append(links[0].from_node)
                    emission_node = nodes.new('ShaderNodeEmission')
                    material.node_tree.links.new(emission_node.outputs[0], node.inputs['Surface'], verify_limits = True)
                    self.emission_shaders.append(emission_node)
                    tex_node = nodes.new('ShaderNodeTexImage')
                    nodes.active = tex_node
                    self.texture_nodes.append(tex_node)
                    break

        return True
    
    def clean_materials(self, mat_slots):
        """ Remove all created materials """
        for mat in self.materials:
            bpy.data.materials.remove(mat, do_unlink = True, do_id_user = True, do_ui_user = True)
        
        self.original_mats = []
        self.materials = []
        self.principled_shaders = []
        self.emission_shaders = []
        self.texture_nodes = []
    
    def get_image(self, name, props, clear, clear_color, colorspace):
        """ Return an image to bake to """
        file_path = self.ext_file_name(props.dir_path + name, 'png')
        image = None
        if clear or not self.file_exists(file_path):
            image = bpy.data.images.new(name, props.x_res, props.y_res, alpha = False)
            image.generated_color = clear_color
            image.colorspace_settings.name = colorspace
            image.file_format = 'PNG'
            image.filepath_raw = file_path 
        else:
            image = bpy.data.images.load(file_path, check_existing = False)
        return image
    
    def file_exists(self, file_path):
        try:
            file = open(file_path,'r')
            file.close()
            return True
        except:
            return False

    def ext_file_name(self, file_name, ext):
        parts = file_name.split('.')
        if len(parts) > 1:
            if parts[len(parts) - 1] != ext:
                return file_name + '.' + ext
            else:
                return file_name
        else:
            return file_name + '.' + ext

    def get_output_socket(self, shader, input_name, nodes):
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

    def execute(self, context):
        self.original_mats = []
        self.materials = []
        self.principled_shaders = []
        self.emission_shaders = []
        self.texture_nodes = []

        props = context.scene.easy_pbr_bake_props
        obj = context.active_object

        # Get data from materials
        if not self.set_bake_materials(obj.material_slots):
            self.clean_materials(obj.material_slots)
            self.report({'ERROR'}, 'Incorrect materials setup')
            return {'FINISHED', 'CANCELLED'}
        
        # Replace materials
        for i, ms in enumerate(obj.material_slots):
            ms.material = self.materials[i]

        # Bake albedo
        if props.enable_albedo:
            self.bake_albedo(props, obj.material_slots)
        
        # Bake packed textures
        if props.pack_channels:
            if props.enable_metallic or props.enable_roughness or props.enable_ao:
                self.bake_channels(props, obj.material_slots)
        else:
            # Bake metallic
            if props.enable_metallic:
                self.bake_metallic(props, obj.material_slots)

            # Bake roughness
            if props.enable_roughness:
                self.bake_roughness(props, obj.material_slots)
            
            # Bake ao
            if props.enable_ao:
                self.bake_ao(props, obj.material_slots)
        
        # Bake normals
        if props.enable_normal:
            self.bake_normal(props, obj.material_slots)

        # Restore and clean materials
        for i, ms in enumerate(obj.material_slots):
            ms.material = self.original_mats[i]
        self.clean_materials(obj.material_slots)

        return {'FINISHED'}
    
    def bake_albedo(self, props, mat_slots):
        print('Baking albedo texture')

        image = self.get_image(props.albedo_name, props, props.albedo_clear, props.albedo_clear_color, 'sRGB')
            
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect Base Color to Emit shader
        for i, ms in enumerate(mat_slots):
            albedo_output = self.get_output_socket(self.principled_shaders[i], 'Base Color', ms.material.node_tree.nodes)
            ms.material.node_tree.links.new(albedo_output, self.emission_shaders[i].inputs['Color'], verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'EMIT', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object)
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
    
    def bake_channels(self, props, mat_slots):
        print('Baking metallic, roughness channels')
            
        image = self.get_image(props.packed_name, props, props.packed_clear, props.packed_clear_color, 'Linear')
        
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect channels
        for i, ms in enumerate(mat_slots):
            combine_node = ms.material.node_tree.nodes.new('ShaderNodeCombineRGB')
            ms.material.node_tree.links.new(combine_node.outputs['Image'], self.emission_shaders[i].inputs['Color'], verify_limits = True)
            if props.enable_metallic:
                metallic_output = self.get_output_socket(self.principled_shaders[i], 'Metallic', ms.material.node_tree.nodes)
                ms.material.node_tree.links.new(metallic_output, combine_node.inputs[0], verify_limits = True)
            if props.enable_roughness:
                roughness_output = self.get_output_socket(self.principled_shaders[i], 'Roughness', ms.material.node_tree.nodes)
                ms.material.node_tree.links.new(roughness_output, combine_node.inputs[1], verify_limits = True)
            if props.enable_ao:
                ao_node = ms.material.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
                ao_node.samples = props.ao_samples
                ao_node.inputs[1].default_value = props.ao_distance
                ao_output = ao_node.outputs[1]
                ms.material.node_tree.links.new(ao_output,  combine_node.inputs[1], verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'EMIT', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object)
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
    
    def bake_metallic(self, props, mat_slots):
        print('Baking metallic texture')

        image = self.get_image(props.metallic_name, props, props.metallic_clear, props.metallic_clear_color, 'Linear')
            
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect Base Color to Emit shader
        for i, ms in enumerate(mat_slots):
            metallic_output = self.get_output_socket(self.principled_shaders[i], 'Metallic', ms.material.node_tree.nodes)
            ms.material.node_tree.links.new(metallic_output, self.emission_shaders[i].inputs['Color'], verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'EMIT', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object)
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
    
    def bake_roughness(self, props, mat_slots):
        print('Baking roughness texture')

        image = self.get_image(props.roughness_name, props, props.roughness_clear, props.roughness_clear_color, 'Linear')
            
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect Base Color to Emit shader
        for i, ms in enumerate(mat_slots):
            roughness_output = self.get_output_socket(self.principled_shaders[i], 'Roughness', ms.material.node_tree.nodes)
            ms.material.node_tree.links.new(roughness_output, self.emission_shaders[i].inputs['Color'], verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'EMIT', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object)
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
    
    def bake_ao(self, props, mat_slots):
        print('Baking ao texture')

        image = self.get_image(props.ao_name, props, props.ao_clear, props.ao_clear_color, 'Linear')
            
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect Base Color to Emit shader
        for i, ms in enumerate(mat_slots):
            ao_node = ms.material.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
            ao_node.samples = props.ao_samples
            ao_node.inputs[1].default_value = props.ao_distance
            ao_output = ao_node.outputs[1]
            ms.material.node_tree.links.new(ao_output, self.emission_shaders[i].inputs['Color'], verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'EMIT', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object)
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
    
    def bake_normal(self, props, mat_slots):
        print('Baking normal map')

        image = self.get_image(props.normal_name, props, props.normal_clear, (0.5, 0.5, 1.0, 1.0), 'Linear')
            
        # Set active texture in materials
        for tn in self.texture_nodes:
            tn.image = image
        
        # Connect Base Color to Emit shader
        for i, ms in enumerate(mat_slots):
            shader_output = self.principled_shaders[i].outputs[0]
            mo_input = self.emission_shaders[i].outputs[0].links[0].to_socket
            ms.material.node_tree.links.new(shader_output, mo_input, verify_limits = True)
        
        # Bake
        bpy.ops.object.bake(type = 'NORMAL', width = props.x_res, height = props.y_res,
                            use_clear = False, margin = props.margin, use_selected_to_active = props.selected_to_active,
                            cage_extrusion = props.cage_extrusion, cage_object = props.cage_object, normal_space = props.normal_space,
                            normal_r = 'POS_X', normal_g = 'POS_Y', normal_b = 'POS_Z')
        
        # Save and clear image
        image.save()
        bpy.data.images.remove(image, do_unlink = True, do_id_user = True, do_ui_user = True)
