# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Set File output Nodes",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "add some tool to handle view layers for rendering",
    "location": "PROPERTIES > OUTPUT",
    "doc_url": "",
    "warning": "",
    "category": "View Layers",
    "blender": (2,90,0),
    "version": (1,0,53)
}

# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"]).replace(",",".").replace("(","").replace(")","")

### import modules ###
import bpy
import random

### define global variables ###
debug_mode = False
separator = "-" * 20
precomp_scene_suffixe = "_Pre-Compositing"

### create property ###
class VLTOOLBOX_properties (bpy.types.PropertyGroup):
    selection_options_prop = [("ALL SCENES","ALL SCENES","ALL SCENES",0),
                                ("CURRENT SCENE","CURRENT SCENE","CURRENT SCENE",1),
                                ("ALL SCENES WITH CURRENT SETTINGS","ALL SCENES WITH CURRENT SETTINGS","ALL SCENES WITH CURRENT SETTINGS",2)
                                ]
    ## outputs
    outputs_scenes_selection : bpy.props.EnumProperty (items = selection_options_prop,name = "Scenes ?",description = "choose selection type",default=1)
    outputs_alpha_solo : bpy.props.BoolProperty (default=False,name="Render Alpha separatly",description="if unchecked, the alpha will be embeded in the main image file")
    output_reset_options = [("RESET ALL TREE","RESET ALL TREE","RESET ALL TREE",0),
                                ("UPDATE OUTPUTS","UPDATE OUTPUTS","UPDATE OUTPUTS",1),
                                ("ONLY UPDATE PATH","ONLY UPDATE PATH","ONLY UPDATE PATH",2),
                                #("UNUSED NODES","UNUSED NODES","UNUSED NODES",2),
                                #("NOTHING","NOTHING","NOTHING",3)
                                ]
    outputs_reset_selection : bpy.props.EnumProperty (items = output_reset_options,name = "",description = "Nodes reset",default=0)
    #outputs_reset : bpy.props.BoolProperty (default=False,name="Reset Output Nodes",description="if checked, all the outputs will be wiped before recreated (recommanded to avoid issues)")
    #outputs_clean_nodeslinks : bpy.props.BoolProperty (default=True,name="Clean Nodes Links",description="if checked, all the links between view layers and outputs will be reset")
    #outputs_path_prop : bpy.props.BoolProperty (default=True,name="Update path",description="if checked, only the outputs path will be update ")
    outputs_usefilename : bpy.props.BoolProperty (default=True,name="Use scene filename",description="if checked, the filename will be use as a folder path")
    outputs_sort_options = [('Ascending','Ascending','Ascending',"SORT_ASC",0),
                            ('Descending','Descending','Descending',"SORT_DESC",1),
                            ('Unsorted','Unsorted','Unsorted',2),
                            ]
    outputs_sort_prop : bpy.props.EnumProperty (items = outputs_sort_options,name = "Layers sort",description = "choose selection type",default=0)
    outputs_prefix_prop : bpy.props.StringProperty(name="Pass Prefix",default="",description="")
    layer_folder_prop : bpy.props.BoolProperty (default=True,name="One folder per layer",description="if checked, images sequences of each layer will be stored in a different folder")
    outputs_folder_prop : bpy.props.BoolProperty (default=False,name="One folder per output",description="if checked, images sequences of each passes will be stored in folders")
    output_separator_options = [("None","None","None",0),("_","_","_",1),("-","-","-",2),(".",".",".",3)]
    output_filename_end_prop : bpy.props.EnumProperty (items = output_separator_options,name = "Filename end",description = 'symbol to separate the name from the frame number.\n i.e: separator = "." gives "filename.0000", separator = "None" gives "filename0000" ' ,default=3)
    outputs_corresponding_prop : bpy.props.StringProperty(name="Translation",default="Image=rgba",description='translate field a to field b, separated by ",". I.E. "Image=rgba,Alpha=alpha"')
    clear_unusedSockets_prop : bpy.props.BoolProperty (default=False,name="Clear Unused Output",description="if checked, clear user unused outputs")
    use_layerName_in_pass_prop : bpy.props.BoolProperty (default=False,name="Use Layer Name",description="if checked, the view layer name will be added in each pass name")

    ## precomp
    precomp_bg_under_prop : bpy.props.BoolProperty(default=False,name="",description="")
    precomp_bg_img_prop : bpy.props.PointerProperty(type=bpy.types.Image, name="BG under", description="")
    precomp_freestyle_prop : bpy.props.BoolProperty (default=True,name="Freestyle Over",description="if freestyle on separate pass, freestyle over")
    
