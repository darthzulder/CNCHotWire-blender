import bpy
import bmesh
import math
from mathutils import Vector
#from . import funcs
import os
dir = os.path.dirname(bpy.data.filepath)
print(f"------->{dir}")
#funcs = bpy.data.texts["funcs.py"].as_module()

#Funciones
class funcs():
    
    def change_origin (self):
        print(f"-------change_origin>{dir}")
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

    def create_block_greed (self, dimensions_X, dimensions_Y, dimensions_Z, foam_size_X = 1.410, foam_size_Y = 0.980, foam_size_Z = 1.180/2, separation = 0.02, scale = 1):
        print(f"-------create_block_greed>{dir}")
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
            array_modifier3.constant_offset_displace = (0.0, 0.0, separation*scale)  # Desplazamiento constante
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

    def create_cutter_planes (self, dimensions_X,dimensions_Y, dimensions_Z, separation_x = 1.43, separation_y = 1, separation_z = 1.180/2,  plane_thickness = 0.02, scale = 1):
        
        plane_size_high = (dimensions_Z+0.5)

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
        bpy.context.scene.cursor.location =(location_x,location_y,separation_z+plane_thickness/2)
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
        array_modifier_Z1.constant_offset_displace = (0.0, 0.0, separation_z+plane_thickness/2)  # Desplazamiento constante

        # Definir las propiedades del modificador
        array_modifier_Z2.offset = 0
        array_modifier_Z2.thickness = plane_thickness

    def crate_cnc_area (self, object_scope, scale = 1):
        print(f"-------crate_cnc_area>{dir}")
        
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

    def create_woods (self, dimensions_X,dimensions_Y, dimensions_Z, separation_x = 1.43, separation_y = 1, separation_z = 1.180/2,  plane_thickness = 0.02, scale = 1):

        plane_size_high = (separation_z+0.5)

        faces_count_x = math.ceil(dimensions_X/separation_x)
        faces_count_y = math.ceil(dimensions_Y/separation_y)

        dim_plane_x=math.ceil(dimensions_X/separation_x)*separation_x+1.5
        dim_plane_y=math.ceil(dimensions_Y/separation_y)*separation_y+2
            
        location_x = (dim_plane_x-1.5)/2
        location_y = (dim_plane_y-2)/2
        location_z = (plane_size_high-0.5)/2

        wood_heigh = 0.050
        wood_width = 0.152
        wood_depth = 4.347
        
        # -----create primitive Plane as cutterPlane --Cuts in X--
        # change cursor location
        bpy.context.scene.cursor.location =(separation_x/2,location_y,location_z)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterWood_X = bpy.context.object
        cutterWood_X.name = "innerWood_x.001"
        cutterWood_X.dimensions = (wood_width, dim_plane_y, wood_heigh)
        #cutterPlane_X.rotation_euler = (0,math.radians(90),0)
        bpy.ops.object.transform_apply(scale=True)

        # Agregar el modificador Array
        array_modifier_X1 = cutterWood_X.modifiers.new(name="Array_X", type='ARRAY')

        # Definir las propiedades del modificador
        array_modifier_X1.count = faces_count_x  # Número de repeticiones
        array_modifier_X1.relative_offset_displace = (1.0, 0.0, 0.0)  # Desplazamiento relativo
        array_modifier_X1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_X1.constant_offset_displace = ((separation_x-wood_width)*scale, 0.0, 0.0)  # Desplazamiento constante


        # -----create primitive Plane as cutterPlane --Cuts in Y--
        # change cursor location
        bpy.context.scene.cursor.location =(location_x,separation_y/2,location_z-wood_heigh)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterWood_Y = bpy.context.object
        cutterWood_Y.name = "innerWood_y.001"
        cutterWood_Y.dimensions = (dim_plane_x, wood_width, wood_heigh)
        #cutterPlane_Y.rotation_euler = (math.radians(90),0,0)
        bpy.ops.object.transform_apply(scale=True)

        # Agregar el modificador Array
        array_modifier_Y1 = cutterWood_Y.modifiers.new(name="Array_Y", type='ARRAY')

        # Definir las propiedades del modificador
        array_modifier_Y1.count = faces_count_y  # Número de repeticiones
        array_modifier_Y1.relative_offset_displace = (0.0, 1.0, 0.0)  # Desplazamiento relativo
        array_modifier_Y1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_Y1.constant_offset_displace = (0.0, (separation_y-wood_width)*scale, 0.0)  # Desplazamiento constante

    def crate_around_object (self, scale = 1):
        print(f"-------crate_around_object>{dir}")
        # store the location of current 3d cursor
        saved_location = bpy.context.scene.cursor.location.xyz   # returns a vector
        
        
        # get object
        selected_object = bpy.context.active_object
        # get object dimensions
        dimensions = selected_object.dimensions
        
        # get new origin coordinates
        dimensions_X = dimensions.x
        dimensions_Y = dimensions.y
        dimensions_Z = dimensions.z   

        self.create_cutter_planes(dimensions_X,dimensions_Y,dimensions_Z, scale = 1) 
        self.create_woods(dimensions_X,dimensions_Y,dimensions_Z, scale = 1)
       
        bpy.ops.object.select_all(action='DESELECT')              

        #-----Select the initial object
        selected_object.select_set(True)
        bpy.context.view_layer.objects.active = selected_object
        # change cursor location
        bpy.context.scene.cursor.location =(0,0,0)              
        # set 3dcursor location back to the stored location
        bpy.context.scene.cursor.location = saved_location
    
    def cut_object(self):
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

        self.create_block_greed(dimensions_X,dimensions_Y,dimensions_Z, scale = 1)

    def inner_part_verif(self):
        print('******inner_part_verif***********')
        #save state in case of error
        bpy.ops.ed.undo_push(message="inner_part_verif Function")
        try:
            collections_name = "Part"
            cubes_name = "foamBlock"
            object_selected_name = "irregObjPart"
            bpy.context.active_object.name = f"{object_selected_name}.001"
            #fix location in z to pass the inner verification, if z location is 0 may have conflict to check if is inside the cube due the cube Z location is 0
            if bpy.context.active_object.location.z == 0: bpy.context.active_object.location.z=+0.0001

            self.cut_object()
            # Get a list of all cube objects and irregular objects in the scene
            objects_cube      = [object for object in bpy.data.objects if object.name.startswith(f"{cubes_name}.")]
            objects_irregular = [object for object in bpy.data.objects if object.name.startswith(f"{object_selected_name}.")]
            
            # Dictionary to store the relationship between cube objects and irregular objects
            relation_cube_irregular = {}

                
            for object_cube in objects_cube:
                # # Get the world coordinates bounding-box-points of object_cube
                bbox_cube = [['%.2f' % elem for elem in object_cube.matrix_world @ Vector(coor)] for coor in object_cube.bound_box]
                have_something_inside = 0
                # Check if each irregular object is contained within any cube object
                for object_irregular in objects_irregular:
                    # Get the world coordinates of the bounding-box-points of object_irregular
                    bbox_irregular = [ ['%.2f' % elem for elem in object_irregular.matrix_world @ Vector(coor)] for coor in object_irregular.bound_box]

                    # # Check if the bounding box of the irregular object is contained within the bounding box of the cube object
                    is_inside = all(
                        bbox_cube[0][i] <= bbox_irregular[0][i] <= bbox_cube[6][i] and
                        bbox_cube[0][i] <= bbox_irregular[6][i] <= bbox_cube[6][i]
                        for i in range(3)
                    )                    
                                    
                    if is_inside:
                        relation_cube_irregular[object_irregular.name] = object_cube.name
                        have_something_inside = 1
                        for i in range (3):                        
                            print(f'c0|{i}:{bbox_cube[0][i]} <= i{i}|{i}:{bbox_irregular[i][i]} <= c6|{i}:{bbox_cube[6][i]}//c0|{i}:{bbox_cube[0][i]} <= i7|{i}:{bbox_irregular[7][i]} <= c6|{i}:{bbox_cube[6][i]}')
                        print('=========')
                        #break
                #Delete cube if don't have nothing inside            
                if have_something_inside == 0:
                    bpy.data.objects.remove(object_cube, do_unlink=True)

            for object_irregular, object_cube in (relation_cube_irregular.items()):
                #set objects                 
                object_irregular_obj = bpy.data.objects[object_irregular]
                object_cube_obj = bpy.data.objects[object_cube]   

                #lock modification but Z rotation
                object_irregular_obj.lock_rotation= (True, True, False)
                object_irregular_obj.lock_location = (True, True, True)
                object_irregular_obj.lock_scale = (True, True, True)
                object_cube_obj.lock_rotation= (True, True, False)
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
        except Exception as e:
            print("Error Custon Function, UNDO:", e)
            # UnDo in case of error
            bpy.ops.ed.undo()
    
    def draw_init(self):
        selected_object = bpy.context.active_object
        rX, rY, rZ = selected_object.rotation_euler
        print(selected_object.users_collection[0].name+'==>%.4f' % float(math.degrees(rZ)))

        loc_x, loc_y, loc_z = selected_object.location

        

        #create gpencil and put in drawing mode
        bpy.ops.object.gpencil_add(location=(loc_x, loc_y-selected_object.dimensions.y*1.5, loc_z), type='EMPTY')        
        

        #change to the actual collection
        gpencil_selected = bpy.context.active_object
        gpencil_coll=gpencil_selected.users_collection[0]
        print(gpencil_coll.name)        
        
        gpencil_coll.objects.unlink(gpencil_selected)
        selected_coll = selected_object.users_collection[0]
        selected_coll.objects.link(gpencil_selected)

        bpy.context.view_layer.objects.active = gpencil_selected
        bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
                

        #turn on the auto key
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        #change Viewport to Solid
        for area in bpy.data.screens[3].areas: 
            if area.type == 'VIEW_3D':
                for space in area.spaces: 
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        bpy.ops.view3d.view_axis(type='FRONT')

    def gpencil_to_mesh(self):
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
            print(f'*-*{gpencil_coll.name}')        
            
            gpencil_coll.objects.unlink(gpencil_selected)
            selected_coll.objects.link(gpencil_selected)  

            #-----Select the initial object
            foamcut_gpencil_curve.select_set(True)
            bpy.context.view_layer.objects.active = foamcut_gpencil_curve
            
            
            verts = foamcut_gpencil_curve.data.vertices

            #export to a *.nc file
            self.write_to_file(verts)

 

            #cut the foam with the actual object
            self.cut_foam()    

            #hide gpencil
            #foamcut_gpencil_curve.hide_select =  True
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False                

    def write_to_file(self,verts,rotation_z_degrees):
        scale=1000
        #create .nc file       
        f = open("e:\BLENDER.nc","w+")
        f.write(f'(BloqueXdesde_Blender)\nM9\nG21\nG90\nF600\nM3\nG00X0.0000Y0.0000A0\nG01X0.0000Y0.0000A0\nF600\n')
        #direction will be form +X  to -X 

        if verts[0].co.x < verts[len(verts)-1].co.x:
            middle_x = (verts[len(verts)-1].co.x + verts[0].co.x) / 2
            for i in reversed(range(0,len(verts))):
                distance_to_middle = verts[i].co.x - middle_x
                new_x = middle_x - distance_to_middle
                x=(new_x - verts[len(verts)-1].co.x) * scale
                y=verts[i].co.y * scale
                z=verts[i].co.z * scale
                coorX=str('%.4f' % x)
                coorY=str('%.4f' % y)
                coorZ=str('%.4f' % z)
                #write in .nc file
                f.write(f'G01X{coorX}Y{coorZ}A{rotation_z_degrees}\n')
        else:
            middle_x = (verts[len(verts)-1].co.x + verts[0].co.x) / 2
            for i in range(0,len(verts)):
                distance_to_middle = verts[i].co.x - middle_x
                new_x = middle_x - distance_to_middle
                x=(new_x - verts[len(verts)-1].co.x) * scale
                y=verts[i].co.y * scale
                z=verts[i].co.z * scale
                coorX=str('%.4f' % x)
                coorY=str('%.4f' % y)
                coorZ=str('%.4f' % z)
                #write in .nc file
                f.write(f'G01X{coorX}Y{coorZ}A{rotation_z_degrees}\n') 
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
        print(f'inivert-->{iniver}')
        vert = initial
        visited_verts = set()
        for i in range(len(bm.verts)):
            print(f'reorder--{vert.index, i}')
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

        #--create bool to cut the foamBlock with gpencil mesh
        #hide gpencil
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
        siluete_multires = 7

        margen_max_cnc=1.137
        margen_min_cnc=1.013

        # Get the selected object
        selected_object = bpy.context.active_object
        # Get the collee object
        object_collection = selected_object.users_collection[0]

        # Move the 3D cursor below the selected object by the CNC_margin amount
        loc_x, loc_y, loc_z = selected_object.location
        bpy.context.scene.cursor.location = (loc_x, loc_y - CNC_margin, 0)

        # Create a plane to serve as the cutter plane
        bpy.ops.mesh.primitive_plane_add(size=2)
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
        bpy.context.scene.cursor.location = (loc_x, loc_y, 0)

        # Create a second plane to serve as the silhouette cutter
        distance_to_plane=0.025
        bpy.ops.mesh.primitive_plane_add(size=2)
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
        plane_base.name = "cutterPlane.001"
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

        #----------------------Reorder vertices----------------------------
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
        # Extrude the minimum X vertex -2 in the X direction
        newvert = bm.verts.new((loc_x-margen_min_cnc, min_x_vertex.co.y, 0))
        newedge = bm.edges.new([min_x_vertex, newvert])
        indices_min=indices_in_z[1]+1
        # Extrude the maximum X vertex +2 in the X direction
        newvert = bm.verts.new((loc_x+margen_max_cnc, max_x_vertex.co.y, 0))
        newedge = bm.edges.new([max_x_vertex, newvert])
        indices_max=len(bm.verts)-1
           
        self.reorder_vertices(indices_max)

        # Update the bmesh and exit Edit Mode
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

    def cut_silhouette(self, loc_z):
        
        selected_silhouette = bpy.context.selected_objects[0]
        #get colection name
        collection_name = selected_silhouette.users_collection[0].name
        #get irregular object
        irregular_obj = [obj for obj in bpy.data.objects if obj.name.startswith("irregObjPart.") and collection_name in obj.users_collection[0].name]
        
        if irregular_obj:
            target_object = irregular_obj[0]
            rotation_euler = target_object.rotation_euler
            rotation_z_degrees = math.degrees(rotation_euler.z)
            print(f"Rotation in Z of {target_object.name}: {rotation_z_degrees} degrees")
        else:
            print("No related objects found in the same collection.")
                
        verts = selected_silhouette.data.vertices

        #export to a *.nc file
        self.write_to_file(verts,rotation_z_degrees)
        silhouette = bpy.context.object
        silhouette.location.z = loc_z
        silhouette.location.y = -1.5
        self.cut_foam()


