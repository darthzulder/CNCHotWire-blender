# ADD-ON
####################################################

bl_info = {
    "name": "CNC HotWire Preparetion",
    "description": "Change origin Position ",
    "author": "nbravo",
    "version": (1, 2),
    "blender": (2, 93, 1),
    "location": "View3D > UI",
    "warning":"(in ALFA production)",
    "doc_url":"",
    "category": "User"
}

import bpy
import bmesh
import math
import re
from mathutils import Vector
#from . import funcs
import os, errno
#dir = os.path.dirname(bpy.data.filepath)
#print(f"------->{dir}")
#funcs = bpy.data.texts["funcs.py"].as_module()

#Funciones
class funcs():

    # meters
    foam_block_x = 1.410
    foam_block_y = 0.980
    foam_block_z = 1.180

    cut_thickness = 0.02

    wood_total_heigh = 0.042 + 8/1000
    wood_total_width = 0.141 + 8/1000
    wood_total_depth = 4.347

    volume_total_irregular = 0
    volume_total_cubes = 1
    quantity_cubes = 0

    def __init__(self):
        self.select_before = None

    def setSizeBlock(self,context, x, y, z):
        # Actualiza los valores introducidos por el usuario
        self.foam_block_x = float(x)
        self.foam_block_y = float(y)
        self.foam_block_z = float(z)

        context.scene.my_text_settings.my_text_property_x = ""
        context.scene.my_text_settings.my_text_property_y = ""
        context.scene.my_text_settings.my_text_property_z = ""

        print(f"Valores introducidos: X={x}, Y={y}, Z={z}")

    def change_origin (self):
        #print(f"-------change_origin>{dir}")
        # store the location of current 3d cursor
        saved_location = bpy.context.scene.cursor.location.xyz   # returns a vector
        
        
        # get object
        selected_object = bpy.context.active_object
        # get object coordinates
        coordinates = selected_object.location
        
        # get new origin coordinates
        location_X = coordinates.x
        location_Y = coordinates.y
        location_Z = coordinates.z
        
        # IN METERS
        
        foam_size_X = 1.410
        foam_size_Y = 0.980
        foam_size_Z = 1.180/2

        cnc_size_X = 2.150
        cnc_size_Y = 2.095
        cnc_size_Z = 1.250
        scale = 1
        dist_X_center = 1.137 #distance X from bootom to center
        
        cnc_center_X = ((cnc_size_X/2)-dist_X_center)
        cnc_center_Y = cnc_size_Y/2
        cnc_center_Z = 0
        
        # give 3dcursor new coordinates for the primitive cube
        bpy.context.scene.cursor.location =(0,0,cnc_size_Z/2)
        
        # create primitive cube as AreaCNC
        bpy.ops.mesh.primitive_cube_add(size=scale)
        AreaCNC = bpy.context.object        
        AreaCNC.dimensions = (cnc_size_X, cnc_size_Y, cnc_size_Z)
        bpy.ops.object.transform_apply(scale=True)
        
        # change cursor location
        bpy.context.scene.cursor.location =(cnc_center_X,0,0)
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # move the cube AreaCNC
        AreaCNC.location = (location_X, location_Y, location_Z)

        # create primitive cube as foamBlock
        # change cursor location
        bpy.context.scene.cursor.location =(0,0,0)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        foamBlock = bpy.context.object        
        foamBlock.dimensions = (foam_size_X, foam_size_Y, foam_size_Z)
        bpy.ops.object.transform_apply(scale=True)

        # change cursor location
        bpy.context.scene.cursor.location =(0,0,-foam_size_Z/2)
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # move the cube foamBlock
        foamBlock.location = (location_X, location_Y, location_Z)
        
        # set 3dcursor location back to the stored location
        bpy.context.scene.cursor.location = saved_location

    def create_block_greed (self, dimensions_X, dimensions_Y, dimensions_Z, foam_size_X, foam_size_Y, foam_size_Z, separation , scale = 1):
        #print(f"-------create_block_greed>{dir}")
        # IN METERS
        n_blocks_x = math.ceil(dimensions_X/foam_size_X)
        n_blocks_y = math.ceil(dimensions_Y/foam_size_Y)
        n_blocks_z = math.ceil((dimensions_Z+separation)/foam_size_Z)
                                          
        # create primitive cube as foamBlock
        # change cursor location
        bpy.context.scene.cursor.location =(0,0,0)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        foamBlock = bpy.context.object        
        foamBlock.name = "foamBlock.001"
        foamBlock.dimensions = (foam_size_X, foam_size_Y, foam_size_Z)
        bpy.ops.object.transform_apply(scale=True)

        # Get the object to apply the mod
        obj = bpy.context.object
        # Move the object
        obj.location = (separation/2,separation/2,foam_size_Z/2)

        # change cursor location
        bpy.context.scene.cursor.location =(0,0,0)
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Move the object
        obj.location = (foam_size_X/2,foam_size_Y/2,0)
        
        # Agregar el modificador Array
        array_modifier1 = obj.modifiers.new(name="Array_Y", type='ARRAY')
        array_modifier2 = obj.modifiers.new(name="Array_X", type='ARRAY')

        # Definir las propiedades del modificador
        array_modifier1.count = n_blocks_y  # Número de repeticiones
        array_modifier1.relative_offset_displace = (0.0, 1.0, 0.0)  # Desplazamiento relativo
        array_modifier1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier1.constant_offset_displace = (0.0, separation*scale, 0.0)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier2.count = n_blocks_x  # Número de repeticiones
        array_modifier2.relative_offset_displace = (1.0, 0.0, 0.0)  # Desplazamiento relativo
        array_modifier2.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier2.constant_offset_displace = (separation*scale, 0.0, 0.0)  # Desplazamiento constante

        if n_blocks_z > 1 :
            array_modifier3 = obj.modifiers.new(name="Array_Z", type='ARRAY')
            array_modifier3.count = n_blocks_z  # Número de repeticiones
            array_modifier3.relative_offset_displace = (0.0, 0.0, 1.0)  # Desplazamiento relativo
            array_modifier3.use_constant_offset = True  # Usar desplazamiento constante
            #array_modifier3.constant_offset_displace = (0.0, 0.0, separation*scale)  # Desplazamiento constante
            array_modifier3.constant_offset_displace = (0.0, 0.0, 0.002*scale)  # Desplazamiento constante
            bpy.ops.object.modifier_apply(modifier=array_modifier3.name)

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier=array_modifier1.name)
        bpy.ops.object.modifier_apply(modifier=array_modifier2.name)

        
        # ------------------Separate by loose parts-------------------------
        bpy.ops.mesh.separate(type='LOOSE')

        # Get divided parts
        foamBlocks = bpy.context.selected_objects

        # Create a new collection "Blocks"
        blocks_collection = bpy.data.collections.new("Blocks")

        # Add block to the collection "Blocks" and config location
        for block in foamBlocks:
            # set the origin on the current object to the ceter of mass location
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
            # get object coordinates
            coor_block = block.location            
            # get new origin coordinates
            block_location_X = coor_block.x
            block_location_Y = coor_block.y
            block_location_Z = coor_block.z
            # change cursor location
            bpy.context.scene.cursor.location = (block_location_X,block_location_Y,block_location_Z-foam_size_Z/2)
            # set the origin on the current object to the 3dcursor location
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            #change collection
            original_collection = block.users_collection[0]
            original_collection.objects.unlink(block)
            blocks_collection.objects.link(block)
        # Agregar la colección "Blocks" a la escena
        bpy.context.scene.collection.children.link(blocks_collection)      

    def create_cutter_planes (self, dimensions_X,dimensions_Y, dimensions_Z, separation_z, separation_x, separation_y,  plane_thickness, scale = 1):               

        plane_size_high = (dimensions_Z+0.5)
        #division_hight_z = plane_thickness
        division_hight_z = 0.002

        faces_count_x = math.ceil(dimensions_X/separation_x)+1 
        faces_count_y = math.ceil(dimensions_Y/separation_y)+1 
        faces_count_z = math.ceil((dimensions_Z)/separation_z)-1

        dim_plane_x=math.ceil(dimensions_X/separation_x)*separation_x+0.5
        dim_plane_y=math.ceil(dimensions_Y/separation_y)*separation_y+0.5
            
        location_x = (dim_plane_x-0.5)/2
        location_y = (dim_plane_y-0.5)/2
        location_z = (plane_size_high-0.5)/2
        
        # -----create primitive Plane as cutterPlane --Cuts in X--
        # change cursor location
        bpy.context.scene.cursor.location =(0,location_y,location_z)
        bpy.ops.mesh.primitive_plane_add(size=scale)
        cutterPlane_X = bpy.context.object
        cutterPlane_X.name = "cutterPlane.001"
        cutterPlane_X.dimensions = (plane_size_high, dim_plane_y, 0)
        cutterPlane_X.rotation_euler = (0,math.radians(90),0)
        bpy.ops.object.transform_apply(scale=True)
        cutterPlane_X.hide_select =  True
        

        # Agregar el modificador Array
        array_modifier_X1 = cutterPlane_X.modifiers.new(name="Array_X", type='ARRAY')
        # Agregar el modificador Array
        array_modifier_X2 = cutterPlane_X.modifiers.new(name="Solidify_X", type='SOLIDIFY')

        # Definir las propiedades del modificador
        array_modifier_X1.count = faces_count_x  # Número de repeticiones
        array_modifier_X1.relative_offset_displace = (1.0, 0.0, 0.0)  # Desplazamiento relativo
        array_modifier_X1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_X1.constant_offset_displace = (separation_x*scale, 0.0, 0.0)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier_X2.offset = 0
        array_modifier_X2.thickness = plane_thickness

        # -----create primitive Plane as cutterPlane --Cuts in Y--
        # change cursor location
        bpy.context.scene.cursor.location =(location_x,0,location_z)
        bpy.ops.mesh.primitive_plane_add(size=scale)
        cutterPlane_Y = bpy.context.object
        cutterPlane_Y.name = "cutterPlane.002"
        cutterPlane_Y.dimensions = (dim_plane_x, plane_size_high, 0)
        cutterPlane_Y.rotation_euler = (math.radians(90),0,0)
        bpy.ops.object.transform_apply(scale=True)        
        cutterPlane_Y.hide_select =  True

        # Agregar el modificador Array
        array_modifier_Y1 = cutterPlane_Y.modifiers.new(name="Array_Y", type='ARRAY')
        # Agregar el modificador Array
        array_modifier_Y2 = cutterPlane_Y.modifiers.new(name="Solidify_Y", type='SOLIDIFY')

        # Definir las propiedades del modificador
        array_modifier_Y1.count = faces_count_y  # Número de repeticiones
        array_modifier_Y1.relative_offset_displace = (0.0, 1.0, 0.0)  # Desplazamiento relativo
        array_modifier_Y1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_Y1.constant_offset_displace = (0.0, separation_y*scale, 0.0)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier_Y2.offset = 0
        array_modifier_Y2.thickness = plane_thickness

        # -----create primitive Plane as cutterPlane --Cuts in Z--
        # change cursor location
        #bpy.context.scene.cursor.location =(location_x,location_y,separation_z+plane_thickness/2)
        bpy.context.scene.cursor.location =(location_x,location_y,separation_z + division_hight_z/2)
        bpy.ops.mesh.primitive_plane_add(size=scale)
        cutterPlane_Z = bpy.context.object
        cutterPlane_Z.name = "cutterPlane.003"
        cutterPlane_Z.dimensions = (dim_plane_x, dim_plane_y, 0)        
        bpy.ops.object.transform_apply(scale=True)

        # Agregar el modificador Array
        array_modifier_Z1 = cutterPlane_Z.modifiers.new(name="Array_Y", type='ARRAY')
        # Agregar el modificador Array
        array_modifier_Z2 = cutterPlane_Z.modifiers.new(name="Solidify_Y", type='SOLIDIFY')

        # Definir las propiedades del modificador
        array_modifier_Z1.count = faces_count_z  # Número de repeticiones
        array_modifier_Z1.relative_offset_displace = (0.0, 0.0, 1.0)  # Desplazamiento relativo
        array_modifier_Z1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_Z1.constant_offset_displace = (0.0, 0.0, separation_z + division_hight_z/2)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier_Z2.offset = 0
        #array_modifier_Z2.thickness = plane_thickness
        array_modifier_Z2.thickness = division_hight_z    

    def crate_cnc_area (self, object_scope, scale = 1):
        #print(f"-------create_cnc_area>{dir}")
        
        cnc_size_X = 2.150
        cnc_size_Y = 2.095
        cnc_size_Z = 1.250
        dist_X_center = 1.137 #distance X from bootom to center

        # store the location of current 3d cursor
        #saved_location = bpy.context.scene.cursor.location.xyz   # returns a vector
        
        # get object
        # selected_object = bpy.context.active_object
        # get object coordinates
        coordinates = object_scope.location
        
        # get new origin coordinates
        location_X = coordinates.x
        location_Y = coordinates.y
        location_Z = coordinates.z        
        
        
        
        cnc_center_X = ((cnc_size_X/2)-dist_X_center)
        cnc_center_Y = cnc_size_Y/2
        cnc_center_Z = 0
        
        # give 3dcursor new coordinates for the primitive cube
        bpy.context.scene.cursor.location =(0,0,cnc_size_Z/2)
        
        # create primitive cube as AreaCNC
        bpy.ops.mesh.primitive_cube_add(size=scale)
        AreaCNC = bpy.context.object
        AreaCNC.name = "areaCNC.000" 
        AreaCNC.dimensions = (cnc_size_X, cnc_size_Y, cnc_size_Z)
        bpy.ops.object.transform_apply(scale=True)
        
        # change cursor location
        bpy.context.scene.cursor.location =(cnc_center_X,0,0)
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # move the cube AreaCNC
        AreaCNC.location = (location_X, location_Y, location_Z)
              
        # set 3dcursor location back to the stored location
        #bpy.context.scene.cursor.location = saved_location

        return AreaCNC

    def create_woods (self, dimensions_X,dimensions_Y, dimensions_Z, separation_z, separation_x, separation_y,  plane_thickness, scale = 1):

        plane_size_high = (separation_z+0.5)

        wood_heigh = self.wood_total_heigh
        wood_width = self.wood_total_width
        wood_depth = self.wood_total_depth

        faces_count_x = math.ceil(dimensions_X/separation_x)
        faces_count_y = math.ceil(dimensions_Y/separation_y)

        dim_plane_x=math.ceil(dimensions_X/separation_x)*separation_x+1.5
        dim_plane_y=math.ceil(dimensions_Y/separation_y)*separation_y+2
            
        location_x = (dim_plane_x-1.5)/2
        location_y = (dim_plane_y-2)/2
        #location_z = (plane_size_high-0.5)/2
        location_z = wood_heigh/2+wood_width #floor position
        
        # -----create primitive Plane as cutterPlane --Cuts in X--
        # change cursor location
        bpy.context.scene.cursor.location =(separation_x/2,location_y,location_z)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterWood_X = bpy.context.object
        cutterWood_X.name = "innerWood_x.001"
        cutterWood_X.dimensions = (wood_width, dim_plane_y, wood_heigh)
        #cutterPlane_X.rotation_euler = (0,math.radians(90),0)
        bpy.ops.object.transform_apply(scale=True)

        # Add array modifier
        array_modifier_X1 = cutterWood_X.modifiers.new(name="Array_X", type='ARRAY')

        # Set modifier properties
        array_modifier_X1.count = faces_count_x  # count number
        array_modifier_X1.relative_offset_displace = (1.0, 0.0, 0.0)  # Relative Offset
        array_modifier_X1.use_constant_offset = True  # Use constant offset
        array_modifier_X1.constant_offset_displace = ((separation_x-wood_width)*scale, 0.0, 0.0)  # Constant offset displace

        # -----create primitive Plane as cutterPlane --Cuts in Y--
        # change cursor location
        bpy.context.scene.cursor.location =(location_x,separation_y/2,location_z-wood_heigh/2-wood_width/2)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterWood_Y = bpy.context.object
        cutterWood_Y.name = "innerWood_y.001"
        cutterWood_Y.dimensions = (dim_plane_x, wood_width, wood_heigh)
        cutterWood_Y.rotation_euler = (math.radians(90),0,0)
        bpy.ops.object.transform_apply(scale=True)

        # Add array modifier
        array_modifier_Y1 = cutterWood_Y.modifiers.new(name="Array_Y", type='ARRAY')

        # Set modifier properties
        array_modifier_Y1.count = faces_count_y  # count number
        array_modifier_Y1.relative_offset_displace = (0.0, 1.0, 0.0)  # Relative Offset
        array_modifier_Y1.use_constant_offset = True  # Use constant offset
        array_modifier_Y1.constant_offset_displace = (0.0, (separation_y-wood_heigh)*scale, 0.0)  # Constant offset displace
        
        # Apply modifiers
        bpy.ops.object.modifier_apply(modifier=array_modifier_Y1.name)
        bpy.ops.object.modifier_apply(modifier=array_modifier_X1.name)

    def crate_around_object (self, context, scale = 1):
        #print(f"-------crate_around_object>{dir}")
        # store the location of current 3d cursor
        saved_location = bpy.context.scene.cursor.location.xyz   # returns a vector
            

        x_value = context.scene.my_number_settings.my_number_property_foam_block_x
        y_value = context.scene.my_number_settings.my_number_property_foam_block_y
        z_value = context.scene.my_number_settings.my_number_property_foam_block_z

        foam_block_hight_x = x_value + self.cut_thickness
        foam_block_hight_y = y_value + self.cut_thickness
        foam_block_hight_z = z_value        

        print(f"from context foam_block_hight_x:{foam_block_hight_x} foam_block_hight_y:{foam_block_hight_y} foam_block_hight_z:{foam_block_hight_z}")
        print(f"from self foam_block_hight_x:{self.foam_block_x} foam_block_hight_y:{self.foam_block_y} foam_block_hight_z:{self.foam_block_z}")

        separation = self.cut_thickness
        # get object
        selected_object = bpy.context.active_object
        # get object dimensions
        dimensions = selected_object.dimensions
        
        # get new origin coordinates
        dimensions_X = round(dimensions.x,1)
        dimensions_Y = round(dimensions.y,1)
        dimensions_Z = round(dimensions.z,1)   

        self.create_cutter_planes(dimensions_X,dimensions_Y,dimensions_Z,foam_block_hight_z,foam_block_hight_x,foam_block_hight_y,separation, scale = 1) 
        self.create_woods(dimensions_X,dimensions_Y,dimensions_Z,foam_block_hight_z,foam_block_hight_x,foam_block_hight_y, separation, scale = 1)
       
        bpy.ops.object.select_all(action='DESELECT')              

        #-----Select the initial object
        selected_object.select_set(True)
        bpy.context.view_layer.objects.active = selected_object
        # change cursor location
        bpy.context.scene.cursor.location =(0,0,0)              
        # set 3dcursor location back to the stored location
        bpy.context.scene.cursor.location = saved_location
    
    def cut_object(self, context):

        foam_size_X = context.scene.my_number_settings.my_number_property_foam_block_x
        foam_size_Y = context.scene.my_number_settings.my_number_property_foam_block_y
        foam_size_Z = context.scene.my_number_settings.my_number_property_foam_block_z

        separation = self.cut_thickness

        selected_object = bpy.context.active_object
        # get object dimensions
        dimensions = selected_object.dimensions
        # get new origin coordinates
        dimensions_X = dimensions.x
        dimensions_Y = dimensions.y
        dimensions_Z = dimensions.z 

        

        # Add boolean modifiers to cut the object
        boolean_modifier_X = selected_object.modifiers.new(name="Cut_plane_X", type='BOOLEAN')
        boolean_modifier_X.solver = 'FAST'
        boolean_modifier_X.object = bpy.data.objects['cutterPlane.001']

        boolean_modifier_Y = selected_object.modifiers.new(name="Cut_plane_Y", type='BOOLEAN')
        boolean_modifier_Y.solver = 'FAST'
        boolean_modifier_Y.object = bpy.data.objects['cutterPlane.002']

        boolean_modifier_Z = selected_object.modifiers.new(name="Cut_plane_Z", type='BOOLEAN')
        boolean_modifier_Z.solver = 'FAST'
        boolean_modifier_Z.object = bpy.data.objects['cutterPlane.003']

        bpy.ops.object.modifier_apply(modifier=boolean_modifier_Z.name)
        bpy.ops.object.modifier_apply(modifier=boolean_modifier_X.name)
        bpy.ops.object.modifier_apply(modifier=boolean_modifier_Y.name)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get each parts
        objectBlocks = bpy.context.selected_objects

        # Create a new collection
        cut_blocks_collection = bpy.data.collections.new("cut_Blocks")
        
        i=0
        # Add parts to the collection "cut_Blocks"
        for block in objectBlocks:
            # set the origin on the current object to the ceter of mass location
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
            
            # get object coordinates
            coor_block = block.location            
            # get new origin coordinates
            block_location_X = coor_block.x
            block_location_Y = coor_block.y
            block_location_Z = coor_block.z
            # change cursor location
            bpy.context.scene.cursor.location = (block_location_X,block_location_Y,block_location_Z)
            # set the origin on the current object to the 3dcursor location
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            original_collection = block.users_collection[0]
            original_collection.objects.unlink(block)
            cut_blocks_collection.objects.link(block)
        # Agregar la colección "Blocks" a la escena
        bpy.context.scene.collection.children.link(cut_blocks_collection) 

        self.create_block_greed(dimensions_X,dimensions_Y,dimensions_Z,foam_size_X, foam_size_Y, foam_size_Z, separation, scale = 1)

    def cut_and_order_parts(self, context):
        print('******inner_part_verif***********')
        #save state in case of error
        bpy.ops.ed.undo_push(message="inner_part_verif Function")
        #try:
        collections_name = "P"
        cubes_name = "foamBlock"
        object_selected_name = "irregObjPart"
        bpy.context.active_object.name = f"{object_selected_name}.001"
        #fix location in z to pass the inner verification, if z location is 0 may have conflict to check if is inside the cube due the cube Z location is 0
        if bpy.context.active_object.location.z == 0: bpy.context.active_object.location.z=+0.0001

        self.cut_object(context)
        # Get a list of all cube objects and irregular objects in the scene
        objects_cube      = [object for object in bpy.data.objects if object.name.startswith(f"{cubes_name}.")]
        objects_irregular = [object for object in bpy.data.objects if object.name.startswith(f"{object_selected_name}.")]
        
        # Dictionary to store the relationship between cube objects and irregular objects
        relation_cube_irregular = {}

        
        vol_cubo_obj = abs(context.scene.my_number_settings.my_number_property_foam_block_x*context.scene.my_number_settings.my_number_property_foam_block_y*context.scene.my_number_settings.my_number_property_foam_block_z)
            
        for object_cube in objects_cube:
            # # Get the world coordinates bounding-box-points of object_cube
            bbox_cube = [['%.4f' % elem for elem in object_cube.matrix_world @ Vector(coor)] for coor in object_cube.bound_box]
            have_something_inside = 0
            # Check if each irregular object is contained within any cube object
            for object_irregular in objects_irregular:
                # Get the world coordinates of the bounding-box-points of object_irregular
                bbox_irregular = [ ['%.4f' % elem for elem in object_irregular.matrix_world @ Vector(coor)] for coor in object_irregular.bound_box]

                # # Check if the bounding box of the irregular object is contained within the bounding box of the cube object
                is_inside = all(
                    float(bbox_cube[0][i]) <= float(bbox_irregular[0][i]) <= float(bbox_cube[6][i]) and
                    float(bbox_cube[0][i]) <= float(bbox_irregular[6][i]) <= float(bbox_cube[6][i])
                    for i in range(3)
                )                    
                                
                if is_inside:
                    relation_cube_irregular[object_irregular.name] = object_cube.name
                    have_something_inside = 1
                    #print(f'===={object_irregular.name} - {object_cube.name}=====')
                    #for i in range (3):                        
                        #print(f'c0|{i}:{bbox_cube[0][i]} <= i{i}|{i}:{bbox_irregular[i][i]} <= c6|{i}:{bbox_cube[6][i]}//c0|{i}:{bbox_cube[0][i]} <= i7|{i}:{bbox_irregular[7][i]} <= c6|{i}:{bbox_cube[6][i]}')
                '''if object_irregular.name == 'irregObjPart.068': #and object_cube.name == 'foamBlock.113':
                    print(f'-----------------====[{have_something_inside}]--{object_irregular.name} -in- {object_cube.name}=====')
                    for i in range (3):                     
                        print(f'[{float(bbox_cube[0][i]) <= float(bbox_irregular[0][i]) <= float(bbox_cube[6][i])}] and [{float(bbox_cube[0][i]) <= float(bbox_irregular[6][i]) <= float(bbox_cube[6][i])}] - c0  |{i}:{bbox_cube[0][i]} <= i0|{i}:{bbox_irregular[0][i]} <= c6|{i}:{bbox_cube[6][i]}//c0|{i}:{bbox_cube[0][i]} <= i6|{i}:{bbox_irregular[6][i]} <= c6|{i}:{bbox_cube[6][i]}')
                    
                    break'''
            #Delete cube if don't have nothing inside            
            if have_something_inside == 0:
                bpy.data.objects.remove(object_cube, do_unlink=True)
        
        volumen_total_irregular_obj = 0
        volumen_total_cube_obj = 0
        quantity_cube_obj = 0
        for object_irregular, object_cube in (relation_cube_irregular.items()):
            #set objects                 
            object_irregular_obj = bpy.data.objects[object_irregular]
            object_cube_obj = bpy.data.objects[object_cube]  

            #lock modification but Z rotation
            object_irregular_obj.lock_rotation = (True, True, False)
            object_irregular_obj.lock_location = (True, True, True)
            object_irregular_obj.lock_scale = (True, True, True)
            object_cube_obj.lock_rotation = (True, True, False)
            object_cube_obj.lock_location = (True, True, True)
            object_cube_obj.lock_scale = (True, True, True)
            object_cube_obj.hide_select = True                

            # --Set the origin on the current irregular object to the cube center
            # change cursor location
            bpy.context.scene.cursor.location = object_cube_obj.location
            bpy.ops.object.select_all(action='DESELECT')
            object_irregular_obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            if not(object_cube_obj.users_collection[0].name.startswith(f"{collections_name}.")):
                
                areaCNC = self.crate_cnc_area(object_cube_obj)                    
                
                #lock modification but Z rotation       
                areaCNC.lock_rotation= (True, True, True)
                areaCNC.lock_location = (True, True, True)
                areaCNC.lock_scale = (True, True, True)
                areaCNC.hide_select = True
                #make areaCNC and block just wire visible
                areaCNC.display_type = 'WIRE'
                #object_cube_obj.display_type = 'WIRE'

                # Create a new collection for the related objects
                blocks_collection = bpy.data.collections.new(f"{collections_name}.000")

                original_collection = object_cube_obj.users_collection[0]
                original_collection.objects.unlink(object_cube_obj)
                blocks_collection.objects.link(object_cube_obj)                
                
                original_collection = object_irregular_obj.users_collection[0]
                original_collection.objects.unlink(object_irregular_obj)
                blocks_collection.objects.link(object_irregular_obj)

                vol_irregular = abs(self.get_total_area_vol(object_irregular_obj)[1])
                volumen_total_irregular_obj = volumen_total_irregular_obj + vol_irregular
                volumen_total_cube_obj = volumen_total_cube_obj + vol_cubo_obj
                quantity_cube_obj = quantity_cube_obj + 1
                print(f'---------Volumen del irregular {object_irregular_obj.name} = {vol_irregular} | {vol_cubo_obj}')

                original_collection = areaCNC.users_collection[0]
                original_collection.objects.unlink(areaCNC)
                blocks_collection.objects.link(areaCNC) 
                
                # Add the created collection to the scene
                bpy.context.scene.collection.children.link(blocks_collection) 

                #set irregular object as parent of the cube
                object_cube_obj.parent = object_irregular_obj
                #fix miss location after parenting
                object_cube_obj.matrix_parent_inverse = object_irregular_obj.matrix_world.inverted()
            else:
                #print(f"The irregular object {object_irregular} is inside the cube object {object_cube}")
                original_collection = object_irregular_obj.users_collection[0]
                original_collection.objects.unlink(object_irregular_obj)
                object_cube_obj.users_collection[0].objects.link(object_irregular_obj)
                #bpy.context.scene.collection.children.link(blocks_collection)
            if object_irregular_obj.location.z < context.scene.my_number_settings.my_number_property_foam_block_z :
                self.cut_wood(context, object_irregular_obj,'x')
                self.cut_wood(context, object_irregular_obj,'y')
            #----create STL file of irregular object
            collection_name = object_irregular_obj.users_collection[0].name
            self.export_to_stl_origin(context,collection_name,collection_name,"irregObjPart.")
        print(f'---------Volumen Total del irregular = {volumen_total_irregular_obj}')
        print(f'---------Volumen Total del cubes = {volumen_total_cube_obj}')
        #vol_used = volumen_total_irregular_obj / volumen_total_cube_obj * 100
        #print(f'---------Volumen Used = {round(vol_used,2)}%')

        context.scene.my_number_settings.my_number_property_volume_total_irregular = volumen_total_irregular_obj
        context.scene.my_number_settings.my_number_property_volume_total_cubes = volumen_total_cube_obj
        context.scene.my_number_settings.my_number_property_quantity_cubes = quantity_cube_obj
        #except Exception as e:
            #print("Error Custon Function, UNDO:", e)
            # UnDo in case of error
            #bpy.ops.ed.undo()
    
    def draw_init(self):
        selected_object = bpy.context.active_object
        self.select_before = selected_object
        print(f"------------------------CARGA OBJ = {self.select_before.name}------------------------")
        rX, rY, rZ = selected_object.rotation_euler
        print(selected_object.users_collection[0].name+'==> rotation Z %.4f' % float(math.degrees(rZ)))

        loc_x, loc_y, loc_z = selected_object.location

        #create gpencil and put in drawing mode
        bpy.ops.object.gpencil_add(location=(loc_x, loc_y-selected_object.dimensions.y*2, loc_z), type='EMPTY')   

        #change to the actual collection
        gpencil_selected = bpy.context.active_object
        gpencil_coll=gpencil_selected.users_collection[0]
        #print(gpencil_coll.name)        
        
        gpencil_coll.objects.unlink(gpencil_selected)
        selected_coll = selected_object.users_collection[0]
        selected_coll.objects.link(gpencil_selected)

        # Change the Mode in the actual View while selected the gpencil
        bpy.context.view_layer.objects.active = gpencil_selected
        bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
             
        #bpy.ops.gpencil.primitive_polyline(subdivision=6, edges=4, type='POLYLINE', wait_for_input=True)        

        #turn on the auto key
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        #change Viewport to front view and shading type
        for area in bpy.data.screens[3].areas: 
            if area.type == 'VIEW_3D':
                for space in area.spaces: 
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        bpy.ops.view3d.view_axis(type='FRONT')

    def gpencil_to_mesh(self, scale = 1):
            print(f"------------------------self.select_before.name = {self.select_before.name}------------------------")
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

            context = bpy.context.copy()
            
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            context['area'] = area
                            context['region'] = region
                            break
                    break

            bpy.ops.gpencil.convert(context, type='CURVE', use_timing_data=True)
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.mode_set(mode='OBJECT')
            greacePencil = bpy.context.object
            
            selected_coll = greacePencil.users_collection[0]             

            #delete original gpencil curve
            bpy.data.objects.remove(greacePencil, do_unlink=True)             
            foamcut_gpencil_curve = bpy.context.selected_objects[0]           

            #change to the actual collection
            bpy.context.view_layer.objects.active = foamcut_gpencil_curve
            gpencil_selected = bpy.context.active_object
            gpencil_coll=gpencil_selected.users_collection[0]
            
            gpencil_coll.objects.unlink(gpencil_selected)
            selected_coll.objects.link(gpencil_selected)  

            
              

            #-----Select the gpencil curve object
            foamcut_gpencil_curve.select_set(True)
            bpy.context.view_layer.objects.active = foamcut_gpencil_curve
            
            
            verts = foamcut_gpencil_curve.data.vertices

            #get irregular object
            foamBlock = [obj for obj in bpy.data.objects if obj.name.startswith("foamBlock.") and selected_coll.name in obj.users_collection[0].name]

            # change cursor location
            bpy.context.scene.cursor.location =(foamBlock[0].location.x,foamBlock[0].location.y,foamBlock[0].location.z)
            # set the origin on the current object to the 3dcursor location
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            print(f'*-*{gpencil_coll.name} => {selected_coll.name} bloque {foamBlock[0].name} rotacion{math.degrees(foamBlock[0].rotation_euler.z)}')

            #----------------------Reorder vertex----------------------------

            # Switch to Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')

            # Select all vertices to extrude
            bpy.ops.mesh.select_all(action='SELECT')

            # Get the mesh data and create a BMesh
            me = bpy.context.object.data
            bm = bmesh.from_edit_mesh(me)

            # Dissolve vertices within a certain angle limit
            #bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5), verts=bm.verts)

            bm.verts.ensure_lookup_table()

            # Set Index of the start vertex
            if bm.verts[0].index > bm.verts[len(bm.verts)-1].index:
                initial = bm.verts[0]
            else:
                initial = bm.verts[len(bm.verts)-1]                

            vert = initial
            prev = None
            for i in range(len(bm.verts)):
                vert.index = i
                next = None
                adjacent = []
                for v in [e.other_vert(vert) for e in vert.link_edges]:
                    if (v != prev and v != initial):
                        next = v
                if next == None:
                    break
                prev, vert = vert, next

            # Sort vertices
            bm.verts.sort()

            # Update the mesh
            bmesh.update_edit_mesh(me)
            #----------------------Reorder vertex END----------------------------

            # Extract the vertex coordinates from the verts list
            
            vertex_coordinates = [{'x':v.co.x, 'y':v.co.y, 'z':v.co.z} for v in bm.verts if  -1.013 < v.co.x < 1.137 ]
            if vertex_coordinates[0]['x']>0:
                vertex_coordinates.insert(0,{'x':1.137, 'y':0, 'z':0})
            else:
                vertex_coordinates.append({'x':1.137, 'y':0, 'z':0})

            vertex_coo_edit = {}

            print(f"--  {vertex_coordinates[0]['x']} < {vertex_coordinates[len(vertex_coordinates)-1]['x']}")
            if vertex_coordinates[0]['x'] > vertex_coordinates[len(vertex_coordinates)-1]['x']:
                custom_range = range(0,len(vertex_coordinates))
                print("direction =>")
            else:
                custom_range = reversed(range(0,len(vertex_coordinates)))
                print("direction <=")

            j=0
            for i in custom_range:
                                    
                vertex_coo_edit[j] = {'x':(vertex_coordinates[i]['x']), 'y':vertex_coordinates[i]['y'], 'z':vertex_coordinates[i]['z']}
                #print(f"vertex_coo_edit[j{j} => i{i}] = {vertex_coo_edit[j]}")
                j+=1
                        
            # ------Export to a *.nc file
            self.write_to_file(vertex_coo_edit,math.degrees(foamBlock[0].rotation_euler.z),selected_coll.name)

            # Switch to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')     

            gpencil_curve = bpy.context.active_object
        
            #foamcut_gpencil_curve.hide_select =  True
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

             # --- Cut the foam START ---

            selected_object_active = self.select_before
            #selected_objects = bpy.context.selected_objects

            # Create a new collection for the related objects
            blocks_collection = bpy.data.collections.new(f"small_parts_{selected_object_active.name}.000")
            bpy.context.scene.collection.children.link(blocks_collection)

            original_collection = selected_object_active.users_collection[0]
            original_collection.objects.unlink(selected_object_active)
            blocks_collection.objects.link(selected_object_active)

            print (f"---original_collection = {original_collection.name} | blocks_collection.name = {blocks_collection.name}")

            '''# create primitive cube as foamBlock
            # change cursor location
            bpy.context.scene.cursor.location =(selected_object_active.location.x,selected_object_active.location.y,self.foam_block_z/2)
            bpy.ops.mesh.primitive_cube_add(size=scale)
            foamBlock = bpy.context.object        
            foamBlock.name = "foamBlock.001"
            foamBlock.dimensions = (self.foam_block_x, self.foam_block_y, self.foam_block_z)'''
            
            # --- Cut the foam END ---

            #self.cut_silhouette(self.location_z,self.udpdate_value_bool)

            #delete gpencil curve
            bpy.data.objects.remove(gpencil_curve, do_unlink=True)

            #change Viewport to front view and shading type
            for area in bpy.data.screens[3].areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'WIREFRAME'
                            bpy.ops.view3d.view_axis(type='FRONT')

    def write_to_file(self,verts,rotation_z_degrees,collection_name,update=False, wood=False):
        scale=1000
        i=0
        if wood == 'X':
            pathFileName=".\\PARTES\\"+collection_name+"\\"+collection_name+"_WX."
        elif wood == 'Y':
            pathFileName=".\\PARTES\\"+collection_name+"\\"+collection_name+"_WY."
        else:
            pathFileName=".\\PARTES\\"+collection_name+"\\"+collection_name+"."
            
        pathFileNumber=pathFileName+'%03d' % i +"_samurai.nc"
        #create .nc file 
        try:
            os.makedirs(".\\PARTES\\"+collection_name, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        while os.path.exists(pathFileNumber):
            i=i+1
            pathFileNumber=pathFileName+'%03d' % i +"_samurai.nc"
        if update == True:
            #if not wood:
            i=i-1
            pathFileNumber=pathFileName+'%03d' % i +"_samurai.nc"
        f = open(pathFileNumber,"w+")
        f.write(f'(GCODE_from_Blender)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')
        
        #direction will be from +X  to -X
        x_first = verts[0]['x']

        custom_range = range(0,len(verts))         

        for i in custom_range:
            x=round((x_first - verts[i]['x']) * scale,2)
            y=round(verts[i]['y'] * scale,2)

            if verts[i]['z'] > 0 and wood == False:
                z=round((verts[i]['z'] - verts[0]['z']) * scale,2)
                #print(f"more than 0 ({verts[i]['z']} - {verts[0]['z']} = {z})")
            else:
                z=round(verts[i]['z'] * scale,2)
                #print(f"less than 0 ({verts[i]['z']}) = {z}")

            coorX=str('%.4f' % x)
            coorY=str('%.4f' % y)
            coorZ=str('%.4f' % z)

            #write in .nc file
            #if 0 < x <= 2150:
            f.write(f'G01X{coorX}Y{coorZ}A{rotation_z_degrees}\n') 
            #---------------write creasees if is a wood cut-------------------------
            if i+1 < len(verts) and i > 0 and wood != False:
                crease_width = 2
                creases_up = ''
                creases_down = ''
                actual_vert_z = round(verts[i]['z'], 2)
                next_vert_z   = round(verts[i+1]['z'], 2)
                #print(f'Vertex Z{i} : {actual_vert_z} == {next_vert_z} ?')
                if  actual_vert_z == next_vert_z:
                    width_wood=(round(verts[2]['x'],4) - round(verts[3]['x'],4))*scale
                    crease_step=width_wood/4 #for 3 creases
                    #print(f'vertex distance {i}:{verts[i].co.x} - {verts[i+1].co.x} = {width_wood}')
                    for j in range(1,4):
                        #direction logic
                        if round(verts[i]['x'],2) > round(verts[i+1]['x'],2):
                            creases_top = coorZ
                            #verif if is on floor
                            if(float(coorZ)<=0):
                                creases_bottom = 0
                            else:
                                creases_bottom = "%.4f" % (z+crease_width)
                            creases_up =  (f'G01X{str("%.4f" % (x-(-j*crease_step+crease_width/2)))}Y{creases_top}A{rotation_z_degrees}\n')
                            creases_up += (f'G01X{str("%.4f" % (x-(-j*crease_step+crease_width/2)))}Y{creases_bottom}A{rotation_z_degrees}\n')
                            creases_up += (f'G01X{str("%.4f" % (x-(-j*crease_step-crease_width/2)))}Y{creases_bottom}A{rotation_z_degrees}\n')
                            creases_up += (f'G01X{str("%.4f" % (x-(-j*crease_step-crease_width/2)))}Y{creases_top}A{rotation_z_degrees}\n')
                            f.write(creases_up)
                        elif round(verts[i]['x'],2) < round(verts[i+1]['x'],2):
                            creases_top = coorZ
                            if(float(coorZ)<=0):
                                creases_bottom = 0
                            else:
                                creases_bottom = "%.4f" % (z-crease_width)
                            creases_down =  (f'G01X{str("%.4f" % (x+(-j*crease_step+crease_width/2)))}Y{coorZ}A{rotation_z_degrees}\n')
                            creases_down += (f'G01X{str("%.4f" % (x+(-j*crease_step+crease_width/2)))}Y{creases_bottom}A{rotation_z_degrees}\n')
                            creases_down += (f'G01X{str("%.4f" % (x+(-j*crease_step-crease_width/2)))}Y{creases_bottom}A{rotation_z_degrees}\n')
                            creases_down += (f'G01X{str("%.4f" % (x+(-j*crease_step-crease_width/2)))}Y{coorZ}A{rotation_z_degrees}\n')
                            f.write(creases_down)

        if x != 0:    
            f.write(f'G01X2150Y1200A{rotation_z_degrees}\n') 
            f.write(f'G01X0Y1200A{rotation_z_degrees}\n')
        f.write(f'(Zigzag)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')

    def reorder_vertices(self, iniver):
        #must be in EDIT mode
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()

        # index of the start vertex SELECT the specific vertex
        initial = bm.verts[iniver]
        #print(f'inivert-->{iniver}')
        vert = initial
        visited_verts = set()
        for i in range(len(bm.verts)):
            #print(f'reorder--{vert.index, i}')
            vert.index = i
            next = None
            for edge in vert.link_edges:
                next = edge.other_vert(vert)
                if next not in visited_verts:
                    visited_verts.add(vert)
                    break
            if next == None: break
            vert = next

        bm.verts.sort(key=lambda v: v.index)

        bmesh.update_edit_mesh(me)
    
    def cut_foam(self):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 3, 0)})
        bpy.ops.object.mode_set(mode='OBJECT')        

        #identify and choose collection union
        silhouette_selected = bpy.context.active_object
        silhouette_coll = silhouette_selected.users_collection[0]
        col = bpy.data.collections[silhouette_coll.name]

        # create a list requiring both objects selected and in chosen collection
        objects_cube = [object for object in col.objects if object.name.startswith(f"foamBlock.")]        
        objects_irreg = [object for object in col.objects if object.name.startswith(f"irregObjPart.")]

        print('---'+objects_cube[0].name+'--------------------------------------------')

        #--create bool to cut the foamBlock with silhouette mesh
        #hide silhouette
        silhouette_selected.hide_select =  True
        silhouette_selected.select_set(False) # deselect to evade errors
        bpy.context.view_layer.objects.active = objects_cube[0]
        boolean_modifier_Z = objects_cube[0].modifiers.new(name="Cut_foam_001", type='BOOLEAN')
        boolean_modifier_Z.solver = 'FAST'
        boolean_modifier_Z.operation = 'INTERSECT'
        boolean_modifier_Z.object = silhouette_selected
        bpy.ops.object.modifier_apply(modifier=boolean_modifier_Z.name)
                
        bpy.data.objects.remove(silhouette_selected, do_unlink=True)
    
    def create_silhouette(self):
        # Set CNC margin
        CNC_margin = 2
        # Set scale factor, how big will scale the siluete
        scale_factor = 1.05
        # Set subdivision level for the siluete
        siluete_multires = 8

        margen_max_cnc=1.137
        margen_min_cnc=1.013

        # Get the selected object
        selected_object = bpy.context.active_object
        # Get the object collection 
        object_collection = selected_object.users_collection[0]

        # Move the 3D cursor below the selected object by the CNC_margin amount
        loc_x, loc_y, loc_z = selected_object.location
        bpy.context.scene.cursor.location = (loc_x, loc_y - CNC_margin, loc_z)

        # Create a plane to serve as the cutter plane
        bpy.ops.mesh.primitive_plane_add(size=4)
        silhouette_base = bpy.context.object
        silhouette_base.name = "cutterPlane.001"
        silhouette_base.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(scale=True,location=False)
        silhouette_base.hide_select = True

        # Add a Multiresolution modifier with 8 levels
        Multires_01 = silhouette_base.modifiers.new(name="Multires_01", type='MULTIRES')
        for i in range(siluete_multires):
            bpy.ops.object.multires_subdivide(modifier=Multires_01.name, mode='SIMPLE')        
        # Add a Shrinkwrap modifier to project the cutter plane onto the selected object
        Srinkwrap_01 = silhouette_base.modifiers.new(name="Srinkwrap_01", type='SHRINKWRAP')
        Srinkwrap_01.target = selected_object
        Srinkwrap_01.wrap_method = 'PROJECT'
        Srinkwrap_01.wrap_mode = 'ON_SURFACE'
        Srinkwrap_01.use_project_y = True
        Srinkwrap_01.offset = -2
        
        #apply modifiers
        bpy.ops.object.modifier_apply(modifier=Multires_01.name)        
        bpy.ops.object.modifier_apply(modifier=Srinkwrap_01.name)

        #--scale by normals (shink/fatten)
        bpy.ops.object.mode_set(mode='EDIT')        
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.transform.shrink_fatten(value=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Reset 3D cursor position
        bpy.context.scene.cursor.location = (loc_x, loc_y, loc_z)

        # Create a second plane to serve as the silhouette cutter
        distance_to_plane=0.025
        bpy.ops.mesh.primitive_plane_add(size=4)
        silhouette = bpy.context.object
        silhouette.name = "siluete.001"
        silhouette.rotation_euler = (math.radians(90), 0, 0)
        silhouette.location.y=silhouette_base.location.y+distance_to_plane
        bpy.ops.object.transform_apply(scale=True,location=False)
        
        #change silhouette collection to actual collection.    
        siluete_collection = silhouette.users_collection[0]
        siluete_collection.objects.unlink(silhouette)
        object_collection.objects.link(silhouette)
        bpy.context.view_layer.objects.active = silhouette        

        # Add a Boolean modifier to intersect the silhouette cutter with the projected plane
        Boolean_01 = silhouette.modifiers.new(name="Boolean_01", type='BOOLEAN')
        Boolean_01.operation = 'INTERSECT'
        Boolean_01.solver = 'FAST'
        Boolean_01.object = silhouette_base

        # Apply the Boolean modifier to create the silhouette
        bpy.ops.object.modifier_apply(modifier=Boolean_01.name)

        # Set the origin of the silhouette cutter to the center of mass
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        # ---------------------cut the base of the silhouette (<0 in Z)----------------------------------
        # Create a plane to serve as the cutter plane
        bpy.ops.mesh.primitive_plane_add(size=5)
        plane_base = bpy.context.object
        plane_base.name = "cutterPlaneforSilhouette.001"
        bpy.ops.object.transform_apply(scale=True,location=False)

        bpy.ops.object.select_all(action='DESELECT')    
        silhouette.select_set(True)
        bpy.context.view_layer.objects.active = silhouette

        # Add a Boolean modifier to intersect the silhouette cutter with the projected plane
        Boolean_02 = silhouette.modifiers.new(name="Boolean_02", type='BOOLEAN')
        Boolean_02.solver = 'EXACT'
        Boolean_02.object = plane_base

        # Apply the Boolean modifier to create the silhouette
        bpy.ops.object.modifier_apply(modifier=Boolean_02.name)
        bpy.data.objects.remove(plane_base, do_unlink=True)
        
        #move silhouette to the center of the irregular object
        silhouette.location.y=loc_y
        
        # Enter Edit Mode to reorder vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Get the mesh data and create a BMesh
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)

        # Dissolve vertices within a certain angle limit
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5), verts=bm.verts)

        #----------------------Reorder vertex----------------------------
        bm.verts.ensure_lookup_table()

        # Index of the start vertex
        initial = bm.verts[0]

        vert = initial
        prev = None
        for i in range(len(bm.verts)):
            vert.index = i
            next = None
            adjacent = []
            for v in [e.other_vert(vert) for e in vert.link_edges]:
                if (v != prev and v != initial):
                    next = v
            if next == None:
                break
            prev, vert = vert, next

        # Sort vertices
        bm.verts.sort()

        # Update the mesh
        bmesh.update_edit_mesh(me)

        # Exit Edit Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.data.objects.remove(silhouette_base, do_unlink=True)        
        # select object to scale
        silhouette_curve = bpy.context.active_object
        
        # Aplicar la escala al objeto
        bpy.ops.object.transform_apply(scale=True)

        #---------------------------edit sluete------------------
        # Select the plane object
        obj = bpy.context.active_object

        # Make sure you're in Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        # Change back to Vertex selection mode
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')

        # Create a new bmesh from the mesh data
        bm = bmesh.from_edit_mesh(obj.data)

        # Deselect all vertices
        for v in bm.verts:
            v.select = False

        # Find the lowest Z coordinate among all vertices
        lowest_z = min(v.co.z for v in bm.verts)


        indices_in_z = []

        # Select the vertices that have the lowest Z coordinate
        lowest_z_vertices = [v for v in bm.verts if v.co.z == lowest_z]
        for v in lowest_z_vertices:
            v.select = True
            indices_in_z.append(v.index)

        # Find the vertex with the minimum X coordinate among the selected vertices
        min_x_vertex = min(lowest_z_vertices, key=lambda v: v.co.x)

        # Find the vertex with the maximum X coordinate among the selected vertices
        max_x_vertex = max(lowest_z_vertices, key=lambda v: v.co.x)

        for e in bm.edges:
            if e.verts[0].index in indices_in_z and e.verts[1].index in indices_in_z:
                e.select = True
                break

        # Change to Edge selection mode
        bpy.ops.mesh.select_mode(type="EDGE")

        # Elimina los bordes seleccionados
        bpy.ops.mesh.delete(type='EDGE')

        # Change back to Vertex selection mode
        bpy.ops.mesh.select_mode(type="VERT")

        ##-------Extrude to the limits of the CNC---------
        # Extrude the maximum X vertex +2 in the X direction
        newvert = bm.verts.new((loc_x+margen_max_cnc, max_x_vertex.co.y, loc_z))
        newedge = bm.edges.new([max_x_vertex, newvert])
        indices_max=len(bm.verts)-1

        if max_x_vertex.index == min_x_vertex.index:
            # Update the mesh
            bm.verts.ensure_lookup_table()
            print(f"------------------max {max_x_vertex.index}  min {min_x_vertex.index} len {len(bm.verts)}")
            
            # Index of the start vertex
            initial = bm.verts[len(bm.verts)-1]

            vert = initial
            prev = None
            for i in range(len(bm.verts)):
                vert.index = i
                next = None
                adjacent = []
                for v in [e.other_vert(vert) for e in vert.link_edges]:
                    if (v != prev and v != initial):
                        next = v
                if next == None:
                    break
                prev, vert = vert, next

            # Sort vertices
            bm.verts.sort()
            bm.verts.ensure_lookup_table()
            min_x_vertex=bm.verts[1]
            before_last=bm.verts[len(bm.verts)-1]
            newvert = bm.verts.new((min_x_vertex.co.x, min_x_vertex.co.y, min_x_vertex.co.z))
            newedge = bm.edges.new([before_last, newvert])
            
            bm.verts.ensure_lookup_table()
            before_last=bm.verts[len(bm.verts)-1]
            newvert = bm.verts.new((loc_x+margen_max_cnc, min_x_vertex.co.y, loc_z))
            newedge = bm.edges.new([before_last, newvert])

        else:
            # Extrude the minimum X vertex -2 in the X direction
            newvert = bm.verts.new((loc_x-margen_min_cnc, min_x_vertex.co.y, loc_z))
            newedge = bm.edges.new([min_x_vertex, newvert])
            indices_min=indices_in_z[1]+1
           
            self.reorder_vertices(indices_max)

        # Update the bmesh and exit Edit Mode
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.scene.cursor.location = (0, 0, 0)

    def cut_silhouette(self, loc_z, update=False):
        
        selected_object = bpy.context.selected_objects[0]
        #get colection name
        collection_name = selected_object.users_collection[0].name
        #get irregular object
        irregular_obj = [obj for obj in bpy.data.objects if obj.name.startswith("irregObjPart.") and collection_name in obj.users_collection[0].name]
        
        if irregular_obj:
            target_object = irregular_obj[0]
            rotation_euler = target_object.rotation_euler
            rotation_z_degrees = math.degrees(rotation_euler.z)
            print(f"Rotation in Z of {target_object.name}: {rotation_z_degrees} degrees")
        else:
            print("No related objects found in the same collection.")
                
        verts = selected_object.data.vertices


        if not('customVar' in irregular_obj[0]):
            custom_list = []
            irregular_obj[0]['customVar'] = custom_list
            #print('---LISTA NO EXISTE antes----')
            #print(irregular_obj[0]['customVar'])
        else:
            custom_list = irregular_obj[0]['customVar']
            #print('---LISTA EXISTEantes----')
            #print(irregular_obj[0]['customVar'])            
            
        # Extract the vertex coordinates from the verts list
        vertex_coordinates = [{'x':v.co.x, 'y':v.co.y, 'z':v.co.z} for v in verts]

        gcode_dict = dict()
        gcode_dict = { 'collection_name': collection_name, 
                       'selected_silhouette.name':selected_object.name,
                       'vertex_list' : vertex_coordinates, 
                       'rotation_z'  : rotation_z_degrees,                 
                     }
        
        '''print('---LISTA antes----')
        print(irregular_obj[0]['customVar'][0]['collection_name'])
        print('---INDEX----')'''
        #print(len(irregular_obj[0]['customVar']))
        
        if update == False:
            #custom_list.append('gcode_dict-NUEVO')
            custom_list.append(gcode_dict)
        elif update == True:
            #custom_list.append('gcode_dict-UPDATE')
            custom_list.append(gcode_dict)
        
        irregular_obj[0]['customVar'] = custom_list

        #-------export to a *.nc file-------
        #self.write_to_file(vertex_coordinates,rotation_z_degrees,collection_name,update)
        silhouette = bpy.context.object
        silhouette.location.z = loc_z
        silhouette.location.y = -1.5
        self.cut_foam()
        
        irregular_obj[0].select_set(True)
        #bpy.context.active_object.name = irregular_obj[0].name
        bpy.context.view_layer.objects.active = irregular_obj[0]

    def cut_wood(self, context,  selected_obj=False, wood_axis='x'):
        #identify and choose collection union
        #print('CUT_WOOD--START')
        if selected_obj:
            #print(f'-------seleccionado activo--------{selected_obj.name}')            
            irreg_obj_selected = selected_obj
        else:
            irreg_obj_selected = bpy.context.active_object              
        silhouette_coll = irreg_obj_selected.users_collection[0]
        object_collection = bpy.data.collections[silhouette_coll.name]

        # create a list requiring both objects selected and in chosen collection
        objects_cube = [object for object in object_collection.objects if object.name.startswith(f"foamBlock.")]

        margen_max_cnc=1.137
        margen_min_cnc=1.013

        loc_x, loc_y, loc_z = objects_cube[0].location
        
        # Set the origin of the silhouette cutter to the center of mass        
        bpy.context.scene.cursor.location = (loc_x, loc_y, loc_z) 
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Create a second plane to serve as the silhouette cutter
        distance_to_plane=0.025
        bpy.ops.mesh.primitive_plane_add(size=1)
        silhouette_wood = bpy.context.object
        silhouette_wood.name = "siluete_wood_"+wood_axis+".001"
        if wood_axis == 'y':
            silhouette_wood.scale = (context.scene.my_number_settings.my_number_property_foam_block_x, context.scene.my_number_settings.my_number_property_foam_block_y,0 )
            silhouette_wood.rotation_euler = (0, math.radians(90), 0)
            distance_to_plane=0
        else:
            silhouette_wood.scale = (context.scene.my_number_settings.my_number_property_foam_block_x, context.scene.my_number_settings.my_number_property_foam_block_y,0 )
            silhouette_wood.rotation_euler = (math.radians(90), 0, 0)
        silhouette_wood.location.y=objects_cube[0].location.y+distance_to_plane
        bpy.ops.object.transform_apply(scale=True,location=False)

        #change silhouette collection to actual collection.    
        siluete_collection = silhouette_wood.users_collection[0]
        siluete_collection.objects.unlink(silhouette_wood)
        object_collection.objects.link(silhouette_wood)
        bpy.context.view_layer.objects.active = silhouette_wood        

        # Add a Boolean modifier to intersect the silhouette cutter with the projected plane
        Boolean_01 = silhouette_wood.modifiers.new(name="Boolean_01", type='BOOLEAN')
        Boolean_01.operation = 'INTERSECT'
        Boolean_01.solver = 'EXACT'
        Boolean_01.object = bpy.data.objects['innerWood_'+wood_axis+'.001']
        
        # Apply the Boolean modifier to create the silhouette
        bpy.ops.object.modifier_apply(modifier=Boolean_01.name)
        if wood_axis == 'y':
            silhouette_wood.rotation_euler = (0, 0, math.radians(90))
            bpy.ops.object.transform_apply(rotation=True,location=False)            
        #---------------------------edit sluete------------------
        # Select the plane object
        obj = bpy.context.active_object

        # Make sure you're in Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        # Change back to Vertex selection mode
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')

        # Create a new bmesh from the mesh data
        bm = bmesh.from_edit_mesh(obj.data)

        # Deselect all vertices
        for v in bm.verts:
            v.select = False

        # Find the lowest Z coordinate among all vertices
        lowest_z = min(v.co.z for v in bm.verts)


        indices_in_z = []

        # Select the vertices that have the lowest Z coordinate
        lowest_z_vertices = [v for v in bm.verts if v.co.z == lowest_z]
        for v in lowest_z_vertices:
            v.select = True
            indices_in_z.append(v.index)

        # Find the vertex with the minimum X coordinate among the selected vertices
        min_x_vertex = min(lowest_z_vertices, key=lambda v: v.co.x)

        # Find the vertex with the maximum X coordinate among the selected vertices
        max_x_vertex = max(lowest_z_vertices, key=lambda v: v.co.x)

        for e in bm.edges:
            if e.verts[0].index in indices_in_z and e.verts[1].index in indices_in_z:
                e.select = True
                break

        # Change to Edge selection mode
        bpy.ops.mesh.select_mode(type="EDGE")

        # Elimina los bordes seleccionados
        bpy.ops.mesh.delete(type='EDGE')

        # Change back to Vertex selection mode
        bpy.ops.mesh.select_mode(type="VERT")
        
        #get global coords
        max_x_vertex_world = obj.matrix_world @ max_x_vertex.co
        
        ##-------Extrude to the limits of the CNC---------
        # Extrude the minimum X vertex -2 in the X direction
        #newvert = bm.verts.new((-margen_min_cnc, min_x_vertex.co.y, max_x_vertex_world[2]))        
        newvert = bm.verts.new((margen_max_cnc, max_x_vertex.co.y, max_x_vertex_world[2]))
        newedge = bm.edges.new([min_x_vertex, newvert])
        indices_min=indices_in_z[1]+1
        # Extrude the maximum X vertex +2 in the X direction
        newvert = bm.verts.new((margen_max_cnc, max_x_vertex.co.y, max_x_vertex_world[2]))
        newedge = bm.edges.new([max_x_vertex, newvert])
        indices_max=len(bm.verts)-1
           
        self.reorder_vertices(indices_max)
        # Update the bmesh and exit Edit Mode
        verts=silhouette_wood.data.vertices
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.context.scene.cursor.location = (loc_x, loc_y, loc_z)
        
        # Extract the vertex coordinates from the verts list
        vertex_coordinates = [{'x':v.co.x, 'y':v.co.y, 'z':v.co.z} for v in verts]

        if wood_axis == 'x':
            self.write_to_file(vertex_coordinates,0,silhouette_wood.users_collection[0].name,True,'X')
        elif wood_axis == 'y':            
            self.write_to_file(vertex_coordinates,90,silhouette_wood.users_collection[0].name,True,'Y')
        #delete silhouette
        bpy.data.objects.remove(silhouette_wood, do_unlink=True)
        #print('CUT_WOOD--END')

    def export_gcode_raw(self, context):
        selected_object = bpy.context.selected_objects[0]
        #get colection name
        collection_name = selected_object.users_collection[0].name
        #get irregular object
        irregular_obj = [obj for obj in bpy.data.objects if obj.name.startswith("irregObjPart.") and collection_name in obj.users_collection[0].name]        

        #--Delete all cut-files that have been created before for this collection
        folder_path = ".\\PARTES\\"+collection_name
        
        pattern = r"^{0}\.\d{{3}}_samurai\.nc$".format(re.escape(collection_name))

        print(f'pattern===>{pattern}')
        for filename in os.listdir(folder_path):
            if re.match(pattern, filename):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)

        for gcode_dict in irregular_obj[0]['customVar']:
            collection_name = gcode_dict['collection_name']
            verts = gcode_dict['vertex_list']
            rotation_z_degrees = gcode_dict['rotation_z']

            print(f'collection===>{collection_name}')

            #----create GCODE file
            self.write_to_file(verts,rotation_z_degrees,collection_name)
        #reset rotation of irregular object
        irregular_obj[0].rotation_euler.z = math.radians(0)

        self.export_to_stl_origin(context,collection_name,collection_name+'_raw',"foamBlock.")

    def export_to_stl_origin(self,context,collection_name,stl_name,obj_name_base):

        scale_for_powermill=1000
        foam_x = context.scene.my_number_settings.my_number_property_foam_block_x
        foam_y = context.scene.my_number_settings.my_number_property_foam_block_y
        foam_z = context.scene.my_number_settings.my_number_property_foam_block_z

        try:
            os.makedirs(".\\PARTES\\"+collection_name, exist_ok=True)  
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        output_path=".\\PARTES\\"+collection_name+"\\"+stl_name+".stl"
        #get foamBlock object
        objective_object = [obj for obj in bpy.data.objects if obj.name.startswith(obj_name_base) and collection_name in obj.users_collection[0].name]
        
        # --Check dimentions--
        y_less=999999
        y_max=0
        for obj in bpy.data.objects:
            if obj.name.startswith('irregObjPart.'):
                if obj.location.y > y_max:
                    y_max=obj.location.y
                if obj.location.y < y_less:
                    y_less=obj.location.y
        distance = y_max-y_less
        middle_pos = y_less + distance/2

        #print(f"export_to_stl_origin: menor -> {y_less} mayor -> {y_max} distancia de centros -> {distance}")

        # --END Check dimentions--

        bpy.ops.object.select_all(action='DESELECT')

        objective_object[0].hide_select = False

        objective_object[0].select_set(True)
        bpy.context.view_layer.objects.active = objective_object[0]

        # save location
        location_ini_x = objective_object[0].location.x
        location_ini_y = objective_object[0].location.y
        location_ini_z = objective_object[0].location.z
        rotation_ini_x = objective_object[0].rotation_euler.x

        # - no rotate logic -
        '''objective_object[0].location.x = 0
        objective_object[0].location.y = 0
        objective_object[0].location.z = 0
        objective_object[0].rotation_euler.x = math.radians(0)'''


        # - Rotate elements related to the middle of he object (for little parts floating in Z)-
        objective_object[0].location.x = 0
        if(objective_object[0].location.y < middle_pos and objective_object[0].location.z < foam_z):
            objective_object[0].location.y = -0.49 #0
            objective_object[0].location.z = 0.49 #0
            objective_object[0].rotation_euler.x = math.radians(-90) #0
            print("giro Izq")
        elif(objective_object[0].location.y > middle_pos and objective_object[0].location.z < foam_z):
            objective_object[0].location.y = 0.49 #0
            objective_object[0].location.z = 0.49 #0
            objective_object[0].rotation_euler.x = math.radians(90) #0
            print("giro Der")

        # ------- Fix Faces -------
        # go edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        # select al faces
        bpy.ops.mesh.select_all(action='SELECT')
        # recalculate outside normals 
        bpy.ops.mesh.normals_make_consistent(inside=False)
        # go object mode again
        bpy.ops.object.editmode_toggle()


        # Export the object as STL
        bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True, check_existing=False,global_scale = scale_for_powermill)

        # load and restore location
        objective_object[0].location.x = location_ini_x
        objective_object[0].location.y = location_ini_y
        objective_object[0].location.z = location_ini_z
        objective_object[0].rotation_euler.x = rotation_ini_x
        if not (objective_object[0].name.startswith("irregObjPart.")):
            objective_object[0].hide_select = True
        bpy.ops.object.select_all(action='DESELECT')

    def create_block_apart(self, context,  scale = 1):

        selected_object_active = bpy.context.active_object
        selected_objects = bpy.context.selected_objects

        # create primitive cube as foamBlock
        # change cursor location
        bpy.context.scene.cursor.location =(selected_object_active.location.x,selected_object_active.location.y,context.scene.my_number_settings.my_number_property_foam_block_z/2)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        foamBlock = bpy.context.object        
        foamBlock.name = "foamBlock.001"
        foamBlock.dimensions = (context.scene.my_number_settings.my_number_property_foam_block_x, context.scene.my_number_settings.my_number_property_foam_block_y, context.scene.my_number_settings.my_number_property_foam_block_z)
        bpy.ops.object.transform_apply(scale=True)

        # change cursor location
        bpy.context.scene.cursor.location.z = 0
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Get the object to apply the mod
        obj = bpy.context.object
        # Move the object
        obj.location.z = 0

        areaCNC = self.crate_cnc_area(foamBlock)
                
        #lock modification but Z rotation       
        areaCNC.lock_rotation= (True, True, True)
        areaCNC.lock_location = (True, True, True)
        areaCNC.lock_scale = (True, True, True)
        areaCNC.hide_select = True
        #make areaCNC and block just wire visible
        areaCNC.display_type = "WIRE"
        foamBlock.display_type = "WIRE"

        # Create a new collection for the related objects
        blocks_collection = bpy.data.collections.new(f"small_parts.000")

        original_collection = foamBlock.users_collection[0]
        original_collection.objects.unlink(foamBlock)
        blocks_collection.objects.link(foamBlock)

        '''original_collection = selected_object_active.users_collection[0]
        original_collection.objects.unlink(selected_object_active)
        blocks_collection.objects.link(selected_object_active)'''

        for object_selected in selected_objects:
            original_collection = object_selected.users_collection[0]
            original_collection.objects.unlink(object_selected)
            blocks_collection.objects.link(object_selected)

        original_collection = areaCNC.users_collection[0]
        original_collection.objects.unlink(areaCNC)
        blocks_collection.objects.link(areaCNC)
        
        # Add the created collection to the scene
        bpy.context.scene.collection.children.link(blocks_collection)

    def change_scale(self, size):
        # Obtener el objeto seleccionado
        obj = bpy.context.active_object

        # Obtener la malla de la duplicado
        mesh = bpy.context.active_object.data

        if mesh is not None and bpy.context.active_object.select_get():

            bpy.ops.object.transform_apply(scale=True)

            # Calcular el área actual del objeto 3D poligonal irregular
            area_actual = self.get_total_area_vol(mesh)[0]

            # Calcular la nueva escala para que el área total sea 500
            nueva_escala = math.sqrt(float(size) / area_actual)

            # Escalar el objeto con la nueva escala
            obj.scale = (nueva_escala, nueva_escala, nueva_escala)

            # Actualizar la malla después de la escala
            bpy.ops.object.convert(target='MESH')
            mesh = bpy.context.active_object.data

            bpy.ops.object.transform_apply(scale=True)

            # Calcular el nuevo área después de la escala
            nueva_area = self.get_total_area_vol(mesh)[0]

            # Imprimir los resultados
            print(f"Área actual: {area_actual}")
            print(f"Nueva escala: {nueva_escala}")
            print(f"Nueva área: {nueva_area}")

    def get_total_area_vol(self, mesh = None):
        if mesh is None and bpy.context.active_object.select_get():
            mesh = bpy.context.active_object
            print(mesh.data.name)
            copy_obj = mesh.copy()
            copy_obj.data = mesh.data.copy()
            bpy.context.collection.objects.link(copy_obj)
            
            bpy.context.view_layer.objects.active = copy_obj
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.transform_apply(scale=True)
            mesh_copy = copy_obj.data

            # calc the volume
            me = copy_obj.to_mesh()
            #me.transform(matrix)
            bm = bmesh.new()
            bm.from_mesh(me)

            volume = bm.calc_volume(signed=True)
            bm.free()
            #print('*volume*', volume)
            # --- Calcular el área actual del objeto 3D poligonal irregular
            area = sum(polygon.area for polygon in mesh_copy.polygons)

            # Eliminar la copia
            bpy.data.objects.remove(copy_obj, do_unlink=True)

            bpy.context.view_layer.objects.active = mesh
        elif bpy.context.active_object.select_get():
            # Calcular el área actual del objeto 3D poligonal irregular
            area = sum(polygon.area for polygon in mesh.polygons)
            volume = 1 #add volume logic here
        elif mesh is not None:
            print(f'nombre----{mesh.name}')
            mesh = bpy.data.objects[mesh.name]
            copy_obj = mesh.copy()
            copy_obj.data = mesh.data.copy()
            bpy.context.collection.objects.link(copy_obj)
            
            bpy.context.view_layer.objects.active = copy_obj
            copy_obj.hide_select = False
            copy_obj.select_set(True)
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.transform_apply(scale=True)
            mesh_copy = copy_obj.data

            # calc the volume
            me = copy_obj.to_mesh()
            #me.transform(matrix)
            bm = bmesh.new()
            bm.from_mesh(me)

            volume = bm.calc_volume(signed=True)
            bm.free()
            #print('*volume*', volume)
            # --- Calcular el área actual del objeto 3D poligonal irregular
            area = sum(polygon.area for polygon in mesh_copy.polygons)

            # Eliminar la copia
            bpy.data.objects.remove(copy_obj, do_unlink=True)
            #area = 2
            #volume = 2 #add volume logic here
        else:
            area = 0
            volume = 0 #add volume logic here

        print(area)
        return area, volume

