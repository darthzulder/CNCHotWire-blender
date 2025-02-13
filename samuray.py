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

# Importaciones estándar
import os
import errno
import math
import re

# Importaciones de Blender
import bpy
import bmesh
from mathutils import Vector
import mathutils
# Importaciones locales (si las hubiera)
# from . import funciones  # Descomentar si se utilizan funciones de otros módulos

func = None
#Funciones
class funcs():

    # meters
    foam_block_x = 1.410
    foam_block_y = 0.980
    foam_block_z = 1.180

    dist_X_center = 1.137

    cut_thickness_x = 0.02
    cut_thickness_y = 0.06
    cut_thickness_z = 0.002

    margin = 0.01 #magen alrededor de la madera para la espuma liquida.
    variable_size = 8/1000 #suma 8mm, 4mm por lado por la variabilidad del tamaño de la madera

    wood_total_heigh = 0.042 + variable_size
    wood_total_width = 0.141 + variable_size
    wood_total_depth = 4.347

    volume_total_irregular = 0
    volume_total_cubes = 1
    quantity_cubes = 0

    # list of top objects that will be grouped and will be cut
    list_top_objects = []    
    
    # Sensibilidad del giro en grados
    sensitivity = 15.0

    def __init__(self):
        self.select_before = None
        # top object that will be blocked
        self.main_top_object_blocked = ""
        # top object that will be groupen to the blocked object
        self.top_object_to_group = ""

    def set_size_block(self,context, x, y, z):
        # Actualiza los valores introducidos por el usuario
        self.foam_block_x = float(x)
        self.foam_block_y = float(y)
        self.foam_block_z = float(z)

        context.scene.my_text_settings.my_text_property_x = ""
        context.scene.my_text_settings.my_text_property_y = ""
        context.scene.my_text_settings.my_text_property_z = ""

        print(f"Valores introducidos bloques: X={x}, Y={y}, Z={z}")

    def set_size_wood(self,context, x, y, z):
        # Actualiza los valores introducidos por el usuario
        self.wood_total_depth = float(z)
        self.wood_total_width = float(y)
        self.wood_total_heigh = float(x)

        context.scene.my_text_settings.my_text_property_x = ""
        context.scene.my_text_settings.my_text_property_y = ""
        context.scene.my_text_settings.my_text_property_z = ""

        print(f"Valores introducidos maderas: X={x}, Y={y}, Z={z}")

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
        dist_X_center = self.dist_X_center #distance X from bootom to center
        
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

    def create_block_greed (self, dimensions_X, dimensions_Y, dimensions_Z, foam_size_X, foam_size_Y, foam_size_Z, separation_x, separation_y , scale = 1):
        #print(f"-------create_block_greed>{dir}")
        # IN METERS
        n_blocks_x = math.ceil(dimensions_X/foam_size_X)
        n_blocks_y = math.ceil(dimensions_Y/foam_size_Y)
        n_blocks_z = math.ceil((dimensions_Z+separation_x)/foam_size_Z)
                                          
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
        obj.location = (separation_x/2,separation_y/2,foam_size_Z/2)

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
        array_modifier1.constant_offset_displace = (0.0, separation_y*scale, 0.0)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier2.count = n_blocks_x  # Número de repeticiones
        array_modifier2.relative_offset_displace = (1.0, 0.0, 0.0)  # Desplazamiento relativo
        array_modifier2.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier2.constant_offset_displace = (separation_x*scale, 0.0, 0.0)  # Desplazamiento constante

        if n_blocks_z > 1 :
            array_modifier3 = obj.modifiers.new(name="Array_Z", type='ARRAY')
            array_modifier3.count = n_blocks_z  # Número de repeticiones
            array_modifier3.relative_offset_displace = (0.0, 0.0, 1.0)  # Desplazamiento relativo
            array_modifier3.use_constant_offset = True  # Usar desplazamiento constante
            #array_modifier3.constant_offset_displace = (0.0, 0.0, separation*scale)  # Desplazamiento constante
            array_modifier3.constant_offset_displace = (0.0, 0.0, self.cut_thickness_z*scale)  # Desplazamiento constante
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

    def create_cutter_planes (self, dimensions_X,dimensions_Y, dimensions_Z, separation_z, separation_x, separation_y,  plane_thickness_x,  plane_thickness_y, scale = 1):               

        plane_size_high = (dimensions_Z+0.5)
        #division_hight_z = plane_thickness
        division_hight_z = self.cut_thickness_z

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
        array_modifier_X2.thickness = plane_thickness_x

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
        array_modifier_Y2.thickness = plane_thickness_y

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
        array_modifier_Z1 = cutterPlane_Z.modifiers.new(name="Array_Z", type='ARRAY')
        # Agregar el modificador Array
        array_modifier_Z2 = cutterPlane_Z.modifiers.new(name="Solidify_Z", type='SOLIDIFY')

        # Definir las propiedades del modificador
        array_modifier_Z1.count = faces_count_z  # Número de repeticiones
        array_modifier_Z1.relative_offset_displace = (0.0, 0.0, 1.0)  # Desplazamiento relativo
        array_modifier_Z1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_Z1.constant_offset_displace = (0.0, 0.0, separation_z + division_hight_z)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier_Z2.offset = 0
        #array_modifier_Z2.thickness = plane_thickness
        array_modifier_Z2.thickness = division_hight_z

    def crate_cnc_area (self, object_scope, scale = 1):
        #print(f"-------create_cnc_area>{dir}")
        
        cnc_size_X = 2.150
        cnc_size_Y = 2.095
        cnc_size_Z = 1.250
        dist_X_center = self.dist_X_center #distance X from bootom to center

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

    def create_woods (self, context, dimensions_X,dimensions_Y, dimensions_Z, separation_z, separation_x, separation_y,  plane_thickness_x,  plane_thickness_y, scale = 1):

        plane_size_high = (separation_z+0.5)

        wood_heigh = context.scene.my_number_settings.my_number_property_wood_x
        wood_width = context.scene.my_number_settings.my_number_property_wood_y
        wood_depth = context.scene.my_number_settings.my_number_property_wood_z

        faces_count_x = math.ceil(dimensions_X/separation_x)
        faces_count_y = math.ceil(dimensions_Y/separation_y)

        dim_plane_x=math.ceil(dimensions_X/separation_x)*separation_x+1.5
        dim_plane_y=math.ceil(dimensions_Y/separation_y)*separation_y+2
            
        #location_x = (dim_plane_x-1.5)/2
        #location_y = (dim_plane_y-2)/2
        #location_z = (plane_size_high-0.5)/2

        location_x = (dim_plane_x-1.5)/2
        location_y = (dim_plane_y-2)/2
        #location_z = wood_heigh/2+wood_width #floor position
        location_z = (plane_size_high-0.5)/2

        # -----create primitive Plane as cutterPlane --Cuts in X--
        # change cursor location
        bpy.context.scene.cursor.location =(separation_x-(wood_width/2), location_y, location_z-(wood_heigh/2+wood_width/2))
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
        bpy.context.scene.cursor.location =(location_x, separation_y, location_z)
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
        wood_x = context.scene.my_number_settings.my_number_property_wood_x
        separation_x = self.cut_thickness_x

        separation_y = wood_x + self.margin #
        self.cut_thickness_y = separation_y
        saved_location = bpy.context.scene.cursor.location.xyz   # returns a vector
            

        x_value = context.scene.my_number_settings.my_number_property_foam_block_x
        y_value = context.scene.my_number_settings.my_number_property_foam_block_y
        z_value = context.scene.my_number_settings.my_number_property_foam_block_z

        foam_block_hight_x = x_value + separation_x
        foam_block_hight_y = y_value + separation_y
        foam_block_hight_z = z_value

        print(f"from context foam_block_hight_x:{foam_block_hight_x} foam_block_hight_y:{foam_block_hight_y} foam_block_hight_z:{foam_block_hight_z}")
        print(f"from self foam_block_hight_x:{self.foam_block_x} foam_block_hight_y:{self.foam_block_y} foam_block_hight_z:{self.foam_block_z}")

        #separation_x = self.cut_thickness_x
        #separation_y = self.cut_thickness_y

        # get object
        selected_object = bpy.context.active_object
        # get object dimensions
        dimensions = selected_object.dimensions

        # get new origin coordinates
        dimensions_X = round(dimensions.x,1)
        dimensions_Y = round(dimensions.y,1)
        dimensions_Z = round(dimensions.z,1)   

        

        self.create_cutter_planes(dimensions_X,dimensions_Y,dimensions_Z,foam_block_hight_z,foam_block_hight_x,foam_block_hight_y,separation_x,separation_y, scale = 1) 
        self.create_woods(context, dimensions_X,dimensions_Y,dimensions_Z,foam_block_hight_z,foam_block_hight_x,foam_block_hight_y, separation_x,separation_y, scale = 1)

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

        separation_x = self.cut_thickness_x
        separation_y = self.cut_thickness_y

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

        self.create_block_greed(dimensions_X,dimensions_Y,dimensions_Z,foam_size_X, foam_size_Y, foam_size_Z, separation_x, separation_y, scale = 1)

    def cut_and_order_parts(self, context):
        print('******inner_part_verif***********')
        
        self.write_to_file_block_base_cut(context)
        #save state in case of error
        bpy.ops.ed.undo_push(message="inner_part_verif Function")
        #try:
        collections_name = "P"
        cubes_name = "foamBlock"
        object_selected_name = "irregObjPart"
        bpy.context.active_object.name = f"{object_selected_name}.001"
        #fix location in z to pass the inner verification, if z location is 0 may have conflict to check if is inside the cube due the cube Z location is 0
        if bpy.context.active_object.location.z == 0: bpy.context.active_object.location.z=+0.0001

        foam_size_Z = context.scene.my_number_settings.my_number_property_foam_block_z
        selected_object = bpy.context.active_object
        # get new origin coordinates
        dimensions_Z = selected_object.dimensions.z
        n_blocks_z = math.ceil((dimensions_Z+self.cut_thickness_x)/foam_size_Z)
        self.list_top_objects = []

        self.cut_object(context)
        # Get a list of all cube objects and irregular objects in the scene
        objects_cube      = [object for object in bpy.data.objects if object.name.startswith(f"{cubes_name}.")]
        #objects_irregular = [object for object in bpy.data.objects if object.name.startswith(f"{object_selected_name}.")]

        objects_irregular = []
        for object in bpy.data.objects:
            object['Top'] = False
            if object.name.startswith(f"{object_selected_name}."):
                objects_irregular.append(object)


        # Dictionary to store the relationship between cube objects and irregular objects
        relation_cube_irregular = {}

        
        vol_cubo_obj = abs(context.scene.my_number_settings.my_number_property_foam_block_x*context.scene.my_number_settings.my_number_property_foam_block_y*context.scene.my_number_settings.my_number_property_foam_block_z)

        extra_x = self.cut_thickness_x
        extra_y = self.cut_thickness_y
        extra_z = self.cut_thickness_z

        '''extra_x = 0
        extra_y = 0
        extra_z = 0'''


        for object_cube in objects_cube:
            # # Get the world coordinates bounding-box-points of object_cube
            bbox_cube = [['%.4f' % elem for elem in object_cube.matrix_world @ Vector(coor)] for coor in object_cube.bound_box]
            have_something_inside = 0
            # Check if each irregular object is contained within any cube object
            for object_irregular in objects_irregular:
                # Get the world coordinates of the bounding-box-points of object_irregular
                bbox_irregular = [ ['%.4f' % elem for elem in object_irregular.matrix_world @ Vector(coor)] for coor in object_irregular.bound_box]

                # # Check if the bounding box of the irregular object is contained within the bounding box of the cube object
                is_inside = all((
                    float(bbox_cube[0][0])-extra_x <= float(bbox_irregular[0][0]) <= float(bbox_cube[6][0])+extra_x and
                    float(bbox_cube[0][0])-extra_x <= float(bbox_irregular[6][0]) <= float(bbox_cube[6][0])+extra_x ,

                    float(bbox_cube[0][1])-extra_y <= float(bbox_irregular[0][1]) <= float(bbox_cube[6][1])+extra_y and
                    float(bbox_cube[0][1])-extra_y <= float(bbox_irregular[6][1]) <= float(bbox_cube[6][1])+extra_y ,

                    float(bbox_cube[0][2])-extra_z <= float(bbox_irregular[0][2]) <= float(bbox_cube[6][2])+extra_z and
                    float(bbox_cube[0][2])-extra_z <= float(bbox_irregular[6][2]) <= float(bbox_cube[6][2])+extra_z)
                )
                
                '''is_inside = all(
                    float(bbox_cube[0][i]) <= float(bbox_irregular[0][i]) <= float(bbox_cube[6][i]) and
                    float(bbox_cube[0][i]) <= float(bbox_irregular[6][i]) <= float(bbox_cube[6][i])
                    for i in range(3)
                )'''                

                if is_inside:
                    relation_cube_irregular[object_irregular.name] = object_cube.name
                    have_something_inside = 1
                    #print(f'===={object_irregular.name} - {object_cube.name}=====')
                    #for i in range (3):                        
                        #print(f'c0|{i}:{bbox_cube[0][i]} <= i{i}|{i}:{bbox_irregular[i][i]} <= c6|{i}:{bbox_cube[6][i]}//c0|{i}:{bbox_cube[0][i]} <= i7|{i}:{bbox_irregular[7][i]} <= c6|{i}:{bbox_cube[6][i]}')
                '''if object_irregular.name == 'irregObjPart.047': #and object_cube.name == 'foamBlock.113':
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
                #self.cut_wood(context, object_irregular_obj,'y')
            #are top objects? set it as top
            if (n_blocks_z-1) * foam_size_Z <= object_irregular_obj.location.z:
                self.list_top_objects.append(object_irregular_obj.name)
                bpy.data.objects[object_irregular]['Top'] = True

                #print(f"Elemento Top {n_blocks_z}-- bloquesZ {(n_blocks_z-1) * foam_size_Z} objZ--> {object_irregular_obj.location.z} obj--> {object_irregular_obj}")
            #----create STL file of irregular object
            collection_name = object_irregular_obj.users_collection[0].name
            self.export_to_stl_origin(context,collection_name,collection_name,"irregObjPart.")
        print(f'---------Volumen Total del irregular = {volumen_total_irregular_obj}')
        print(f'---------Volumen Total del cubes = {volumen_total_cube_obj}')
        bpy.context.scene["my_top_object_list"] = self.list_top_objects
        print(f"-----------------------Cantidad de objetos top {len(bpy.context.scene['my_top_object_list'])}")
        #vol_used = volumen_total_irregular_obj / volumen_total_cube_obj * 100
        #print(f'---------Volumen Used = {round(vol_used,2)}%')

        context.scene.my_number_settings.my_number_property_volume_total_irregular = volumen_total_irregular_obj
        context.scene.my_number_settings.my_number_property_volume_total_cubes = volumen_total_cube_obj
        context.scene.my_number_settings.my_number_property_quantity_cubes = quantity_cube_obj
        #except Exception as e:
            #print("Error Custon Function, UNDO:", e)
            # UnDo in case of error
            #bpy.ops.ed.undo()
    
    def write_to_file_block_base_cut(self, context):
        
        foam_block_x = self.foam_block_x*1000
        foam_block_y = self.foam_block_y*1000
        foam_block_z = self.foam_block_z*1000
        dist_X_center = self.dist_X_center*1000


        front_x = dist_X_center - (foam_block_x/2)
        back_x = dist_X_center + (foam_block_x/2)
        left_y = dist_X_center - (foam_block_y/2)
        right_y = dist_X_center + (foam_block_y/2)

        scale=1000
        i=0
        pathFileName=".\\PARTES\\BaseCleanBlock"
            
        pathFileNumber=pathFileName+".nc"
        #create .nc file 
        try:
            os.makedirs(".\\PARTES\\", exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        f = open(pathFileNumber,"w+")
        f.write(f'(GCODE_from_Blender)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')
        
        #direction will be from +X  to -X
      
        f.write(f"G01X{front_x}Y{0}A{0}\n") 
        f.write(f"G01X{front_x}Y{foam_block_z}A{0}\n")
        f.write(f"G01X{back_x}Y{foam_block_z}A{0}\n")
        f.write(f"G01X{back_x}Y{0}A{0}\n")
        f.write(f"G01X{2150}Y{0}A{0}\n")
        f.write(f"G01X{2150}Y{0}A{90}\n")
        f.write(f"G01X{right_y}Y{0}A{90}\n")
        f.write(f"G01X{right_y}Y{foam_block_z}A{90}\n")
        f.write(f"G01X{left_y}Y{foam_block_z}A{90}\n")
        f.write(f"G01X{left_y}Y{0}A{90}\n")
        f.write(f"G01X{0}Y{0}A{90}\n")
        f.write(f"G01X{0}Y{0}A{0}\n")
        f.write(f'(To Origin)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')

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

    def write_to_file_by_arms(self,verts,collection_name,update=False):
        
        scale=1000
        i=0
        pathFileName=".\\PARTES\\"+collection_name+"\\"+collection_name+"."
            
        pathFileNumber=pathFileName+'%03d' % i +"_TOP_samurai.nc"
        #create .nc file 
        try:
            os.makedirs(".\\PARTES\\"+collection_name, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        while os.path.exists(pathFileNumber):
            i=i+1
            pathFileNumber=pathFileName+'%03d' % i +"_TOP_samurai.nc"
        if update == True:
            #if not wood:
            i=i-1
            pathFileNumber=pathFileName+'%03d' % i +"_TOP_samurai.nc"

        f = open(pathFileNumber,"w+")
        f.write(f'(GCODE_from_Blender)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')
        
        #direction will be from +X  to -X
        x_first = verts[0]['X']
        
        f.write(f"G01X{verts[0]['X']}Y{verts[0]['Y']}U{verts[0]['U']}V{verts[0]['V']}\n") 
        f.write(f"G01X{verts[1]['X']}Y{verts[1]['Y']}U{verts[1]['U']}V{verts[1]['V']}\n")
        f.write(f'G01X2150Y1200U2150V1200\n') 
        f.write(f'G01X0Y1200U0V1200\n')
        f.write(f'(To Origin)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000U0.0000V0.0000\nG01X0.0000Y0.0000U0.0000V0.0000\nF600\n')
    
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
            objective_object[0].location.y = -0.59 #0
            objective_object[0].location.z = 0.49 #0
            objective_object[0].rotation_euler.x = math.radians(-90) #0
            print("giro Izq")
        elif(objective_object[0].location.y > middle_pos and objective_object[0].location.z < foam_z):
            objective_object[0].location.y = 0.59 #0
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
            #print(mesh.data.name)
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

    def block_base_top_part(self, context):

        if 'top_object_block' not in context.scene:
            context.scene['top_object_block'] = context.active_object
            self.main_top_object_blocked=context.active_object
        elif context.scene['top_object_block'] == context.active_object:
            del context.scene['top_object_block']
        elif context.scene['top_object_block'] != context.active_object:    
            self.main_top_object_blocked.hide_select = False       
            context.active_object.location = context.scene['save_location']
            context.active_object.rotation_euler = [0, 0, 0]        
            print("COLECCION ACTUAL"+context.active_object.users_collection[0].name)

            for object in context.active_object.users_collection[0].objects:
                        if object.name.startswith('areaCNC.'):
                            object.hide_viewport = False
                        if object.name.startswith('foamBlock.'):
                            object.hide_viewport = False
            
            context.active_object.users_collection[0].hide_viewport = True
            context.view_layer.objects.active = context.scene['top_object_block']
            del context.scene['top_object_block']        

    def block_base_top_part_finish(self, context):        

        self.block_base_top_part(context)
        self.isolate_part_collection(context)
        context.active_object['finish']=True
        context.active_object.users_collection[0].hide_viewport = True

        
        # Hide Current Collection

    def isolate_part_collection(self, context):

        # Get the active object
        active_obj = context.active_object

        # Get all collections in the scene
        all_collections = context.scene.collection.children        

        # Hide all collections except the target collections
        for collection in all_collections:
            if collection.name != active_obj.users_collection[0].name:
                collection.hide_viewport = not collection.hide_viewport
                for objeto in collection.objects:
                    if 'finish' in objeto and objeto['finish'] == True:
                        collection.hide_viewport = not collection.hide_viewport
                        #break'''

        #print(f"Coleccion actual {active_obj.users_collection[0].name} estado {context.scene['top_object_block'].name}")

    def change_select_top_part(self, context,direction = 1):
        main_top_object_blocked = self.main_top_object_blocked
        

        top_object_list = context.scene['my_top_object_list']
        if context.active_object.select_get() == True:
            obj_active_name = context.active_object.name
            index = top_object_list.index(obj_active_name)
            coll_active_name = context.scene['top_object_block'].users_collection[0].name
            
            if obj_active_name in bpy.data.objects:  # Check if the object is in the scene
                if len(top_object_list) > 0:  # Check if the top_object_list is not empty
                    # Calculate the next index using modulo to handle wrapping around the list, when index is the last -1 in the list it will be 0
                    if direction == 0:  
                        index_next = top_object_list.index(context.scene['top_object_block'].name)
                        obj_next = bpy.data.objects[top_object_list[index_next]]
                    else:
                        index_next = (index + direction) % len(top_object_list)
                        obj_next = bpy.data.objects[top_object_list[index_next]]  # Get the next object from the list
                        while 'group' in obj_next:                        
                            obj_next = bpy.data.objects[top_object_list[index_next]] 
                            print(f"WHILE obj_next = {obj_next.name} have group = {'group' in obj_next},  obj_active_name = {obj_active_name}------------------------\n")
                            index_next = (index_next + direction) % len(top_object_list)
                else:  # If top_object_list is empty
                    index_next = 0
                    obj_next = bpy.data.objects[top_object_list[index_next]]  # Get the first object from the list
                print(f"------------------------obj_next = {obj_next.name} have group = {'group' in obj_next},  obj_active_name = {obj_active_name}------------------------\n")                
                obj_next.users_collection[0].hide_viewport = False #let selected blocked object be visible
                for object in obj_next.users_collection[0].objects:
                        if object.name.startswith('areaCNC.') and object.users_collection[0].name != coll_active_name:
                            #object.hide_viewport = not object.hide_viewport
                            object.hide_viewport = True
                            #print(f'------------> OCULTAR {object.name} = {object.hide_viewport}  coll_actual={object.users_collection[0].name} Coll_act={coll_active_name}')
                            #break
                        if object.name.startswith('foamBlock.') and object.users_collection[0].name != coll_active_name:
                            #object.hide_viewport = not object.hide_viewport
                            object.hide_viewport = True
                            #print(f'------------> OCULTAR {object.name} = {object.hide_viewport}  coll_actual={object.users_collection[0].name} Coll_act={coll_active_name}')
                            #break
                       
                if context.scene['top_object_block'].name != obj_active_name:
                    context.active_object.location = context.scene['save_location']
                    context.active_object.rotation_euler = [0, 0, 0]
                context.scene['save_location'] = obj_next.location
                obj_next.location = context.scene['top_object_block'].location

                if context.scene['top_object_block'].name != obj_active_name: #hide selected/active object collection if it is not top_object_block                                        
                    
                    for object in context.active_object.users_collection[0].objects:
                        if object.name.startswith('areaCNC.'):
                            #object.hide_viewport = not object.hide_viewport
                            object.hide_viewport = False
                            #print(f'------------> MOSTRAR {object.name} = {object.hide_viewport}')
                            #break
                        if object.name.startswith('foamBlock.'):
                            #object.hide_viewport = not object.hide_viewport
                            object.hide_viewport = False
                            #print(f'------------> MOSTRAR {object.name} = {object.hide_viewport}')
                            #break
                    
                    context.active_object.users_collection[0].hide_viewport = True
                '''for obj in context.active_object.users_collection[0].objects:
                    obj.hide_viewport = not obj.hide_viewport'''
                
                #------------------------Change selection to next object------------------------

                bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects

                #block selection of main_top_object_blocked
                if main_top_object_blocked.name == obj_next.name:
                    main_top_object_blocked.hide_select = False
                    print("main_top_object_blocked.hide_select = False\n")
                else:
                    main_top_object_blocked.hide_select = True
                    print("main_top_object_blocked.hide_select = True\n")
                obj_next.select_set(True)  # Select the next object
                bpy.context.view_layer.objects.active = obj_next  # Set the next object as the active object

            print(f"El índice de '{obj_active_name}' en la lista es: {index}")
            print(f"-----------------------Total objetos top {len(bpy.context.scene['my_top_object_list'])}")

    def rotate_top_part(self, context, axis, angle):
        
        context.active_object.rotation_euler[axis] = math.radians(angle)
        print(f"-----------------------Rotar objetos top {context.active_object.rotation_euler[axis]}")

    def group_top_part(self, context):
        # Get the main top object we work with
        
        main_object_blocked = self.main_top_object_blocked
        # Obtén la referencia al objeto activo
        objeto_activo = context.active_object
        # add base block
        objeto_activo['group'] = context.scene['top_object_block'].name
        main_object_blocked['group'] = context.scene['top_object_block'].name
        # add order
        if 'order_group' not in objeto_activo:
            objeto_activo['order_group'] = 0
        else:
            objeto_activo['order_group'] += 1

        objeto_activo.hide_select = True
        
        # Obtén la referencia a la colección del objeto activo
        actual_collection = objeto_activo.users_collection[0]

        # Crea un nuevo plano
        bpy.ops.mesh.primitive_plane_add(size=2.6, enter_editmode=False, location=objeto_activo.location)

        # Obtén el plano recién creado
        cuter_plane = bpy.context.active_object
        cuter_plane.name = "cutterPlane.001"
        cuter_plane['cutter']='plane'

        cuter_plane.lock_location = (True, True, False)
        cuter_plane.lock_scale = (True, True, True)

        # Cambia la colección del plano al mismo que el objeto activo
        cuter_plane.users_collection[0].objects.unlink(cuter_plane)
        main_object_blocked.users_collection[0].objects.link(cuter_plane)
        # Copia la colección del objeto activo a la colección de la base        
        context.scene.collection.children.unlink(objeto_activo.users_collection[0])
        main_object_blocked.users_collection[0].children.link(objeto_activo.users_collection[0])
        print(f"///////////////****{main_object_blocked.users_collection[0].name} - {objeto_activo.users_collection[0].name}")

        #bpy.context.view_layer.objects.active = objeto_copia

        for objeto in actual_collection.objects:
            if objeto.name.startswith('areaCNC.'):
                vertices_co = [vertex.co for vertex in objeto.data.vertices]
                # Print object name
                print(f"final - {objeto.name} coords_clean_area = {vertices_co}")

    def create_cutter_plane(self, context):
        main_object_blocked = self.main_top_object_blocked
        objeto_activo = context.active_object
        # Crea un nuevo plano
        bpy.ops.mesh.primitive_plane_add(size=2.6, enter_editmode=False, location=objeto_activo.location)

        # Obtén el plano recién creado
        cuter_plane = bpy.context.active_object
        cuter_plane.name = "cutterPlane.001"
        cuter_plane['cutter']='plane'

        cuter_plane.lock_location = (True, True, False)
        cuter_plane.lock_scale = (True, True, True)

        # Cambia la colección del plano al mismo que el objeto activo
        cuter_plane.users_collection[0].objects.unlink(cuter_plane)
        main_object_blocked.users_collection[0].objects.link(cuter_plane)

    def change_origin_front_left_bottom(self, context, object):
        
        obj_block = object
        #change origin to vertex to left down the block

        # Get the vertices of the object
        verts = obj_block.data.vertices

        # Get the vertex with the highest value in the X axis
        max_x = max(vert.co.x for vert in verts)
        vertice_max_x = next(vert for vert in verts if vert.co.x == max_x)

        # Get the vertex with the lowest value in the Y axis
        min_y = min(vert.co.y for vert in verts)
        vertice_min_y = next(vert for vert in verts if vert.co.y == min_y)

        # Get the vertex with the lowest value in the Z axis
        min_z = min(vert.co.z for vert in verts)
        vertice_min_z = next(vert for vert in verts if vert.co.z == min_z)

        # Calcular el nuevo origen del cubo
        new_origin = (obj_block.matrix_world @ Vector((vertice_max_x.co.x, vertice_min_y.co.y, vertice_min_z.co.z)))

        # change cursor location
        bpy.context.scene.cursor.location = new_origin
        # set the origin on the current object to the 3dcursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
    def cut_and_group_parts(self, context):
        cutter_obj = context.active_object
        actual_collection = cutter_obj.users_collection[0]
        main_object_blocked = self.main_top_object_blocked
        print(f'------------------->actual_collection.name = {actual_collection.name} \n cutter_obj.name = {cutter_obj.name}')


        for objeto in actual_collection.objects:
            if objeto.name.startswith('areaCNC.'):
                # Print object name
                #print(objeto.name)

                area_copy = objeto.copy()
                area_copy.data = objeto.data.copy()
                #show hidden block
                area_copy.hide_viewport = False
                actual_collection.objects.link(area_copy)
                area_copy.location = context.scene['top_object_block'].location
                #base block flag
                area_copy['cutter']="block"

                coords_block_pre_cut = []
                for vert in objeto.data.vertices:
                        # Almacena las coordenadas del vértice
                        coords_block_pre_cut.append(objeto.matrix_world @ vert.co)
                #print(f"original objeto {objeto.name} \ncoords_clean_area = {coords_block_pre_cut}")
                break

        for objeto in actual_collection.objects:
            if 'cutter' in objeto:
                if objeto['cutter']=='block':
                    obj_block=objeto                  

                    # Obtén la referencia al objeto mesh del objeto cubo
                    mesh = obj_block.data

                    coords_block_pre_cut = []

                    # Get the vertices of the object before cutting
                    coords_block_pre_cut = [ vert.co for vert in mesh.vertices]
                    #print(f"Copia objeto {obj_block.name} \ncoords_clean_area = {coords_block_pre_cut}")

                    #print(f"Block = {objeto['cutter']}\n")

                    boolean_modifier_block = obj_block.modifiers.new(name="temporal_cut_001", type='BOOLEAN')
                    boolean_modifier_block.solver = 'FAST'
                    boolean_modifier_block.object = bpy.data.objects['cutterPlane.001']
                    bpy.context.view_layer.objects.active = obj_block    
                    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects                
                    obj_block.hide_select = False
                    obj_block.select_set(True)             

                    bpy.ops.object.modifier_apply(modifier=boolean_modifier_block.name)
                    
                    obj_block_cut = objeto
                    mesh = obj_block_cut.data
                    # Get the vertices of the object after cutting
                    coords_block_cut = [ vert.co for vert in mesh.vertices]
                    #print(f"coords_block_cut = {coords_block_cut}\n")
                    #print(f"Block-Cut = {objeto['cutter']}\n")
                     
                    #Set coordinates to compare the block before and after cut
                    A = set(tuple((round(coor.x,4),round(coor.y,4),round(coor.z,4))) for coor in coords_block_pre_cut)
                    B = set(tuple((round(coor.x,4),round(coor.y,4),round(coor.z,4))) for coor in coords_block_cut)
                    coords_to_cut = (B-A)
                    
                    #change coords_to_cut to local coords
                    coords_to_cut_local = tuple((round(((coord[0]-self.dist_X_center)*-1000), 4), round((coord[1]*1000), 4), round((coord[2]*1000), 4)) for coord in [Vector((vert)) for vert in coords_to_cut])

                    #coords_to_cut_local = [obj_block_cut.matrix_world @ vert.co for vert in coords_to_cut] 

                    #print(f"Coords A-B to cut = {coords_to_cut} \n Coords to cut local = {coords_to_cut_local}")

                    #Group coordinates order by Y coord
                    grupos = {}
                    for tupla in coords_to_cut_local:
                        primer_elemento = tupla[0]
                        if primer_elemento in grupos:
                            grupos[primer_elemento].append(tupla)
                        else:
                            grupos[primer_elemento] = [tupla]

                    for grupo in grupos:
                        grupos[grupo] = sorted(grupos[grupo], key=lambda tupla: (tupla[0], tupla[1]))

                    #remove block that was cut
                    bpy.data.objects.remove(obj_block)

                    bpy.data.objects["cutterPlane.001"].hide_select = True
                    bpy.data.objects["cutterPlane.001"].name = 'cutterPlane.CUT.001'
                    
                    #print(f"*******002********** MAIN BLOCKED = {main_object_blocked.users_collection[0].name}")

                    # active main object
                    bpy.context.view_layer.objects.active = main_object_blocked
                    # deselect all
                    bpy.ops.object.select_all(action='DESELECT')
                    # select the main object
                    main_object_blocked.hide_select = False
                    main_object_blocked.select_set(True)

                    # set flag for cut object
                    # cutter_obj['groupto']=main_object_blocked.name
                    
                    #print(f"A = {A} \n B = {B} \n Diference = {coords_to_cut} \n Grupos = {grupos}")

                    verts = []
                    for key, coords in dict(sorted(grupos.items())).items():
                        vert = {'X': coords[0][0], 'Y': coords[0][2], 'U': coords[1][0], 'V': coords[1][2]}
                        verts.append(vert)

                    print(f"\n Verts = {verts} \n")
                    #cambiar esta funcion para que escriba el codigo en XYUV
                    self.write_to_file_by_arms(verts,actual_collection.name)#XYUV
                    
                    break        

    def get_volume(self, mesh = None):
        if mesh.type == 'MESH':
            # Crear una copia temporal del objeto para no modificar el original
            obj_copy = mesh.copy()
            obj_copy.data = mesh.data.copy()
            
            # Aplicar todas las transformaciones para asegurar un cálculo preciso
            obj_copy.matrix_world = mathutils.Matrix.Identity(4)
            
            # Crear un BMesh desde la malla
            bm = bmesh.new()
            bm.from_mesh(obj_copy.data)
            
            # Triangular las caras para mayor precisión
            bmesh.ops.triangulate(bm, faces=bm.faces)
            
            # Calcular el volumen usando BMesh
            volume = bm.calc_volume()
            
            # Limpiar
            bm.free()
            bpy.data.objects.remove(obj_copy, do_unlink=True)
            
            return volume
        else:
            return 0

    def get_wood_vol(self, context):
        obj_base = context.active_object
        wood01 = bpy.data.objects['innerWood_x.001']
        wood02 = bpy.data.objects['innerWood_y.001']
        
        for obj in [obj_base, wood01, wood02]:
            for mod in obj.modifiers:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)

        # Create a copy of the base object
        obj_base_copy = obj_base.copy()
        obj_base_copy.data = obj_base.data.copy()
        # Link the copy to the scene before using it
        context.collection.objects.link(obj_base_copy)
        
        # Add boolean modifier for wood01
        bool_mod = obj_base_copy.modifiers.new("Boolean", 'BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.solver = 'FAST'
        bool_mod.object = wood01
        
        # Set active and apply modifier
        context.view_layer.objects.active = obj_base_copy
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        
        # Calculate volume of first intersection
        volume_wood01 = self.get_volume(obj_base_copy)
        # Remove first copy
        bpy.data.objects.remove(obj_base_copy, do_unlink=True)

        # Create another copy for second intersection
        obj_base_copy = obj_base.copy()
        obj_base_copy.data = obj_base.data.copy()
        context.collection.objects.link(obj_base_copy)
        
        # Add boolean modifier for wood02
        bool_mod = obj_base_copy.modifiers.new("Boolean", 'BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.solver = 'FAST'
        bool_mod.object = wood02
        
        # Set active and apply modifier
        context.view_layer.objects.active = obj_base_copy
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        
        # Calculate volume of second intersection
        volume_wood02 = self.get_volume(obj_base_copy)
        # Remove second copy
        bpy.data.objects.remove(obj_base_copy, do_unlink=True)

        # Calculate total volume
        volume = float(volume_wood01) + float(volume_wood02)
        
        # Reset active object
        context.view_layer.objects.active = obj_base
        
        return volume

    def get_wood_weight(self, context):
        density_wood = context.scene.my_number_settings.density_wood #kg/m3
        #density_wood = 450
        wood_vol = self.get_wood_vol(context)
        self.wood_vol = wood_vol

        weight_wood = density_wood * wood_vol
        return weight_wood, wood_vol

    def get_foam_weight(self, context):
        density_foam = context.scene.my_number_settings.density_foam #kg/m3
        #density_foam = 30
        foam_vol = self.get_volume(context.active_object) - self.wood_vol
        weight_foam = density_foam * foam_vol
        return weight_foam, foam_vol

    def get_fiber_weight(self, context):
        area_foam = self.get_total_area_vol()[0]
        #height_fiber = 0.005 #meters
        height_fiber = context.scene.my_number_settings.hight_fiber/1000 #mmeters
        vol_fiber = area_foam * height_fiber #m2
        density_fiber = context.scene.my_number_settings.density_fiber #kg/m3
        #density_fiber = 200
        weight_fiber = vol_fiber * density_fiber
        return weight_fiber 

    def get_grass_area(self, context):
        object = context.active_object
        # Obtener las dimensiones y la ubicación del objeto activo
        obj_dim = object.dimensions
        obj_location_save = object.location.copy()
        # Cambiar el origen del objeto a su centro de masa
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        obj_location = object.location.copy()

        # Setear el nuevo origen en las coordenadas de obj_location_save
        bpy.context.scene.cursor.location = obj_location_save
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        # Calcular las dimensiones del plano aumentadas en 20% en X y Y (el plano debe ser algo mas grande para que pueda contener al objeto).
        plane_dim_x = obj_dim.x * 1.2
        plane_dim_y = obj_dim.y * 1.2
        # Calcular la altura del plano como 10 veces la altura del objeto (el plano debe estar realtivamente alto para poder hacer una proyeccion correcta)
        plane_dim_z = obj_dim.z * 10
        # Crear el plano en el centro del objeto
        bpy.ops.mesh.primitive_plane_add(size=1, location=(obj_location.x, obj_location.y, obj_location.z + plane_dim_z/2))
        plane = context.active_object
        # Ajustar las dimensiones del plano
        plane.dimensions = (plane_dim_x, plane_dim_y, plane_dim_z)

        # Añadir un modificador Remesh al plano activo
        remesh_modifier = plane.modifiers.new(name="Remesh", type='REMESH')
        remesh_modifier.voxel_size = 0.01
        shrinkwrap_modifier = plane.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        shrinkwrap_modifier.target = object
        shrinkwrap_modifier.offset = 0.01
        shrinkwrap_modifier.wrap_method = 'PROJECT'

        # Crear otro plano igual al que ya tenemos, sin modificadores, en la misma posición pero en Z debe estar 2 veces la altura de object
        bpy.ops.mesh.primitive_plane_add(size=1, location=(obj_location.x, obj_location.y, obj_location.z + obj_dim.z * 2))
        second_plano = context.active_object
        # Ajustar las dimensiones del segundo plano
        second_plano.dimensions = (plane_dim_x, plane_dim_y, plane_dim_z)

        # Añadir un modificador booleano al segundo plano
        boolean_modifier = second_plano.modifiers.new(name="Boolean", type='BOOLEAN')
        boolean_modifier.operation = 'INTERSECT'
        boolean_modifier.solver = 'FAST'
        boolean_modifier.object = plane
        # Aplicar el modificador booleano al segundo plano
        bpy.ops.object.modifier_apply(modifier="Boolean")

        # Eliminar completamente el objeto 'plane'
        bpy.data.objects.remove(plane, do_unlink=True)

        # Aplicar las escalas al segundo plano
        bpy.ops.object.transform_apply(scale=True)

        # Crear una copia del objeto 'segundo_plano'
        second_plano.select_set(True)
        bpy.ops.object.duplicate()
        copy_second_plano = context.active_object

        # Entrar en modo de edición del segundo plano
        bpy.ops.object.editmode_toggle()

        # Triangulación de las caras del plano
        bpy.ops.mesh.select_all(action='SELECT')
        #bpy.ops.mesh.quads_convert_to_tris()

        #----------------------------------------------------

        # Inset del plano de 0.04 (esto es el grosor estimado de la roca)
        bpy.ops.mesh.inset(thickness=0.4)

        # Eliminar solo la cara seleccionada con 'delete only faces'
        bpy.ops.mesh.delete(type='FACE')

        # Salir del modo de edición
        bpy.ops.object.editmode_toggle()

        area_rock = self.get_total_area_vol()[0]

        # Hacer que copia_segundo_plano sea el objeto activo
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = second_plano
        second_plano.select_set(True)

        area_top = self.get_total_area_vol()[0]
        self.area_top = area_top
        area_grass = area_top - area_rock
        print(f"area de la roca: {area_rock}")
        print(f"area total de la vista superior: {area_top}")
        print(f"area de la tierra: {area_grass}")

        # Eliminar completamente el objeto 'segundo_plano'
        bpy.data.objects.remove(second_plano, do_unlink=True)
        # Eliminar completamente el objeto 'copia_segundo_plano'
        bpy.data.objects.remove(copy_second_plano, do_unlink=True)

        return area_grass

    def get_grass_weight(self, context):
        area_grass = self.get_grass_area(context)
        #high_grass = 0.1 #meters
        high_grass = context.scene.my_number_settings.hight_grass/100 #cmeters
        grass_density = context.scene.my_number_settings.density_grass #kg/m3
        #grass_density = 100
        weight_grass = area_grass * high_grass * grass_density

        return weight_grass, area_grass
    # Función para rotar la vista relativa a su orientación actual
    def rotate_view(context, axis, angle_degrees):
        region_3d = context.space_data.region_3d
        angle_radians = math.radians(angle_degrees * sensitivity)
        rotation_quaternion = mathutils.Quaternion(axis, angle_radians)
        region_3d.view_rotation = rotation_quaternion @ region_3d.view_rotation
    # Función para actualizar la sensibilidad
    def update_sensitivity(self, context):
        global sensitivity
        sensitivity = context.scene.view_rotation_sensitivity

    def plane_corta_objeto(plane_obj, target_obj, epsilon=1e-6):
        """
        Comprueba si 'plane_obj' (objeto plano) corta/interseca al 'target_obj' (objeto irregular).
        
        Retorna True si el plano divide al objeto (al menos un vértice a cada lado del plano),
        o False en caso contrario.
        
        Nota: Ambos objetos deben ser de tipo 'MESH'.
        """
        # Verificar que ambos objetos sean de malla
        if plane_obj.type != 'MESH' or target_obj.type != 'MESH':
            print("Ambos objetos deben ser de tipo MESH")
            return False

        # Obtener la malla del plano y asegurarse de que tenga caras
        plane_mesh = plane_obj.data
        if not plane_mesh.polygons:
            print("El objeto plano no tiene caras.")
            return False

        # Tomar la primera cara del plano para obtener la normal y un punto
        poly = plane_mesh.polygons[0]
        
        # Obtener la normal de la cara en coordenadas locales y transformarla a mundo
        local_normal = poly.normal.copy()
        world_normal = plane_obj.matrix_world.to_3x3() @ local_normal
        world_normal.normalize()
        
        # Tomar un vértice de la cara para usarlo como punto de referencia del plano
        vert_idx = poly.vertices[0]
        local_point = plane_mesh.vertices[vert_idx].co.copy()
        world_point = plane_obj.matrix_world @ local_point

        # Variables para detectar si hay vértices a ambos lados del plano
        tiene_positivo = False
        tiene_negativo = False

        # Obtener la malla del objeto irregular
        target_mesh = target_obj.data

        # Recorrer cada vértice del objeto irregular en coordenadas del mundo
        for vert in target_mesh.vertices:
            world_vert = target_obj.matrix_world @ vert.co
            # Calcular la distancia signada del vértice al plano
            d = (world_vert - world_point).dot(world_normal)
            if d > epsilon:
                tiene_positivo = True
            elif d < -epsilon:
                tiene_negativo = True

            # Si ya se detecta que hay vértices a ambos lados, se concluye que el plano corta al objeto
            if tiene_positivo and tiene_negativo:
                return True

        # Si todos los vértices están por un mismo lado (o exactamente sobre el plano), el plano no corta el objeto
        return False

    # Ejemplo de uso:
    # Asegúrate de tener un objeto llamado "Plane" y otro llamado "ObjetoIrregular" en la escena.
    # plane_obj = bpy.data.objects["Plane"]
    # target_obj = bpy.data.objects["ObjetoIrregular"]
    # resultado = plane_corta_objeto(plane_obj, target_obj)
    # print("El plano corta al objeto:", resultado)

    def obtener_objetos_en_coleccion(self, coleccion):
        """Obtiene todos los objetos de una colección, incluyendo los de sus subcolecciones."""
        objetos = list(coleccion.objects)  # Objetos directos de la colección
        for subcoleccion in coleccion.children:
            objetos.extend(self.obtener_objetos_en_coleccion(subcoleccion))  # Recursión para subcolecciones
        return objetos

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
        name="Area", default="", description="Introduce Area en metros cuadrados")
    
class INPUT_NUMBER_01(bpy.types.PropertyGroup):

    my_number_property_foam_block_x: bpy.props.FloatProperty(
        name="foam_block_x", default=1.410, description="Valor X para el bloque de Foam")
    
    my_number_property_foam_block_y: bpy.props.FloatProperty(
        name="foam_block_y", default=0.980, description="Valor Y para el bloque de Foam")
    
    my_number_property_foam_block_z: bpy.props.FloatProperty(
        name="foam_block_z", default=1.180, description="Valor Z para el bloque de Foam")
    
    my_number_property_wood_x: bpy.props.FloatProperty(
        name="wood_x", default=(0.042+0.008), description="Valor X para el bloque de Wood")
    
    my_number_property_wood_y: bpy.props.FloatProperty(
        name="wood_y", default=(0.141+0.008), description="Valor Y para el bloque de Wood")
    
    my_number_property_wood_z: bpy.props.FloatProperty(
        name="wood_z", default=4.347, description="Valor Z para el bloque de Wood")

    my_number_property_volume_total_irregular: bpy.props.FloatProperty(
        name="volume_total_irregular", default=0, description="Volumen total de la superficie irregular")
    
    my_number_property_volume_total_cubes: bpy.props.FloatProperty(
        name="volume_total_cubes", default=1, description="Valumen total de los bloques Foam")
    
    my_number_property_quantity_cubes: bpy.props.FloatProperty(
        name="quantity_cubes", default=0, description="Cantidad de bloques Foam usados aproximadamente")
    
    foam_weight: bpy.props.FloatProperty(
        name="foam weight", default=0, description="peso del plumavid")
    
    wood_weight: bpy.props.FloatProperty(
        name="foam weight", default=0, description="peso de la madera")
    
    fiber_weight: bpy.props.FloatProperty(
        name="foam weight", default=0, description="peso del fibra de vidrio")
    
    grass_weight: bpy.props.FloatProperty(
        name="foam weight", default=0, description="peso de la tierra")
    
    total_weight: bpy.props.FloatProperty(
        name="total weight", default=0, description="peso de la tierra")
    
    wood_lenght: bpy.props.FloatProperty(
        name="wood lenght", default=0, description="largo de la madera")
    
    foam_volume: bpy.props.FloatProperty(
        name="foam volume", default=0, description="volumen del plumavid")
    
    area_grass: bpy.props.FloatProperty(
        name="area grass", default=0, description="Area de la pasto")
    
    area_top: bpy.props.FloatProperty(
        name="area top", default=0, description="Area total 2d")
    
    obj_hight: bpy.props.FloatProperty(
        name="hight", default=0, description="Altura del modelo")
    
    submersion_depth: bpy.props.FloatProperty(
        name="submersion depth", default=0, description="Altura del modelo")
    
    
    
    density_foam: bpy.props.FloatProperty(
        name="density foam", default=30, description="Introduce Densidad en kg/m3")
    
    density_wood: bpy.props.FloatProperty(
        name="density wood", default=450, description="Introduce Densidad en kg/m3")
    
    density_grass: bpy.props.FloatProperty(
        name="density grass", default=1500, description="Introduce Densidad en kg/m3")
    
    density_fiber: bpy.props.FloatProperty(
        name="density fiber", default=1800, description="Introduce Densidad en kg/m3")
    
    hight_fiber: bpy.props.FloatProperty(
        name="hight fiber", default=5, description="Introduce espesor de la fibra con resina")
    
    hight_grass: bpy.props.FloatProperty(
        name="hight grass", default=10, description="Introduce espezor de la tierra")
    
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
    
class BUTTOM_GET_VOL(bpy.types.Operator):
    bl_label = "BUTTOM_GET_VOL"
    bl_idname = "object.button_get_vol"

    def execute(self, context):
        global func
        if func is None:
            func = funcs()
        func = funcs()
        
        #context.scene.my_text_settings.my_text_property_area = str(round(func.get_volume(context.active_object),2))
                
        total_height = context.active_object.dimensions.z
        wood = func.get_wood_weight(context)
        wood_weight = wood[0]
        wood_vol = wood[1]
        foam = func.get_foam_weight(context)
        foam_weight = foam[0]
        foam_vol = foam[1]
        fiber_weight = func.get_fiber_weight(context)
        grass = func.get_grass_weight(context)
        grass_weight = grass[0]
        grass_area = grass[1]
        wood_length = wood_vol / (func.wood_total_heigh * func.wood_total_width)
        total_weight = foam_weight + wood_weight + fiber_weight + grass_weight

        density_water = 1000 #kg/m3
        area_top = func.area_top

        submersion_depth = (total_weight/density_water)/(area_top)

        print(f"SUMERGIDO -- ({total_weight}/{density_water})/({area_top}) = {submersion_depth}")

        context.scene.my_number_settings.foam_weight = foam_weight
        context.scene.my_number_settings.wood_weight = wood_weight
        context.scene.my_number_settings.fiber_weight = fiber_weight
        context.scene.my_number_settings.grass_weight = grass_weight
        context.scene.my_number_settings.wood_lenght = wood_length
        context.scene.my_number_settings.foam_volume = foam_vol
        context.scene.my_number_settings.area_top = area_top
        context.scene.my_number_settings.area_grass = grass_area
        context.scene.my_number_settings.total_weight = total_weight
        context.scene.my_number_settings.obj_hight = total_height
        context.scene.my_number_settings.submersion_depth = submersion_depth




        print(f"Peso espuma: {(round(foam_weight,2))}\n")
        print(f"Peso madera: {(round(wood_weight,2))}\n")
        print(f"Peso fibra: {(round(fiber_weight,2))}\n")
        print(f"Peso tierra: {(round(grass_weight,2))}\n")
        print(f"Peso Total: {(round(total_weight,2))}\n")

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

        func.set_size_block(context, x_value, y_value, z_value)

        print(f"Valores introducidos: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados: X={func.foam_block_x}, Y={func.foam_block_y}, Z={func.foam_block_z}")
        return {'FINISHED'}
    
class BUTTOM_SET_WOOD_SIZE(bpy.types.Operator):
    bl_label = "BUTTOM_SET_WOOD_SIZE"
    bl_idname = "object.button_buttom_set_wood_size"
    bl_options = {'UNDO'}

    def execute(self, context):

        x_value = float(context.scene.my_text_settings.my_text_property_x)
        y_value = float(context.scene.my_text_settings.my_text_property_y)
        z_value = float(context.scene.my_text_settings.my_text_property_z)

        context.scene.my_number_settings.my_number_property_wood_x = x_value
        context.scene.my_number_settings.my_number_property_wood_y = y_value
        context.scene.my_number_settings.my_number_property_wood_z = z_value

        #func = myFunc
        func = funcs()

        func.set_size_wood(context, x_value, y_value, z_value)

        print(f"Valores introducidos wood: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados wood: X={func.wood_total_heigh}, Y={func.wood_total_width}, Z={func.wood_total_depth}")
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
        
        func.set_size_block(context, x_value, y_value, z_value)
        print(f"Valores introducidos foam: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados foam: X={func.foam_block_x}, Y={func.foam_block_y}, Z={func.foam_block_z}")
        return {'FINISHED'}

class BUTTOM_SET_WOOD_DEFAULT(bpy.types.Operator):
    bl_label = "BUTTOM_SET_WOOD_DEFAULT"
    bl_idname = "object.button_buttom_set_wood_default"
    bl_options = {'UNDO'}

    def execute(self, context):

        #func = myFunc
        func = funcs()
        
        x_value = round(func.wood_total_heigh, 2) 
        y_value = round(func.wood_total_width, 2) 
        z_value = round(func.wood_total_depth, 2)

        context.scene.my_number_settings.my_number_property_wood_x = x_value
        context.scene.my_number_settings.my_number_property_wood_y = y_value
        context.scene.my_number_settings.my_number_property_wood_z = z_value
    
        func.set_size_wood(context, x_value, y_value, z_value)

        print(f"Valores introducidos wood: X={x_value}, Y={y_value}, Z={z_value}")
        print(f"Valores Recuperados wood: X={func.wood_total_heigh}, Y={func.wood_total_width}, Z={func.wood_total_depth}")
        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_buttom_set_wood_default"

class BUTTOM_CUSTOM01(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM01_Prepare"
    bl_idname = "object.button_custom01"
    bl_options = {'UNDO'}

    def execute(self, context):
        #func = myFunc
        global func
        if func is None:
            func = funcs()
        

        x_value = context.scene.my_number_settings.my_number_property_foam_block_x
        y_value = context.scene.my_number_settings.my_number_property_foam_block_y
        z_value = context.scene.my_number_settings.my_number_property_foam_block_z

        print(f"Valores Recuperados BTN01: X={x_value}, Y={y_value}, Z={z_value}")
        func.crate_around_object(context)
        
        print("execute button01 ---custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom01"
    
class BUTTOM_CUSTOM02(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM02_Cut"
    bl_idname = "object.button_custom02"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        #func = myFunc
        global func
        if func is None:
            func = funcs()
        func.cut_and_order_parts(context)
        
        print("execute button02 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom02"
    
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
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom03"
    
class BUTTOM_CUSTOM04(bpy.types.Operator):
    bl_label = "Calibrate Cut in Z axis"
    bl_idname = "object.button_custom04"
    bl_options = {'REGISTER','UNDO'} #REGISTER popup a little window in the left down corner to introduce the parameters values

    update_value_bool : bpy.props.BoolProperty(
        name="update", 
        default=False, 
        options={'HIDDEN','SKIP_SAVE'}
        )
    
    def execute_updater(self, context):
        
        self.update_value_bool = True

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
        funcion.cut_silhouette(self.location_z,self.update_value_bool)
        #funcion.reorder_vertices(0)
        
        print("execute button04 custom ok!, Update:" + str(self.update_value_bool))

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom04"
    
class BUTTOM_CUSTOM05(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM05_CutFoam"
    bl_idname = "object.button_custom05"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.export_gcode_raw(context)

        print("execute button05 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom05"

#-----------------------------------------------------------

class BUTTOM_CUSTOM06(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM06_CutFoam"
    bl_idname = "object.button_custom06"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.block_base_top_part(context)
        func.isolate_part_collection(context)
        print("execute button06 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom06"  
    
class BUTTOM_CUSTOM0605(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM0605_CutFoam"
    bl_idname = "object.button_custom0605"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.block_base_top_part_finish(context)

        print("execute button0605 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom0605" 
    
class BUTTOM_CUSTOM07(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM07_CutFoam"
    bl_idname = "object.button_custom07"
    bl_options = {'UNDO'}

    global func

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.change_select_top_part(context,-1)
        print("execute button07 custom ok!")

        return {'FINISHED'} 
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom07"
    
class BUTTOM_CUSTOM0705(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM0705_CutFoam"
    bl_idname = "object.button_custom0705"
    bl_options = {'UNDO'}

    global func

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.change_select_top_part(context,0)
        func.create_cutter_plane(context)
        print("execute button07.05 custom ok!")

        return {'FINISHED'} 
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom07.05"

class BUTTOM_CUSTOM08(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM08_CutFoam"
    bl_idname = "object.button_custom08"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.change_select_top_part(context,1)

        print("execute button08 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom08"    

class BUTTOM_CUSTOM09(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM09_CutFoam"
    bl_idname = "object.button_custom09"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.rotate_top_part(context,0,180)

        print("execute button09 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom09"

class BUTTOM_CUSTOM10(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM10_CutFoam"
    bl_idname = "object.button_custom10"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.rotate_top_part(context,0,0)

        print("execute button10 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom10"

class BUTTOM_CUSTOM11(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM11_CutFoam"
    bl_idname = "object.button_custom11"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.rotate_top_part(context,2,180)

        print("execute button11 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom11"   

class BUTTOM_CUSTOM12(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM12_CutFoam"
    bl_idname = "object.button_custom12"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.rotate_top_part(context,2,0)

        print("execute button12 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom12"

class BUTTOM_CUSTOM13(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM13_CutFoam"
    bl_idname = "object.button_custom13"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.group_top_part(context)

        print("execute button13 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom13"

class BUTTOM_CUSTOM14(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM14_CutFoam"
    bl_idname = "object.button_custom14"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        global func
        if func is None:
            func = funcs()
        func.cut_and_group_parts(context)

        print("execute button14 custom ok!")

        return {'FINISHED'}
    @classmethod
    def description(cls, context, properties):
        return "object.button_custom14"

class RotateViewLeft(bpy.types.Operator):
    bl_idname = "view3d.rotate_view_left"
    bl_label = "Rotate View Left"

    def execute(self, context):
        # Rotar alrededor del eje Z (global) hacia la izquierda
        rotate_view(context, (0, 0, 1), 1)
        return {'FINISHED'}

class RotateViewRight(bpy.types.Operator):
    bl_idname = "view3d.rotate_view_right"
    bl_label = "Rotate View Right"

    def execute(self, context):
        # Rotar alrededor del eje Z (global) hacia la derecha
        rotate_view(context, (0, 0, 1), -1)
        return {'FINISHED'}

class RotateViewUp(bpy.types.Operator):
    bl_idname = "view3d.rotate_view_up"
    bl_label = "Rotate View Up"

    def execute(self, context):
        #check if the plane cut the irregular objects in the actual collection
        #bpy.ops.object.check_plane_cut()

        # Rotar alrededor del eje "derecho" de la vista (x-axis de la vista) hacia arriba
        region_3d = context.space_data.region_3d
        right_axis = region_3d.view_rotation @ mathutils.Vector((1, 0, 0))
        rotate_view(context, right_axis, 1)
        return {'FINISHED'}

class RotateViewDown(bpy.types.Operator):
    bl_idname = "view3d.rotate_view_down"
    bl_label = "Rotate View Down"

    def execute(self, context):
        # Rotar alrededor del eje "derecho" de la vista (x-axis de la vista) hacia abajo
        region_3d = context.space_data.region_3d
        right_axis = region_3d.view_rotation @ mathutils.Vector((1, 0, 0))
        rotate_view(context, right_axis, -1)
        return {'FINISHED'}

class OBJECT_OT_check_plane_cut(bpy.types.Operator):
    """Comprueba si el objeto 'Plane' corta alguno de los objetos en la colección 'P.130'"""
    bl_idname = "object.check_plane_cut"
    bl_label = "Verificar corte del plano"

    def execute(self, context):
        global func
        if func is None:
            func = funcs()
        
        plane_obj = bpy.data.objects.get(context.active_object.name)
        if not plane_obj:
            self.report({'ERROR'}, "No se encontró el objeto 'Plane'")
            return {'CANCELLED'}

        # Se obtiene la colección "P.130"
        collection = bpy.data.collections.get(context.active_object.users_collection[0].name)
        if not collection:
            self.report({'ERROR'}, "No se encontró la colección 'P.130'")
            return {'CANCELLED'}

        # Lista para acumular los nombres de objetos que son cortados por el plano
        cut_objects_list = []
        for obj in func.obtener_objetos_en_coleccion(collection):
            if obj.name.startswith("irregObjPart."):
                if func.plane_corta_objeto(plane_obj, obj):
                    cut_objects_list.append(obj.name)

        if cut_objects_list:
            cut_objects_str = "\n".join(cut_objects_list)
            # Invocar el diálogo de confirmación pasando la lista de objetos afectados
            bpy.ops.object.confirm_cut_dialog('INVOKE_DEFAULT', cut_objects=cut_objects_str)
        else:
            self.report({'INFO'}, "El plano no corta ningún objeto irregular.")
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

        # add text input for Area
        row = layout.row()
        row.prop(context.scene.my_text_settings, "my_text_property_area", text="Area")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "density_foam", text="Dens Foam kg/m3")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "density_wood", text="Dens Madera kg/m3")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "density_grass", text="Dens tierra kg/m3")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "density_fiber", text="Dens fibra kg/m3")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "hight_fiber", text="Esp fibra mm")

        row = layout.row()
        row.prop(context.scene.my_number_settings, "hight_grass", text="Esp Tierra cm")
        
        # add button custom
        row = layout.row()
        row.operator(BUTTOM_SET_AREA.bl_idname, text="Set Area")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_GET_AREA.bl_idname, text="Get Area")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_GET_VOL.bl_idname, text="Get Information")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"---INFO---")
                
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Altura: {round(context.scene.my_number_settings.obj_hight,2)} m")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Area Total 2D Top: {round(context.scene.my_number_settings.area_top,2)} m2")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Area Tierra: {round(context.scene.my_number_settings.area_grass,2)} m2")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Volumen Polietileno expandido: {round(context.scene.my_number_settings.foam_volume,2)} m3")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Peso Polietileno expandido: {round(context.scene.my_number_settings.foam_weight,2)} kg")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Peso madera : {round(context.scene.my_number_settings.wood_weight,2)} kg")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"metros de  madera : {round(context.scene.my_number_settings.wood_lenght,2)} m")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"Peso fibra de vidrio: {round(context.scene.my_number_settings.fiber_weight,2)} kg")
        
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Peso tierra: {round(context.scene.my_number_settings.grass_weight,2)} kg")
        
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Peso Total: {round(context.scene.my_number_settings.total_weight,2)} kg")
        
        #create simple row
        row02 = layout.row()
        row02.label(text = f"Sumergido ~: {round(context.scene.my_number_settings.submersion_depth,2)} m")

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

        foam_x = round(context.scene.my_number_settings.my_number_property_foam_block_x,2)
        foam_y = round(context.scene.my_number_settings.my_number_property_foam_block_y,2)
        foam_z = round(context.scene.my_number_settings.my_number_property_foam_block_z,2)

        wood_x = round(context.scene.my_number_settings.my_number_property_wood_x,2)
        wood_y = round(context.scene.my_number_settings.my_number_property_wood_y,2)
        wood_z = round(context.scene.my_number_settings.my_number_property_wood_z,2)

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
        row.label(text=f"X={foam_x}, Y={foam_y}, Z={foam_z}")
        row = layout.row()
        row.label(text=f"Wood Size + margin X Y (8mm recomended):")
        row = layout.row()
        row.label(text=f"X={wood_x}, Y={wood_y}, Z={wood_z}")

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
        row.operator(BUTTOM_SET_FOAM_SIZE.bl_idname, text="Set Size BLOCK")
        row.operator(BUTTOM_SET_WOOD_SIZE.bl_idname, text="Set Size WOOD")

        # add button custom
        row = layout.row()
        row.operator(BUTTOM_SET_FOAM_DEFAULT.bl_idname, text="Default Block")
        row.operator(BUTTOM_SET_WOOD_DEFAULT.bl_idname, text="Default Wood")

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
        row02.operator(BUTTOM_CUSTOM02.bl_idname, text= "Prepare Cuts in CNC Hot Wire", icon = "IMGDISPLAY")

        #create simple row
        row02 = layout.row()
        row02.label(text = f"---VOLUMENES---")

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
    bl_label = "TOP Parts"
    bl_idname = "OBJECT_PT_panel_03"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        #variables
        layout = self.layout
        if 'Top' in context.active_object and context.active_object.select_get():
            if context.active_object['Top'] == False:

                #create simple row
                row01 = layout.row()
                row01.label(text = "Select an object in the Top layer")

            elif context.active_object['Top'] == True:

                if 'top_object_block' in context.scene: 
                    actual_obj=context.scene['top_object_block'].name                     
                    actual_collection= context.scene['top_object_block'].users_collection[0].name
                else:
                    actual_obj=context.active_object.name
                    actual_collection= context.active_object.users_collection[0].name
                #create simple rows
                row01 = layout.row()
                row01.label(text = f"Part: {actual_collection}")
                row01 = layout.row()
                row01.label(text = f"Object : { actual_obj }")

                # add button custom
                row01 = layout.row()
                row01.scale_y = 2
                row01.operator("object.button_custom06", text= "Block TOP Object", icon = "UNLOCKED")

                #create simple row
                row02 = layout.row()
                row02.alert = True
                row02.label(text = f"Group Part: {context.active_object.users_collection[0].name}")
                row02 = layout.row()
                row02.label(text = f"Group Object: {context.active_object.name}") 

                if "top_object_block" in context.scene:
                    # add button custom
                    row02 = layout.row()
                    row02.scale_y = 2
                    row02.operator("object.button_custom07", text= "Before Part", icon = "BACK")

                    
                    row02.scale_y = 1
                    row02.operator("object.button_custom0705", text= "EXRA CUT")
                    # add button custom 
                    row02.scale_y = 2
                    row02.operator("object.button_custom08", text= "Next Part", icon = "FORWARD")
                
                    if context.scene['top_object_block'].name != context.active_object.name:

                        #create simple row
                        row02 = layout.row()
                        row02.label(text = f"Rotation Z: {context.active_object.location.z}")

                        # add button custom
                        row02 = layout.row()
                        row02.scale_y = 2
                        row02.operator("object.button_custom09", text= "R-X 180", icon = "LOOP_FORWARDS")

                        row02.scale_y = 2
                        row02.operator("object.button_custom10", text= "R-X 0", icon = "LOOP_BACK")

                        # add button custom
                        row02 = layout.row()
                        row02.scale_y = 2
                        row02.operator("object.button_custom11", text= "R-Z 180", icon = "LOOP_FORWARDS")

                        row02.scale_y = 2
                        row02.operator("object.button_custom12", text= "R-Z 0", icon = "LOOP_BACK")

                        # add button custom
                        row02 = layout.row()
                        row02.scale_y = 2
                        row02.prop(context.active_object, "location", text="Z Position", index=2)
            #else:
                        #create simple row
                        row02 = layout.row()
                        row02.label(text = "Fourth Step")
                    
                        # add button custom
                        row02 = layout.row()
                        row02.scale_y = 2
                        row02.operator("object.button_custom13", text= "Group")

                    #create simple row
                    row02 = layout.row()
                    row02.label(text = "FINISH Step")
                    
                    # add button custom
                    row02 = layout.row()
                    row02.scale_y = 1
                    row02.operator("object.button_custom0605", text= "FINISH")
            else:
                        #create simple row
                        row02 = layout.row()
                        row02.label(text = "Select a Top Part First")
        elif 'cutter' in context.active_object and context.active_object.select_get() and context.active_object['cutter'] == 'plane':

            #create simple row
            row02 = layout.row()
            row02.label(text = "Fifth Step")
        
            # add button custom
            row02 = layout.row()
            row02.scale_y = 2
            row02.operator("object.button_custom14", text= "Cut")

        layout.label(text="VISTA DE LA CAMARA")
        layout.prop(context.scene, "view_rotation_sensitivity", text="")

        # Botones de giro de vista
        row02 = layout.row()
        row02.operator("view3d.rotate_view_up", text="Rotate Up")
        
        row02 = layout.row(align=True)
        row02.operator("view3d.rotate_view_left", text="Rotate Left")
        row02.operator("view3d.rotate_view_right", text="Rotate Right")
        
        row02 = layout.row()
        row02.operator("view3d.rotate_view_down", text="Rotate Down") 

# DIALOGS UI (PART 2 DRAW)
####################################################

class OBJECT_OT_confirm_cut_dialog(bpy.types.Operator):
    """Diálogo de alerta: El plano corta los siguientes objetos. ¿Desea continuar?"""
    bl_idname = "object.confirm_cut_dialog"
    bl_label = "Alerta: Corte detectado"

    # Se pasará una cadena con los nombres de los objetos afectados
    cut_objects: bpy.props.StringProperty(name="Objetos cortados", default="")

    # Propiedad para elegir la acción
    action: bpy.props.EnumProperty(
        name="Acción",
        items=[
            ("CONTINUAR", "Continuar", "Continuar con la operación"),
            ("CANCELAR", "Cancelar", "Cancelar la operación")
        ],
        default="CANCELAR"
    )

    def execute(self, context):
        if self.action == "CONTINUAR":
            self.report({'INFO'}, "El usuario ha decidido continuar.")
            # Aquí puedes agregar el código que se deba ejecutar al continuar.
        else:
            self.report({'WARNING'}, "Operación cancelada por el usuario.")
            # Aquí puedes agregar código de limpieza o detener la ejecución.
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="El plano corta los siguientes objetos:")
        # Separamos los nombres para mostrarlos en líneas distintas
        for name in self.cut_objects.splitlines():
            layout.label(text=name)
        layout.separator()
        layout.label(text="¿Desea continuar?")
        layout.prop(self, "action", expand=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
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
    bpy.utils.register_class(BUTTOM_GET_VOL)
    bpy.utils.register_class(BUTTOM_SET_FOAM_SIZE)
    bpy.utils.register_class(BUTTOM_SET_WOOD_SIZE)
    bpy.utils.register_class(BUTTOM_SET_FOAM_DEFAULT)
    bpy.utils.register_class(BUTTOM_SET_WOOD_DEFAULT)
    bpy.utils.register_class(BUTTOM_CUSTOM01)
    bpy.utils.register_class(BUTTOM_CUSTOM02)
    bpy.utils.register_class(BUTTOM_CUSTOM03)
    bpy.utils.register_class(BUTTOM_CUSTOM04)
    bpy.utils.register_class(BUTTOM_CUSTOM05)
    bpy.utils.register_class(BUTTOM_CUSTOM06)
    bpy.utils.register_class(BUTTOM_CUSTOM0605)
    bpy.utils.register_class(BUTTOM_CUSTOM07)
    bpy.utils.register_class(BUTTOM_CUSTOM0705)
    bpy.utils.register_class(BUTTOM_CUSTOM08)
    bpy.utils.register_class(BUTTOM_CUSTOM09)
    bpy.utils.register_class(BUTTOM_CUSTOM10)
    bpy.utils.register_class(BUTTOM_CUSTOM11)
    bpy.utils.register_class(BUTTOM_CUSTOM12)
    bpy.utils.register_class(BUTTOM_CUSTOM13)
    bpy.utils.register_class(BUTTOM_CUSTOM14)
    bpy.utils.register_class(RotateViewLeft)
    bpy.utils.register_class(RotateViewRight)
    bpy.utils.register_class(RotateViewUp)
    bpy.utils.register_class(RotateViewDown)
    
    # Agregar propiedad de sensibilidad a la escena
    bpy.types.Scene.view_rotation_sensitivity = bpy.props.FloatProperty(
        name="Sensitivity",
        description="Adjust view rotation sensitivity (degrees)",
        default=15.0,
        min=1.0,
        max=90.0,
        update=update_sensitivity
    )

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
    bpy.utils.unregister_class(BUTTOM_GET_VOL)
    bpy.utils.unregister_class(BUTTOM_SET_FOAM_SIZE)
    bpy.utils.unregister_class(BUTTOM_SET_WOOD_SIZE)
    bpy.utils.unregister_class(BUTTOM_SET_FOAM_DEFAULT)
    bpy.utils.unregister_class(BUTTOM_SET_WOOD_DEFAULT)
    bpy.utils.unregister_class(BUTTOM_CUSTOM01)
    bpy.utils.unregister_class(BUTTOM_CUSTOM02)
    bpy.utils.unregister_class(BUTTOM_CUSTOM03)
    bpy.utils.unregister_class(BUTTOM_CUSTOM04)
    bpy.utils.unregister_class(BUTTOM_CUSTOM05)
    bpy.utils.unregister_class(BUTTOM_CUSTOM06)
    bpy.utils.unregister_class(BUTTOM_CUSTOM0605)
    bpy.utils.unregister_class(BUTTOM_CUSTOM07)
    bpy.utils.unregister_class(BUTTOM_CUSTOM0705)
    bpy.utils.unregister_class(BUTTOM_CUSTOM08)
    bpy.utils.unregister_class(BUTTOM_CUSTOM09)
    bpy.utils.unregister_class(BUTTOM_CUSTOM10)
    bpy.utils.unregister_class(BUTTOM_CUSTOM11)
    bpy.utils.unregister_class(BUTTOM_CUSTOM12)
    bpy.utils.unregister_class(BUTTOM_CUSTOM13)
    bpy.utils.unregister_class(BUTTOM_CUSTOM14)
    bpy.utils.register_class(RotateViewLeft)
    bpy.utils.register_class(RotateViewRight)
    bpy.utils.register_class(RotateViewUp)
    bpy.utils.register_class(RotateViewDown)
    
    # Agregar propiedad de sensibilidad a la escena
    del bpy.types.Scene.view_rotation_sensitivity

if __name__ == "__main__":
    register()
    #myFunc = funcs()
    

print("execute script OK!")