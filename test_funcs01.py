import bpy
import math
from mathutils import Vector

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

#create .nc file       
f = open("e:\BLENDER.nc","w+")
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

#change Viewport to Wireframe
for area in bpy.data.screens[3].areas: 
    if area.type == 'VIEW_3D':
        for space in area.spaces: 
            if space.type == 'VIEW_3D':
                space.shading.type = 'WIREFRAME'   


bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action = 'SELECT')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 3, 0)})
bpy.ops.object.mode_set(mode='OBJECT')        

#identify and choose collection union
gpencil_obj = bpy.context.active_object
gpencil_coll = gpencil_obj.users_collection[0]
col = bpy.data.collections[gpencil_coll.name]

#--create solidfy to cut the foamBlock with gpencil mesh
solidfy_modifier_Z = gpencil_obj.modifiers.new(name="solid_001", type='SOLIDIFY')
solidfy_modifier_Z.thickness = 0.0001
bpy.ops.object.modifier_apply(modifier=solidfy_modifier_Z.name)

# create a list requiring both objects selected and in chosen collection
objects_cube = [object for object in col.objects if object.name.startswith(f"foamBlock.")]        
objects_irreg = [object for object in col.objects if object.name.startswith(f"irregObjPart.")]

print('---'+objects_cube[0].name+'--------------------------------------------')

#--create bool to cut the foamBlock with gpencil mesh
gpencil_obj.select_set(False) # deselect to evade errors
bpy.context.view_layer.objects.active = objects_cube[0]
boolean_modifier_Z = objects_cube[0].modifiers.new(name="Cut_foam_001", type='BOOLEAN')
boolean_modifier_Z.solver = 'EXACT'
boolean_modifier_Z.object = gpencil_obj
bpy.ops.object.modifier_apply(modifier=boolean_modifier_Z.name)

# ------------------Separate by loose parts-------------------------
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action = 'SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT') 

#rest Z rotation to get real bound_box coord
rotation_irregObj = objects_irreg[0].rotation_euler
#objects_irreg[0].rotation_euler.z = math.radians(0)
# Get divided parts

# create a list requiring both objects
objects_cubes = [object for object in col.objects if object.name.startswith(f"foamBlock.")]

#print(objects_irreg)
adjust_value = 0.01
for object_cube in objects_cubes:
        # # Get the world coordinates bounding-box-points of object_cube
        bbox_cube = [[float(math.ceil(elem * 100) / 100)  for elem in object_cube.matrix_world @ Vector(coor)] for coor in object_cube.bound_box]
        have_something_inside = 0
        print(f'Coordenadas de {object_cube.name}: {bbox_cube}')
        # Check if each irregular object is contained within any cube object
        for object_irregular in objects_irreg:
            object_irregular.rotation_euler.z = math.radians(0)
            object_cube.rotation_euler.z = math.radians(0)
            # Get the world coordinates of the bounding-box-points of object_irregular
            bbox_irregular = [ [float(math.ceil(elem * 100) / 100) for elem in object_irregular.matrix_world @ Vector(coor)] for coor in object_irregular.bound_box]
            bpy.ops.object.select_all(action='DESELECT')
            object_cube.select_set(True)
            # # Check if the bounding box of the irregular object is contained within the bounding box of the cube object
            #bpy.ops.object.transform_apply(rotation=True)
            is_inside = all(
                (bbox_cube[0][i]-adjust_value) <= bbox_irregular[0][i] <= (bbox_cube[6][i]+adjust_value) and
                (bbox_cube[0][i]-adjust_value) <= bbox_irregular[6][i] <= (bbox_cube[6][i]+adjust_value)
                for i in range(3)
            )
                            
            if is_inside:
                have_something_inside = 1
            
            for i in range(3):
                print(f'R: {object_cube.rotation_euler.z} dentro?: {have_something_inside} | {bbox_cube[0][i]-adjust_value} <= {bbox_irregular[0][i]} <= {bbox_cube[6][i]+adjust_value} and {bbox_cube[0][i]-adjust_value} <= {bbox_irregular[6][i]} <= {bbox_cube[6][i]+adjust_value}')
            bpy.ops.object.select_all(action='DESELECT')

        #Delete cube if don't have nothing inside            
        #if have_something_inside == 0:
        #    bpy.data.objects.remove(object_cube, do_unlink=True)


#objects_irreg[0].rotation_euler.z = float(rotation_irregObj)