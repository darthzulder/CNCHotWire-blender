import bpy
def change_origin ():
    print("execute change_origin ok!")
    # Obtener el objeto seleccionado
    selected_object = bpy.context.active_object

    # Obtener las nuevas coordenadas del origen
    X = 0  # Valor de X deseado
    Y = 0  # Valor de Y deseado
    Z = 0  # Valor de Z deseado

    # Establecer las nuevas coordenadas del origen
    selected_object.location = (X, Y, Z)

def create_woods (self, dimensions_X,dimensions_Y, dimensions_Z, separation_x = 1.43, separation_y = 1, separation_z = 1.180/2,  plane_thickness = 0.02, scale = 1):

        plane_size_high = (dimensions_Z+0.5)

        faces_count_x = math.ceil(dimensions_X/separation_x)
        faces_count_y = math.ceil(dimensions_Y/separation_y)

        dim_plane_x=math.ceil(dimensions_X/separation_x)*separation_x+0.5
        dim_plane_y=math.ceil(dimensions_Y/separation_y)*separation_y+0.5
            
        location_x = (dim_plane_x-0.5)/2
        location_y = (dim_plane_y-0.5)/2
        location_z = (plane_size_high-0.5)/2

        wood_heigh = 0.050
        wood_width = 0.152
        wood_depth = 4.347
        
        # -----create primitive Plane as cutterPlane --Cuts in X--
        # change cursor location
        bpy.context.scene.cursor.location =(separation_x/2,location_y,location_z)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterPlane_X = bpy.context.object
        cutterPlane_X.name = "innerWood_x.001"
        cutterPlane_X.dimensions = (wood_width, dim_plane_y, wood_heigh)
        #cutterPlane_X.rotation_euler = (0,math.radians(90),0)
        bpy.ops.object.transform_apply(scale=True)

        # Agregar el modificador Array
        array_modifier_X1 = cutterPlane_X.modifiers.new(name="Array_X", type='ARRAY')

        # Definir las propiedades del modificador
        array_modifier_X1.count = faces_count_x  # Número de repeticiones
        array_modifier_X1.relative_offset_displace = (1.0, 0.0, 0.0)  # Desplazamiento relativo
        array_modifier_X1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_X1.constant_offset_displace = ((separation_x-wood_width)*scale, 0.0, 0.0)  # Desplazamiento constante


        # -----create primitive Plane as cutterPlane --Cuts in Y--
        # change cursor location
        bpy.context.scene.cursor.location =(location_x,separation_y/2,location_z-wood_heigh)
        bpy.ops.mesh.primitive_cube_add(size=scale)
        cutterPlane_Y = bpy.context.object
        cutterPlane_Y.name = "innerWood_y.001"
        cutterPlane_Y.dimensions = (dim_plane_x, wood_width, wood_heigh)
        #cutterPlane_Y.rotation_euler = (math.radians(90),0,0)
        bpy.ops.object.transform_apply(scale=True)

        # Agregar el modificador Array
        array_modifier_Y1 = cutterPlane_Y.modifiers.new(name="Array_Y", type='ARRAY')

        # Definir las propiedades del modificador
        array_modifier_Y1.count = faces_count_y  # Número de repeticiones
        array_modifier_Y1.relative_offset_displace = (0.0, 1.0, 0.0)  # Desplazamiento relativo
        array_modifier_Y1.use_constant_offset = True  # Usar desplazamiento constante
        array_modifier_Y1.constant_offset_displace = (0.0, (separation_y-wood_width)*scale, 0.0)  # Desplazamiento constante
