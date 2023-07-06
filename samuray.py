import bpy
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

        
        # ------------------Separar por partes sueltas-------------------------
        bpy.ops.mesh.separate(type='LOOSE')

        # Obtener las partes separadas
        foamBlocks = bpy.context.selected_objects

        # Crear una nueva colección llamada "Blocks"
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

        # Obtener las partes separadas
        objectBlocks = bpy.context.selected_objects

        # Crear una nueva colección llamada "Blocks"
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
                        bbox_cube[0][i] <= bbox_irregular[i][i] <= bbox_cube[6][i] and
                        bbox_cube[0][i] <= bbox_irregular[7][i] <= bbox_cube[6][i]
                        for i in range(3)
                    )
                                    
                    if is_inside:
                        relation_cube_irregular[object_irregular.name] = object_cube.name
                        have_something_inside = 1
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
                    object_cube_obj.display_type = 'WIRE'

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

            foamcut_gpencil = bpy.context.selected_objects[0]
            foamcut_gpencil.name = "foamCut.001"  

            #change to the actual collection
            bpy.context.view_layer.objects.active = foamcut_gpencil
            gpencil_selected = bpy.context.active_object
            gpencil_coll=gpencil_selected.users_collection[0]
            #print(gpencil_coll.name)        
            
            gpencil_coll.objects.unlink(gpencil_selected)
            selected_coll = greacePencil.users_collection[0]
            selected_coll.objects.link(gpencil_selected)  

            #delete original gpencil curve
            bpy.data.objects.remove(greacePencil, do_unlink=True)            

            #-----Select the initial object
            foamcut_gpencil.select_set(True)
            bpy.context.view_layer.objects.active = foamcut_gpencil

            verts=foamcut_gpencil.data.vertices
            #create .nc file       
            f= open("e:\BLENDER.nc","w+")
            #direction will be form +X  to -X 
            if verts[0].co.x < verts[len(verts)-1].co.x:
                for i in reversed(range(0,len(verts))):
                    coorX=str('%.4f' % verts[i].co.x)
                    coorY=str('%.4f' % verts[i].co.y)
                    coorZ=str('%.4f' % verts[i].co.z)
                    #write in .nc file
                    f.write(f'G01X{coorX}Y{coorZ}A{coorY}\n')
            else:
                for i in range(0,len(verts)):
                    coorX=str('%.4f' % verts[i].co.x)
                    coorY=str('%.4f' % verts[i].co.y)
                    coorZ=str('%.4f' % verts[i].co.z)
                    #write in .nc file
                    f.write(f'G01X{coorX}Y{coorZ}A{coorY}\n')
                    
            #cut the foam with the actual object
            self.cut_foam()

            foamcut_gpencil.hide_select =  True
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False        

            #change Viewport to Wireframe
            for area in bpy.data.screens[3].areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces: 
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'WIREFRAME'

    def cut_foam(self):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 3, 0)})

        '''#--create bool to cut the foamBlock with gpencil mesh
        #print(selected_object.users_collection[0].name+'==>%.4f' % float(math.degrees(rZ)))
        for child in selected_object.children:
            if child.type != 'MESH':
                continue
            selected_object = bpy.context.object
            boolean_modifier_Z = child.modifiers.new(name="Cut_foam_001", type='BOOLEAN')
            boolean_modifier_Z.solver = 'EXACT'
            boolean_modifier_Z.object = foamcut_gpencil
            objects_cube      = [object for object in bpy.data.objects if object.name.startswith(f"{cubes_name}.")]
        #bpy.ops.object.modifier_apply(modifier=boolean_modifier_Z.name)'''

        

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
    
class BUTTOM_CUSTOM03(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM03_CutFoam"
    bl_idname = "object.button_custom03"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.draw_init()
        
        print("execute button03 custom ok!")

        return {'FINISHED'}
    
class BUTTOM_CUSTOM04(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM04_CutFoam"
    bl_idname = "object.button_custom04"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        funcion = funcs()
        funcion.gpencil_to_mesh()
        
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
        row01.operator("object.button_custom01", text= "Prepare Work Area", icon = "MODIFIER_ON")

        #create simple row
        row02 = layout.row()
        row02.label(text = "Second Step")

        # add button custom
        row02 = layout.row()
        row02.scale_y = 2
        row02.operator("object.button_custom02", text= "Prepare Cuts in CNC Hot Wire", icon = "MODIFIER_ON")

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
        row01.operator("object.button_custom03", text= "Create Gpencil", icon = "MODIFIER_ON")

        #create simple row
        row01 = layout.row()
        row01.label(text = "Second Step")

        # add button custom
        row01 = layout.row()
        row01.scale_y = 2
        row01.operator("object.button_custom04", text= "Gpencil to code", icon = "MODIFIER_ON")

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