#myFunc = funcs()

# BUTTON CUSTOM (OPERATOR)
####################################################

class INPUT_TEXT_01(bpy.types.PropertyGroup):
    
    my_text_property_x: bpy.props.StringProperty(
        name="X", default="", description="Introduce un valor para X")

    my_text_property_y: bpy.props.StringProperty(
        name="Y", default="", description="Introduce un valor para Y")

    my_text_property_z: bpy.props.StringProperty(
        name="Z", default="", description="Introduce un valor para Z")
    
    my_text_property_area: bpy.props.StringProperty(
        name="Z", default="", description="Introduce Area en metros cuadrados")
    
class INPUT_NUMBER_01(bpy.types.PropertyGroup):

    my_number_property_foam_block_x: bpy.props.FloatProperty(
        name="foam_block_x", default=1.410, description="Valor X para el bloque de Foam")
    
    my_number_property_foam_block_y: bpy.props.FloatProperty(
        name="foam_block_y", default=0.980, description="Valor Y para el bloque de Foam")
    
    my_number_property_foam_block_z: bpy.props.FloatProperty(
        name="foam_block_z", default=1.180, description="Valor Z para el bloque de Foam")
    
    my_number_property_cut_thickness: bpy.props.FloatProperty(
        name="cut_thickness", default=1.180, description="Valor X para el bloque de Foam")

    my_number_property_volume_total_irregular: bpy.props.FloatProperty(
        name="volume_total_irregular", default=0, description="Volumen total de la superficie irregular")
    
    my_number_property_volume_total_cubes: bpy.props.FloatProperty(
        name="volume_total_cubes", default=1, description="Valumen total de los bloques Foam")
    
    my_number_property_quantity_cubes: bpy.props.FloatProperty(
        name="quantity_cubes", default=0, description="Cantidad de bloques Foam usados aproximadamente")
    