### create panels ###
# create panel UPPER_PT_lower
# for view 3D
class VIVLTOOLBOX_PT_filesoutput(bpy.types.Panel):
    bl_label = f"MANAGE FILES OUTPUT - {Addon_Version}"
    bl_idname = "VIVLTOOLBOX_PT_filesoutput"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'output'
    #bl_parent_id = "RENDER_PT_output"
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='NODETREE')

    def draw(self, context):
        viewLayerToolbox_props = context.scene.viewLayerToolbox_props
        layout = self.layout
        bigbox = layout.box()
        split = bigbox.split(factor=.6)
        box = split.box()
        box.operator("vltoolbox.createnodesoutput",text="Update Layers outputs",emboss=True,depress=False,icon="OUTPUT")
        #row = box.row()
        box.operator("vltoolbox.createprecomp",text="Create View Layers Pre-Comp Tree",emboss=True,depress=False,icon="NODE")
        #box.label(text="")
        # node tree options
        box = split.box()
        row = box.row()
        row.label(text="Updates:")
        row = box.row()
        row.prop(viewLayerToolbox_props, "outputs_reset_selection")
        # row = box.row()
        # row.prop(viewLayerToolbox_props, "outputs_reset")
        # row = box.row()
        # row.prop(viewLayerToolbox_props, "clear_unusedSockets_prop")
        # misc options
        box = layout.box()
        box.prop(viewLayerToolbox_props, "outputs_sort_prop")
        #row = box.row()
        box.prop(viewLayerToolbox_props, "outputs_scenes_selection")

class VIVLTOOLBOX_PT_filesoutputoptions(bpy.types.Panel):
    bl_label = "Output Options"
    bl_idname = "VIVLTOOLBOX_PT_filesoutputoptions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'output'
    bl_parent_id = "VIVLTOOLBOX_PT_filesoutput"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='OPTIONS')

    def draw(self, context):
        viewLayerToolbox_props = context.scene.viewLayerToolbox_props

        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(viewLayerToolbox_props, "outputs_usefilename")
        row.prop(viewLayerToolbox_props, "output_filename_end_prop")
        row = box.row()
        row.prop(viewLayerToolbox_props, "outputs_prefix_prop")
        row = box.row()
        row.prop(viewLayerToolbox_props, "layer_folder_prop")
        row.prop(viewLayerToolbox_props, "outputs_folder_prop")
        row = box.row()
        row.prop(viewLayerToolbox_props, "outputs_alpha_solo")
        row.prop(viewLayerToolbox_props, "use_layerName_in_pass_prop")
        box = layout.box()
        row = box.row()
        row.prop(viewLayerToolbox_props, "outputs_corresponding_prop")
        

class VIVLTOOLBOX_PT_precompoptions(bpy.types.Panel):
    bl_label = "Precomp Options"
    bl_idname = "VIVLTOOLBOX_PT_precompoptions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'output'
    bl_parent_id = "VIVLTOOLBOX_PT_filesoutput"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='OPTIONS')

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        viewLayerToolbox_props = context.scene.viewLayerToolbox_props
        row = col.row()
        split = row.split(factor = .1)
        split.prop(viewLayerToolbox_props, "precomp_bg_under_prop")
        split.active = viewLayerToolbox_props.precomp_bg_under_prop
        split.prop(viewLayerToolbox_props, "precomp_bg_img_prop")
        row = col.row()
        row.prop(viewLayerToolbox_props, "precomp_freestyle_prop")
        #
        #row.prop(viewLayerToolbox_props, "precomp_input_prop")
        

