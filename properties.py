import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, EnumProperty

class EasyPBRBakeProp(PropertyGroup):
    DEFAULT_NAME = "bake"

    def update_names(self, context):
        if self.autonames:
            self.albedo_name = self.base_name + '_albedo'
            self.packed_name = self.base_name + '_packed'
            self.metallic_name = self.base_name + '_metallic'
            self.roughness_name = self.base_name + '_roughness'
            self.ao_name = self.base_name + '_ao'
            self.normal_name = self.base_name + '_normal'
    
    autonames = BoolProperty(
        name = "Automatic Names", 
        description = "Automatically generate the names of the textures",
        default = True,
        update = update_names
    )

    dir_path = StringProperty(
        name = "Directory Path",
        description = "Directory where all the textures will be saved",
        default = "//",
        subtype = 'DIR_PATH'
    )

    base_name = StringProperty(
        name = "Base Name",
        description = "Base name for the textures when using automatic names",
        default = DEFAULT_NAME,
        update = update_names
    )

    x_res = IntProperty(
        name = "Resolution X",
        description = "Texture resolution in horizontal axis",
        default = 1024,
        subtype = 'PIXEL'
    )

    y_res = IntProperty(
        name = "Resolution Y",
        description = "Texture resolution in vertical axis",
        default = 1024,
        subtype = 'PIXEL'
    )

    margin = IntProperty(
        name = "Margin",
        description = "Extends the baked result as a post process filter",
        default = 16,
        subtype = 'PIXEL',
        min = 0,
        max = 64
    )

    selected_to_active = BoolProperty(
        name = 'Selected to Active',
        description = 'Bake shading on the surface of selected objects to the active object',
        default = False
    )

    use_cage = BoolProperty(
        name = 'Cage', 
        description = 'Cast rays to active object from a cage',
        default = False
    )

    cage_extrusion = FloatProperty(
        name = 'Extrusion',
        description = 'Distance to use for the inward ray cast when using selected to active',
        default = 0.0,
        min = 0.0,
        max = 1.0
    )

    cage_object = StringProperty(
        name = "Cage Object",
        description = "Object to use as cage instead of calculating the cage from the active object with cage extrusion",
        default = ""
    )

    ########### Albedo #######################
    enable_albedo = BoolProperty(
        name = 'Enable Albedo', 
        description = 'Generate albedo texture',
        default = False
    )

    albedo_name = StringProperty(
        name = "Texture Name",
        description = "Name for the albedo texture file",
        default = DEFAULT_NAME + '_albedo'
    )

    albedo_clear = BoolProperty(
        name = "Clear Image", 
        description = "Clear albedo image before baking",
        default = True
    )

    albedo_clear_color = FloatVectorProperty(
        name = 'Clear Color', 
        description = 'Albedo clear color',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (0.0, 0.0, 0.0, 1.0),
        subtype = 'COLOR_GAMMA'
    )

    ########### Packed #######################
    pack_channels = BoolProperty(
        name = 'Channel Packing', 
        description = 'Pack the metallic, roughness and ao bakes into a single image',
        default = False
    )

    packed_name = StringProperty(
        name = "Texture Name",
        description = "Name for the channel packed texture file",
        default = DEFAULT_NAME + '_packed'
    )

    packed_clear = BoolProperty(
        name = "Clear Image", 
        description = "Clear packed image before baking",
        default = True
    )

    packed_clear_color = FloatVectorProperty(
        name = 'Clear Color', 
        description = 'Packed texture clear color',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (0.0, 0.0, 0.0, 1.0),
        subtype = 'COLOR'
    )

    ########### Metallic #######################
    enable_metallic = BoolProperty(
        name = 'Enable Metallic', 
        description = 'Generate metallic texture',
        default = False
    )

    metallic_name = StringProperty(
        name = "Texture Name",
        description = "Name for the metallic texture file",
        default = DEFAULT_NAME + '_metallic'
    )

    metallic_clear = BoolProperty(
        name = "Clear Image", 
        description = "Clear metallic image before baking",
        default = True
    )

    metallic_clear_color = FloatVectorProperty(
        name = 'Clear Color', 
        description = 'Metallic clear color',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (0.0, 0.0, 0.0, 1.0),
        subtype = 'COLOR'
    )

    ########### Roughness #######################
    enable_roughness = BoolProperty(
        name = 'Enable Roughness', 
        description = 'Generate roughness texture',
        default = False
    )

    roughness_name = StringProperty(
        name = "Texture Name",
        description = "Name for the roughness texture file",
        default = DEFAULT_NAME + '_roughness'
    )

    roughness_clear = BoolProperty(
        name = "Clear Image", 
        description = "Clear roughness image before baking",
        default = True
    )

    roughness_clear_color = FloatVectorProperty(
        name = 'Clear Color', 
        description = 'Roughness clear color',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (0.0, 0.0, 0.0, 1.0),
        subtype = 'COLOR'
    )

    ########### Ambient Occlusion #######################
    enable_ao = BoolProperty(
        name = 'Enable Ambient Occlusion', 
        description = 'Generate ambient occlusion texture',
        default = False
    )

    ao_name = StringProperty(
        name = "Texture Name",
        description = "Name for the AO texture file",
        default = DEFAULT_NAME + '_ao'
    )

    ao_clear = BoolProperty(
        name = "Clear Image", 
        description = "Clear AO image before baking",
        default = True
    )

    ao_clear_color = FloatVectorProperty(
        name = 'Clear Color', 
        description = 'AO clear color',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (0.0, 0.0, 0.0, 1.0),
        subtype = 'COLOR'
    )

    ao_samples = IntProperty(
        name = "Samples",
        description = "Number of rays to trace per shader evaluation",
        default = 16,
        min = 1,
        max = 128
    )

    ao_distance = FloatProperty(
        name = 'Distance',
        description = 'Length of rays, defines how far away other faces give occlusion effect',
        default = 1.0,
        min = 0.0,
    )

    ########### Normal Map #######################
    enable_normal = BoolProperty(
        name = 'Enable Normal', 
        description = 'Generate normal map texture',
        default = False
    )

    normal_name = StringProperty(
        name = 'Texture Name',
        description = 'Name for the normal map texture file',
        default = DEFAULT_NAME + '_normal'
    )

    normal_clear = BoolProperty(
        name = 'Clear Image', 
        description = 'Clear normal map image before baking',
        default = True
    )

    normal_space = EnumProperty(
        items = [('OBJECT', 'Object', 'Bake the normals in object space'), ('TANGENT', 'Tangent', 'Bake the normals in tangent space')],
        name = 'Normal Space',
        description = 'Normal space used to bake',
        default = 'TANGENT'
    )