class BUTTOM_SET_AREA(bpy.types.Operator):
    bl_label = "BUTTOM_SET_AREA"
    bl_idname = "object.button_set_area"
    bl_options = {'UNDO'}

    def execute(self, context):

        area = context.scene.my_text_settings.my_text_property_area
        #func = myFunc        
        func = funcs()
        func.change_scale(area)
        return {'FINISHED'}
    
class BUTTOM_GET_AREA(bpy.types.Operator):
    bl_label = "BUTTOM_GET_AREA"
    bl_idname = "object.button_get_area"

    def execute(self, context):
        #func = myFunc
        func = funcs()
        
        context.scene.my_text_settings.my_text_property_area = str(round(func.get_total_area_vol()[0],2))
               
        return {'FINISHED'}
    
class BUTTOM_SET_FOAM_SIZE(bpy.types.Operator):
    bl_label = "BUTTOM_SET_FOAM_SIZE"
    bl_idname = "object.button_buttom_set_foam_size"
    bl_options = {'UNDO'}

    def execute(self, context):

        x_value = float(context.scene.my_text_settings.my_text_property_x)
        y_value = float(context.scene.my_text_settings.my_text_property_y)
        z_value = float(context.scene.my_text_settings.my_text_property_z)

        context.scene.my_number_settings.my_number_property_foam_block_x = x_value
        context.scene.my_number_settings.my_number_property_foam_block_y = y_value
        context.scene.my_number_settings.my_number_property_foam_block_z = z_value

        #func = myFunc
        func = funcs()

        func.setSizeBlock(context, x_value, y_value, z_value)

        print(f"Valores introducidos: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados: X={func.foam_block_x}, Y={func.foam_block_y}, Z={func.foam_block_z}")
        return {'FINISHED'}