### create functions ###
# create function > create files output
def list_renderlayers(selected_scene,sort_option):
    ## variables
    selected_scene = selected_scene
    sort_option = sort_option
    selected_scene_layer_list = []
    
    ## create layer list from the target scene
    for layer in bpy.data.scenes[selected_scene.name].view_layers:
        selected_scene_layer_list.append(layer)
    # sort layers regarding name
    scene_layerName_list = []
    for layer in selected_scene_layer_list:
        scene_layerName_list.append(layer.name)
    if sort_option == 'Ascending':
        scene_layerName_list.sort()
    elif sort_option == 'Descending':
        scene_layerName_list.sort(reverse=True)
    # recrate the list
    selected_scene_layer_list = []
    for layer in scene_layerName_list:
        selected_scene_layer_list.append(selected_scene.view_layers[layer])
    return selected_scene_layer_list

def list_renderlayers_nodes(selected_scene,sort_option):
    ## variables
    selected_scene = selected_scene
    node_tree = selected_scene.node_tree

    renderLayer_nodes_list = []
    for node in node_tree.nodes:
        if node.type == "R_LAYERS" and node.mute == False:
            renderLayer_nodes_list.append(node)
    #print(f"{renderLayer_nodes_list=}")
    # sort render layers regarding name
    renderLayer_nodes_names_list = []
    for node in renderLayer_nodes_list:
        renderLayer_nodes_names_list.append(node.name)
    if sort_option == 'Ascending':
        renderLayer_nodes_names_list.sort()
    elif sort_option == 'Descending':
        renderLayer_nodes_names_list.sort(reverse=True)
    #print(f"{renderLayer_nodes_names_list=}")
    # recrate the list
    renderLayer_nodes_list = []
    for node in renderLayer_nodes_names_list:
        renderLayer_nodes_list.append(node_tree.nodes[node])
    #print(f"{renderLayer_nodes_list}")
    return renderLayer_nodes_list

def create_renderlayers_nodes(selected_scene,selected_scene_layer_list):
    ## variables
    selected_scene = selected_scene
    selected_scene_layer_list = selected_scene_layer_list
    outputs_reset_selection = bpy.context.scene.viewLayerToolbox_props.outputs_reset_selection

    output_enabled_dict = {}
    
    bpy.data.scenes[selected_scene.name].use_nodes = True
    compo_tree = bpy.data.scenes[selected_scene.name].node_tree

    ## create render layers
    iter_node = 0
    for layer in selected_scene_layer_list:
        ## generate variables
        render_node_name = f"Render Layers - {layer.name}"
        #print(f"{render_node_name=}")
        node_color = (random.uniform(0,1), random.uniform(0,1), random.uniform(0,1))
        x_coord = 0

        ## create layer node if needed
        if render_node_name not in compo_tree.nodes:
            last_render_layer_node = compo_tree.nodes.new(type="CompositorNodeRLayers").name
            compo_tree.nodes[last_render_layer_node].scene = selected_scene # set the scene name 
            compo_tree.nodes[last_render_layer_node].layer = layer.name
            compo_tree.nodes[last_render_layer_node].name = render_node_name
        compo_tree.nodes[render_node_name].label = render_node_name        
        # manage color node
        if compo_tree.nodes[render_node_name].use_custom_color == False:
            compo_tree.nodes[render_node_name].use_custom_color = True
            compo_tree.nodes[render_node_name].color = node_color
        
        ## check number of outputs (= passes) for each layer node
        output_number = 0
        output_enabled_list = []
        for key, output in compo_tree.nodes[render_node_name].outputs.items():
            if getattr(output, 'enabled', False):
                output_enabled_list.append(key)
                output_number += 1    
        output_enabled_dict[render_node_name] = output_enabled_list

        ## move render nodes
        # set coordinates
        if iter_node == 0:
            y_coord = previous_node_size = 0
        else:
            y_coord = previous_node_size*-1
        
        # store the node size for better layout
        if output_number>3:
            offset_outputs = (output_number-3)*20
        else:
            offset_outputs = 0
        previous_node_size += 400 + offset_outputs
        
        # move render layers node
        compo_tree.nodes[render_node_name].location = (x_coord,y_coord)
        
        ## if not used for rendering => mute node
        if layer.use == False:
            compo_tree.nodes[render_node_name].mute = True
        else:
            compo_tree.nodes[render_node_name].mute = False
        
        iter_node += 1 

    #print(f"{output_enabled_dict}")
    return output_enabled_dict

