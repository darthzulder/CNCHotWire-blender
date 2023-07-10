import bpy
import math
from mathutils import Vector

foamcoll = bpy.data.collections['Collection.001']
objects_cubes = [object for object in foamcoll.objects if object.name.startswith(f"foamBlock.")]
for object_cube in objects_cubes:
    # # Get the world coordinates bounding-box-points of object_cube
    bbox_cube = [[float(math.ceil(elem * 100) / 100)  for elem in object_cube.matrix_world @ Vector(coor)] for coor in object_cube.bound_box]
    print(f'--Coordenadas de {object_cube.name}: {bbox_cube}')                    