class BUTTOM_SET_FOAM_DEFAULT(bpy.types.Operator):
    bl_label = "BUTTOM_SET_FOAM_DEFAULT"
    bl_idname = "object.button_buttom_set_foam_default"
    bl_options = {'UNDO'}

    def execute(self, context):
        #func = myFunc
        func = funcs()

        x_value = round(func.foam_block_x, 2) 
        y_value = round(func.foam_block_y, 2) 
        z_value = round(func.foam_block_z, 2)

        
        context.scene.my_number_settings.my_number_property_foam_block_x = x_value
        context.scene.my_number_settings.my_number_property_foam_block_y = y_value
        context.scene.my_number_settings.my_number_property_foam_block_z = z_value
        
        func.setSizeBlock(context, x_value, y_value, z_value)
        print(f"Valores introducidos: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados: X={func.foam_block_x}, Y={func.foam_block_y}, Z={func.foam_block_z}")
        return {'FINISHED'}


class BUTTOM_CUSTOM01(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM01_Prepare"
    bl_idname = "object.button_custom01"
    bl_options = {'UNDO'}

    def execute(self, context):
        #func = myFunc
        func = funcs()

        x_value = context.scene.my_number_settings.my_number_property_foam_block_x
        y_value = context.scene.my_number_settings.my_number_property_foam_block_y
        z_value = context.scene.my_number_settings.my_number_property_foam_block_z

        print(f"Valores Recuperados BTN01: X={x_value}, Y={y_value}, Z={z_value}")
        func.crate_around_object(context)
        
        print("execute button01 ---custom ok!")

        return {'FINISHED'}
    
class BUTTOM_CUSTOM02(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM02_Cut"
    bl_idname = "object.button_custom02"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        #func = myFunc
        func = funcs()
        func.cut_and_order_parts(context)
        
        print("execute button02 custom ok!")

        return {'FINISHED'}
    
#----------------------------------------------------------    

class BUTTOM_CUSTOM03(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM03_CutFoam"
    bl_idname = "object.button_custom03"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        #funcion.cut_wood()
        funcion.create_silhouette()

        print("execute button03 custom ok!")

        return {'FINISHED'}
    
class BUTTOM_CUSTOM04(bpy.types.Operator):
    bl_label = "Calibrate Cut in Z axis"
    bl_idname = "object.button_custom04"
    bl_options = {'REGISTER','UNDO'} #REGISTER popup a little window in the left down corner to introduce the parameters values

    udpdate_value_bool : bpy.props.BoolProperty(
        name="update", 
        default=False, 
        options={'HIDDEN','SKIP_SAVE'}
        )
    
    def execute_updater(self, context):
        
        self.udpdate_value_bool = True

        return None

    location_z: bpy.props.FloatProperty(
        name="Z",
        description="location in the Z axis for the silhouette_cut",
        default=-0.001,
        min=-0.009,
        soft_max=-0.0005,step=0.001,
        update=execute_updater,
        options={'SKIP_SAVE'}
    )

    def execute(self, context):
        
        funcion = funcs()
        funcion.cut_silhouette(self.location_z,self.udpdate_value_bool)
        #funcion.reorder_vertices(0)
        
        print("execute button04 custom ok!, Update:" + str(self.udpdate_value_bool))

        return {'FINISHED'}
    
class BUTTOM_CUSTOM05(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM05_CutFoam"
    bl_idname = "object.button_custom05"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.export_gcode_raw(context)

        print("execute button05 custom ok!")

        return {'FINISHED'}

#-----------------------------------------------------------

class BUTTOM_CUSTOM06(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM06_CutFoam"
    bl_idname = "object.button_custom06"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.create_block_apart()

        print("execute button06 custom ok!")

        return {'FINISHED'}    

class BUTTOM_CUSTOM07(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM07_CutFoam"
    bl_idname = "object.button_custom07"
    bl_options = {'UNDO'}

    global funcion

    def execute(self, context):
        
        BUTTOM_CUSTOM07.funcion = funcs()
        BUTTOM_CUSTOM07.funcion.draw_init()

        print("execute button07 custom ok!")

        return {'FINISHED'} 
    @classmethod
    def description(cls, context, properties):
        return "draw_init()"

class BUTTOM_CUSTOM08(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM08_CutFoam"
    bl_idname = "object.button_custom08"
    bl_options = {'UNDO'}

    def execute(self, context):
        
       #self.funcion = funcs()
        BUTTOM_CUSTOM07.funcion.gpencil_to_mesh()

        print("execute button08 custom ok!")

        return {'FINISHED'}     
     
# PANEL UI (PART 1 DRAW)
####################################################

class PANEL_CUSTOM_UI_00(bpy.types.Panel):
    bl_label = "Prepare Irregular Model"
    bl_idname = "OBJECT_PT_panel_00"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Muestra los valores actuales en labels
        row = layout.row()
        row.label(text=f"Cambiar Area Total")

        # add text input for Z
        row = layout.row()
        row.prop(context.scene.my_text_settings, "my_text_property_area", text="Area")
        
        # add button custom
        row = layout.row()
        row.operator(BUTTOM_SET_AREA.bl_idname, text="Set Area")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_GET_AREA.bl_idname, text="Get Area")

class PANEL_CUSTOM_UI_01(bpy.types.Panel):
    bl_label = "Prepare Cut Model"
    bl_idname = "OBJECT_PT_panel_01"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"

    def draw(self, context):
        #variables
        layout = self.layout

        #func = myFunc
        func = funcs()

        x = round(context.scene.my_number_settings.my_number_property_foam_block_x,2)
        y = round(context.scene.my_number_settings.my_number_property_foam_block_y,2)
        z = round(context.scene.my_number_settings.my_number_property_foam_block_z,2)

        vol_total_irreg= round(context.scene.my_number_settings.my_number_property_volume_total_irregular,2)
        vol_total_cube= round(context.scene.my_number_settings.my_number_property_volume_total_cubes,2)
        vol_total_quantity= round(context.scene.my_number_settings.my_number_property_quantity_cubes,2)

        '''volume_total_irregular = volumen_total_irregular_obj
        volume_total_cubes = volumen_total_cube_obj
        quantity_cubes = quantity_cube_obj'''

        # Muestra los valores actuales en labels
        row = layout.row()
        row.label(text=f"Cube Size:")
        row = layout.row()
        row.label(text=f"X={x}, Y={y}, Z={z}")

        # add text input for X
        row = layout.row()
        row.prop(context.scene.my_text_settings, "my_text_property_x", text="X")

        # add text input for Y
        row = layout.row()
        row.prop(context.scene.my_text_settings, "my_text_property_y", text="Y")

        # add text input for Z
        row = layout.row()
        row.prop(context.scene.my_text_settings, "my_text_property_z", text="Z")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_SET_FOAM_SIZE.bl_idname, text="Set Size")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_SET_FOAM_DEFAULT.bl_idname, text="Default Size")

        #create simple row
        row01 = layout.row()
        row01.label(text = "First Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator(BUTTOM_CUSTOM01.bl_idname, text= "Prepare Work Area", icon = "GRID")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Second Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom02", text= "Prepare Cuts in CNC Hot Wire", icon = "IMGDISPLAY")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"-------------------VOLUMENES----------------------")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Volume Isla: {round(vol_total_irreg,2)} m3")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Cubos Completos Usados: {vol_total_quantity} cubos")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Volume Cubos Completos Usados: {round(vol_total_cube,2)} m3")

        vol_used=round((vol_total_irreg/vol_total_cube)*100,2)
        cubes_used=round(vol_used/100 * vol_total_quantity,2)
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Porcentaje real cubos usados: {vol_used}%")
        
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Cantidad real cubos usados: {cubes_used} cubos")

class PANEL_CUSTOM_UI_02(bpy.types.Panel):
    bl_label = "CNC Hot-Wire"
    bl_idname = "OBJECT_PT_panel_02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"    
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        #variables
        layout = self.layout

        #create simple row
        row01 = layout.row()
        row01.label(text = "Oculte las partes no usadas")

        #create simple row
        row01 = layout.row()
        row01.label(text = "First Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom03", text= "Create Silhouette", icon = "MOD_SHRINKWRAP")

        #create simple row
        row01 = layout.row()
        row01.label(text = "Second Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom04", text= "Cut silhouette", icon = "SCULPTMODE_HLT")

        #create simple row
        row01 = layout.row()
        row01.label(text = "Second Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom05", text= "Export GCODE and RawForm", icon = "FILE_TICK")

class PANEL_CUSTOM_UI_03(bpy.types.Panel):
    bl_label = "Small Parts"
    bl_idname = "OBJECT_PT_panel_03"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        #variables
        layout = self.layout

        #create simple row
        row01 = layout.row()
        row01.label(text = "First Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom06", text= "Prepare Block for small parts", icon = "GRID")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Second Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom06", text= "Prepare Cuts in CNC Hot Wire", icon = "IMGDISPLAY")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Thirth Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom07", text= "Test01", icon = "IMGDISPLAY")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Fourth Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom08", text= "Test02", icon = "IMGDISPLAY")

# REGISTER (PART 2)
####################################################
def register():
    bpy.utils.register_class(PANEL_CUSTOM_UI_00)
    bpy.utils.register_class(PANEL_CUSTOM_UI_01)
    bpy.utils.register_class(PANEL_CUSTOM_UI_02)
    bpy.utils.register_class(PANEL_CUSTOM_UI_03)
    bpy.utils.register_class(INPUT_TEXT_01)
    bpy.utils.register_class(INPUT_NUMBER_01)
    bpy.types.Scene.my_text_settings = bpy.props.PointerProperty(type=INPUT_TEXT_01)    
    bpy.types.Scene.my_number_settings = bpy.props.PointerProperty(type=INPUT_NUMBER_01)
    bpy.utils.register_class(BUTTOM_SET_AREA)
    bpy.utils.register_class(BUTTOM_GET_AREA)
    bpy.utils.register_class(BUTTOM_SET_FOAM_SIZE)
    bpy.utils.register_class(BUTTOM_SET_FOAM_DEFAULT)
    bpy.utils.register_class(BUTTOM_CUSTOM01)
    bpy.utils.register_class(BUTTOM_CUSTOM02)
    bpy.utils.register_class(BUTTOM_CUSTOM03)
    bpy.utils.register_class(BUTTOM_CUSTOM04)
    bpy.utils.register_class(BUTTOM_CUSTOM05)
    bpy.utils.register_class(BUTTOM_CUSTOM06)
    bpy.utils.register_class(BUTTOM_CUSTOM07)
    bpy.utils.register_class(BUTTOM_CUSTOM08)

def unregister():
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_00)
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_01)
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_02)
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_03)
    bpy.utils.unregister_class(INPUT_TEXT_01)
    bpy.utils.unregister_class(INPUT_NUMBER_01)
    del bpy.types.Scene.my_text_settings
    del bpy.types.Scene.my_number_settings
    bpy.utils.unregister_class(BUTTOM_SET_AREA)
    bpy.utils.unregister_class(BUTTOM_GET_AREA)
    bpy.utils.unregister_class(BUTTOM_SET_FOAM_SIZE)
    bpy.utils.unregister_class(BUTTOM_SET_FOAM_DEFAULT)
    bpy.utils.unregister_class(BUTTOM_CUSTOM01)
    bpy.utils.unregister_class(BUTTOM_CUSTOM02)
    bpy.utils.unregister_class(BUTTOM_CUSTOM03)
    bpy.utils.unregister_class(BUTTOM_CUSTOM04)
    bpy.utils.unregister_class(BUTTOM_CUSTOM05)
    bpy.utils.unregister_class(BUTTOM_CUSTOM06)
    bpy.utils.unregister_class(BUTTOM_CUSTOM07)
    bpy.utils.unregister_class(BUTTOM_CUSTOM08)

if __name__ == "__main__":
    register()
    #myFunc = funcs()
    

print("execute script OK!")