def create_outputsNodes(selected_scene,selected_scene_layer_list,output_enabled_dict):
    ## variables
    selected_scene = selected_scene
    selected_scene_layer_list = selected_scene_layer_list
    output_enabled_dict = output_enabled_dict
    
    bpy.data.scenes[selected_scene.name].use_nodes = True
    compo_tree = bpy.data.scenes[selected_scene.name].node_tree
    outputs_folder_prop = bpy.context.scene.viewLayerToolbox_props.outputs_folder_prop
    layer_folder_prop = bpy.context.scene.viewLayerToolbox_props.layer_folder_prop
    outputs_prefix_prop = bpy.context.scene.viewLayerToolbox_props.outputs_prefix_prop
    output_filename_end_prop = bpy.context.scene.viewLayerToolbox_props.output_filename_end_prop
    outputs_corresponding_prop = bpy.context.scene.viewLayerToolbox_props.outputs_corresponding_prop
    clear_unusedSockets_prop = bpy.context.scene.viewLayerToolbox_props.clear_unusedSockets_prop
    use_layerName_in_pass_prop = bpy.context.scene.viewLayerToolbox_props.use_layerName_in_pass_prop
    outputs_reset_selection = bpy.context.scene.viewLayerToolbox_props.outputs_reset_selection

    outputs_corresponding_list = outputs_corresponding_prop.split(',')
    outputs_corresponding_dict = {}
    for corres in outputs_corresponding_list:
        corres = corres.replace(" ","")
        corres_split = corres.split("=")
        outputs_corresponding_dict[corres_split[0]] = corres_split[-1]

    # remove main output namefile to keep only filepath : 
    main_file_output = selected_scene.render.filepath
    possible_separator = ["\\"]
    if bpy.context.scene.viewLayerToolbox_props.outputs_usefilename == False:
        for separator in possible_separator:
            if separator in main_file_output:
                main_file_output = main_file_output.split(separator)
                file_name = main_file_output[-1]
                main_file_output.remove(file_name)
                main_file_output = separator.join(main_file_output)
                main_file_output = f"{main_file_output}{separator}"

    ## create outputs nodes
    iter_node = 0
    for layer in selected_scene_layer_list: 
        # variables
        render_node_name = f"Render Layers - {layer.name}"
        output_node_name = f"File Output - {layer.name}"
        
        if outputs_reset_selection!="ONLY UPDATE PATH":
            # check if file output node exists
            if output_node_name not in compo_tree.nodes:
                # create file output
                last_output_node = compo_tree.nodes.new(type="CompositorNodeOutputFile").name
                compo_tree.nodes[last_output_node].name = output_node_name
                new_output = True
            else:
                new_output = False
            compo_tree.nodes[output_node_name].label = output_node_name
            ## customise node regarding to render output
            # move for more readability
            if new_output:
                compo_tree.nodes[output_node_name].location[0] = 400
                compo_tree.nodes[output_node_name].width = (900)
            compo_tree.nodes[output_node_name].location[1] = compo_tree.nodes[render_node_name].location[1] # always align output to render layer
            compo_tree.nodes[output_node_name].use_custom_color = True
            compo_tree.nodes[output_node_name].color = compo_tree.nodes[render_node_name].color # give the same color as render layer node
            compo_tree.nodes[output_node_name].mute = compo_tree.nodes[render_node_name].mute # check if mute
            compo_tree.nodes[output_node_name].format.file_format = selected_scene.render.image_settings.file_format
            compo_tree.nodes[output_node_name].format.color_mode = selected_scene.render.image_settings.color_mode
            compo_tree.nodes[output_node_name].format.color_depth = selected_scene.render.image_settings.color_depth
            compo_tree.nodes[output_node_name].format.compression = selected_scene.render.image_settings.compression
        else:
            new_output = False
        # update base path
        if layer_folder_prop:
            base_path = compo_tree.nodes[output_node_name].base_path = f"{main_file_output}\{layer.name}"
        else:
            base_path = compo_tree.nodes[output_node_name].base_path = f"{main_file_output}"
        
        # the view layer name will be added in each pass name
        if use_layerName_in_pass_prop:
            layername = layer.name
        else:
            layername = ""

        ## create inputs in file outputs node regarding view layer
        if new_output or outputs_reset_selection == "UPDATE OUTPUTS":
            compo_tree.nodes[output_node_name].inputs.clear()
            output_enabled_list = output_enabled_dict[render_node_name]
            for output in output_enabled_list:
                    output_slot = output
                    if output in outputs_corresponding_dict.keys():
                        output = outputs_corresponding_dict[output]
                    if layer_folder_prop:
                        pass_name = f"{output}"
                    else:
                        pass_name = f"{layer.name}_{output}" 
                    # if output == "Image":
                    #     pass_name = f"rgba"
                    # else:
                    #     pass_name = f"{output}"
                    if outputs_folder_prop:
                        input_slot = f"{outputs_prefix_prop}{layername}_{pass_name}\\{outputs_prefix_prop}{pass_name}{output_filename_end_prop}"
                    else:
                        input_slot = f"{outputs_prefix_prop}{layername}_{pass_name}{output_filename_end_prop}"
                    compo_tree.nodes[output_node_name].layer_slots.new(input_slot) # "." is for better readability in files
                    if bpy.context.scene.viewLayerToolbox_props.outputs_alpha_solo == True or bpy.context.scene.viewLayerToolbox_props.outputs_alpha_solo == False and output != "Alpha":
                        compo_tree.links.new(compo_tree.nodes[render_node_name].outputs[output_slot],compo_tree.nodes[output_node_name].inputs[input_slot])

        # clean unused output
        if clear_unusedSockets_prop:
            for input in compo_tree.nodes[output_node_name].inputs:
                if len(input.links) == 0:
                    compo_tree.nodes[output_node_name].inputs.remove(input)
        
            #{outputs_prefix_prop}


