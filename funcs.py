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
    