# BUTTON CUSTOM (OPERATOR)
####################################################
class BUTTOM_CUSTOM01(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM01_Prepare"
    bl_idname = "object.button_custom01"
    bl_options = {'UNDO'}

    def execute(self, context):
        funcion = funcs()
        funcion.crate_around_object()
        
        print("execute button01 custom ok!")

        return {'FINISHED'}
    
class BUTTOM_CUSTOM02(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM02_Cut"
    bl_idname = "object.button_custom02"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.inner_part_verif()
        
        print("execute button02 custom ok!")

        return {'FINISHED'}
    
#----------------------------------------------------------    

class BUTTOM_CUSTOM03(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM03_CutFoam"
    bl_idname = "object.button_custom03"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.create_silhouette()
        
        print("execute button03 custom ok!")

        return {'FINISHED'}
    
class BUTTOM_CUSTOM04(bpy.types.Operator):
    bl_label = "Calibrate Cut in Z axis"
    bl_idname = "object.button_custom04"
    bl_options = {'REGISTER','UNDO'} #REGISTER popup a little window in the left down corner to introduce the parameters values

    location_z: bpy.props.FloatProperty(
        name="Z",
        description="location in the Z axis for the solhouette",
        default=-0.001,
        min=-0.009,
        soft_max=-0.0005,step=0.001,
    )

    def execute(self, context):
        
        funcion = funcs()
        funcion.cut_silhouette(self.location_z)
        #funcion.reorder_vertices(0)
        
        print("execute button04 custom ok!")

        return {'FINISHED'}
    
# PANEL UI (PART 1 DRAW)
####################################################

class PANEL_CUSTOM_UI_01(bpy.types.Panel):
    bl_label = "Prepare Irregular Model"
    bl_idname = "OBJECT_PT_panel_01"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"

    def draw(self, context):
        #variables
        layout = self.layout

        #create simple row
        row01 = layout.row()
        row01.label(text = "First Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom01", text= "Prepare Work Area", icon = "GRID")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Second Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom02", text= "Prepare Cuts in CNC Hot Wire", icon = "IMGDISPLAY")

class PANEL_CUSTOM_UI_02(bpy.types.Panel):
    bl_label = "CNC Hot-Wire"
    bl_idname = "OBJECT_PT_panel_02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"

    def draw(self, context):
        #variables
        layout = self.layout

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

# REGISTER (PART 2)
####################################################
def register():
    bpy.utils.register_class(PANEL_CUSTOM_UI_01)
    bpy.utils.register_class(PANEL_CUSTOM_UI_02)
    bpy.utils.register_class(BUTTOM_CUSTOM01)
    bpy.utils.register_class(BUTTOM_CUSTOM02)
    bpy.utils.register_class(BUTTOM_CUSTOM03)
    bpy.utils.register_class(BUTTOM_CUSTOM04)

def unregister():
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_01)
    bpy.utils.unregister_class(PANEL_CUSTOM_UI_02)
    bpy.utils.unregister_class(BUTTOM_CUSTOM01)
    bpy.utils.unregister_class(BUTTOM_CUSTOM02)
    bpy.utils.unregister_class(BUTTOM_CUSTOM03)
    bpy.utils.unregister_class(BUTTOM_CUSTOM04)

if __name__ == "__main__":
    register()
    

print("execute script OK!")