### create operators ###        
class VLTOOLBOX_OT_createnodesoutput(bpy.types.Operator):
    bl_idname = "vltoolbox.createnodesoutput"
    bl_label = Addon_Name + "create files output"
    bl_description = "create files output node in compositing module for each view layer"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} {separator} \n")

        sort_option = bpy.context.scene.viewLayerToolbox_props.outputs_sort_prop

        # make it for all scenes or only current
        work_scene = bpy.context.scene

        # create scene list to process
        scenes_list = []
        if bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "ALL SCENES":
            for scene in bpy.data.scenes:
                scenes_list.append(scene)
        elif bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
            for scene in bpy.data.scenes:
                scene.viewLayerToolbox_props.outputs_scenes_selection = work_scene.viewLayerToolbox_props.outputs_scenes_selection
                scene.viewLayerToolbox_props.outputs_alpha_solo = work_scene.viewLayerToolbox_props.outputs_alpha_solo
                scene.viewLayerToolbox_props.outputs_reset_selection = work_scene.viewLayerToolbox_props.outputs_reset_selection
                #scene.viewLayerToolbox_props.outputs_clean_nodeslinks = work_scene.viewLayerToolbox_props.outputs_clean_nodeslinks
                scene.viewLayerToolbox_props.outputs_usefilename = work_scene.viewLayerToolbox_props.outputs_usefilename
                scenes_list.append(scene)
        elif bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "CURRENT SCENE":
            scenes_list.append(work_scene)
        
        #print(f"{scenes_list=}")
        # process
        for scene in scenes_list:
            if precomp_scene_suffixe not in bpy.context.scene.name:
                #if bpy.context.scene.use_nodes: # check if comp tree is on
                #bpy.context.window.scene = scene # switch scene to well create render node (it depends of the current scene)
                if scene.viewLayerToolbox_props.outputs_reset_selection == "RESET ALL TREE":
                    scene.node_tree.nodes.clear()
                # list all render layers
                selected_scene_layer_list = list_renderlayers(work_scene,sort_option)
                # create render layers
                output_enabled_dict = create_renderlayers_nodes(work_scene,selected_scene_layer_list)
                # create output nodes
                create_outputsNodes(work_scene,selected_scene_layer_list,output_enabled_dict)
                bpy.context.window.scene = work_scene # switch back to user scene work
                #print(" --- scene finished --- ")

        return {"FINISHED"}

class VLTOOLBOX_OT_createprecomp(bpy.types.Operator):
    bl_idname = "vltoolbox.createprecomp"
    bl_label = Addon_Name + "Create Pre-Comp Tree scene"
    bl_description = "create a pre compositing scene from render layer in scenes. \n /!\ You need to have render once at least one frame per layer to make it works ! /!\ "
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} {separator} \n")
        
        work_scene = bpy.context.scene
        sort_option = work_scene.viewLayerToolbox_props.outputs_sort_prop
        precomp_bg_under_prop = work_scene.viewLayerToolbox_props.precomp_bg_under_prop
        precomp_bg_img_prop = work_scene.viewLayerToolbox_props.precomp_bg_img_prop
        precomp_freestyle_prop = work_scene.viewLayerToolbox_props.precomp_freestyle_prop
        
        # create scene list to process
        scenes_list = []
        if bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "ALL SCENES":
            for scene in bpy.data.scenes:
                scenes_list.append(scene)
        elif bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
            for scene in bpy.data.scenes:
                scene.viewLayerToolbox_props.outputs_scenes_selection = work_scene.viewLayerToolbox_props.outputs_scenes_selection
                scene.viewLayerToolbox_props.outputs_reset_selection = work_scene.viewLayerToolbox_props.outputs_reset_selection
                scenes_list.append(scene)
        elif bpy.context.scene.viewLayerToolbox_props.outputs_scenes_selection == "CURRENT SCENE":
            scenes_list.append(work_scene)

        #print(f"{scenes_list=}")
        # process
        for scene in scenes_list:
            scene_name = scene.name
            bpy.data.scenes[scene_name].use_nodes = True
            node_tree = bpy.data.scenes[scene_name].node_tree
            if len(node_tree.nodes)==2: # in case of it's a new node tree, renderlayer + composite node are in
                node_tree.nodes.clear()
            if bpy.context.scene.viewLayerToolbox_props.outputs_reset_selection == "RESET ALL TREE":
                node_tree.nodes.clear()
            # list all render layers
            selected_scene_layer_list = list_renderlayers(work_scene,sort_option)
            # create render layers
            output_enabled_dict = create_renderlayers_nodes(work_scene,selected_scene_layer_list)
            # create output nodes
            
            ## create clean list (by alphabatical order) of render layer nodes
            renderLayer_nodes_list = list_renderlayers_nodes(scene,sort_option)
            print(f"{renderLayer_nodes_list=}")

            ### create alpha over node tree
            name_suffix = "_automatic"
            iter = 0
            location_x = 2000
            location_x_add = 300
            node_alphaOver_list = []
            #print(f"{work_scene.viewLayerToolbox_props.precomp_input_prop=}")
            for node in renderLayer_nodes_list:
                if precomp_freestyle_prop and scene.render.use_freestyle and bpy.context.scene.view_layers[-1].freestyle_settings.as_render_pass: # be sure freestyle will be created
                    # add line on top of color with an alpha over
                    node_alphaOverFS_name = node_tree.nodes.new(type="CompositorNodeAlphaOver").name
                    node_alphaOverFS = node_tree.nodes[node_alphaOverFS_name]
                    node_alphaOverFS.name = f"Alpha_Line{iter}"
                    node_alphaOverFS.location[0] = 1200
                    node_alphaOverFS.location[1] = node.location[1]
                    node_tree.links.new(node.outputs["Image"],node_tree.nodes[node_alphaOverFS.name].inputs[1])
                    node_tree.links.new(node.outputs["Freestyle"],node_tree.nodes[node_alphaOverFS.name].inputs[2])
                    node = node_alphaOverFS
                if iter != 1: # check if alpha over is needed
                    node_alphaOver = node_tree.nodes.new(type="CompositorNodeAlphaOver").name
                    node_alphaOver_name = f"Alpha Over.{str(iter).zfill(3)}{name_suffix}"
                    node_tree.nodes[node_alphaOver].name = node_alphaOver_name
                    #print(node_alphaOver_name)
                    node_tree.nodes[node_alphaOver_name].location[0] = location_x
                    node_alphaOver_list.append(node_alphaOver_name)
                    location_x += location_x_add
                if iter == 0:
                    if precomp_bg_under_prop and precomp_bg_img_prop!= None:
                        # create bg_node 
                        bg_node_name = "BG_under"
                        if bg_node_name not in node_tree.nodes:
                            last_render_layer_node = node_tree.nodes.new(type="CompositorNodeImage").name
                            bg_node = node_tree.nodes[last_render_layer_node]
                            bg_node.image = bpy.data.images[precomp_freestyle_prop]
                            bg_node.name = bg_node_name
                            bg_node.location[0] = 0
                            bg_node.location[1] = 500
                            # add alpha for the BG with alpha over
                        bg_node = node_tree.nodes[bg_node_name]
                        node_alphaOverBG_name = "Alpha_BG"
                        if node_alphaOverBG_name not in node_tree.nodes:
                            node_alphaOverBG_tmpname = node_tree.nodes.new(type="CompositorNodeAlphaOver").name
                            node_alphaOverBG = node_tree.nodes[node_alphaOverBG_tmpname]
                            node_alphaOverBG.name = node_alphaOverBG_name
                            node_alphaOverBG.location[0] = 400*2
                            node_alphaOverBG.location[1] = bg_node.location[1]
                        node_alphaOverBG = node_tree.nodes[node_alphaOverBG_name]
                        node_tree.links.new(node_tree.nodes[bg_node.name].outputs["Image"],node_alphaOverBG.inputs[1])
                        node_tree.links.new(node_tree.nodes[node.name].outputs["Image"],node_alphaOverBG.inputs[2])
                        node_tree.links.new(node_tree.nodes[node_alphaOverBG.name].outputs["Image"],node_tree.nodes[node_alphaOver_name].inputs[1])
                    else:
                        node_tree.links.new(node_tree.nodes[node.name].outputs["Image"],node_tree.nodes[node_alphaOver_name].inputs[1])
                        if len(renderLayer_nodes_list)==1:
                            node_tree.nodes[node_alphaOver_name].mute = True
                else:
                    node_tree.links.new(node_tree.nodes[node.name].outputs["Image"],node_tree.nodes[node_alphaOver_name].inputs[2])
                    if iter != 1:
                        node_tree.links.new(node_tree.nodes[node_alphaOver_list[iter-2]].outputs["Image"],node_tree.nodes[node_alphaOver_name].inputs[1])                    
                iter+=1
            #print(f"alpha nodes created : {node_alphaOver_list}")
            
            # create final composite node
            if "Composite" in node_tree.nodes.keys():
                    node_tree.nodes.remove(node_tree.nodes["Composite"])
            if "Viewer" in node_tree.nodes.keys():
                node_tree.nodes.remove(node_tree.nodes["Viewer"])
            
            if len(renderLayer_nodes_list)>0: # check lengh of list to avoid errors
                node_composite = node_tree.nodes.new(type="CompositorNodeComposite").name
                node_composite_named = f"{node_composite}{name_suffix}"
                node_tree.nodes[node_composite].name = node_composite_named
                node_tree.nodes[node_composite_named].location = (location_x, 100)
                node_tree.links.new(node_tree.nodes[node_alphaOver_list[-1]].outputs["Image"],node_tree.nodes[node_composite_named].inputs[0])                    
                # create viewer node
                
                node_viewer = node_tree.nodes.new(type="CompositorNodeViewer").name
                node_viewer_named = f"{node_viewer}{name_suffix}"
                node_tree.nodes[node_viewer].name = node_viewer_named
                node_tree.nodes[node_viewer_named].location = (location_x, -100)
                node_tree.links.new(node_tree.nodes[node_alphaOver_list[-1]].outputs["Image"],node_tree.nodes[node_viewer_named].inputs[0])                    

        # clean useless nodes
        for node in node_tree.nodes:
            input_used = 0
            if node.type == "ALPHAOVER" or node.type == "COMPOSITE" or node.type == "VIEWER":
                for node_input in  node.inputs:
                    if node_input.is_linked == True:
                        input_used += 1
                if input_used == 0:
                    node_tree.nodes.remove(node)

        #print(iter_node)
        bpy.context.window.scene = work_scene
        
        #print(f"{Addon_Name} done on : {nodes_created_list} \n")
        print(f"\n {separator} {Addon_Name} Finished {separator} \n")
        return {"FINISHED"}

# list all classes
classes = (
    VLTOOLBOX_properties,
    VIVLTOOLBOX_PT_filesoutput,
    VIVLTOOLBOX_PT_filesoutputoptions,
    VIVLTOOLBOX_PT_precompoptions,
    VLTOOLBOX_OT_createnodesoutput,
    VLTOOLBOX_OT_createprecomp,
    )

# register classes
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.viewLayerToolbox_props = bpy.props.PointerProperty (type = VLTOOLBOX_properties)

#unregister classes 
def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.viewLayerToolbox_props
        