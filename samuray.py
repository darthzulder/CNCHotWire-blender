import bpy
#from . import funcs
import os
dir = os.path.dirname(bpy.data.filepath)
print(f"------->{dir}")
#funcs = bpy.data.texts["funcs.py"].as_module()

#Funciones
class funcs():
    
    def change_origin ():
        
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
        
        # set origin new coordinates 
        # selected_object.location = (location_X, location_Y, location_Z)
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

# BUTTON CUSTOM (OPERATOR)
####################################################
class BUTTOM_CUSTOM(bpy.types.Operator):
    bl_label = "BUTTOM_CUSTOM"
    bl_idname = "object.button_custom"

    def execute(self, context):

        funcs.change_origin()
        
        print("execute button custom ok!")

        return {'FINISHED'}
    
# PANEL UI (PART 1 DRAW)
####################################################

class PANEL_CUSTOM_UI(bpy.types.Panel):
    bl_label = "CNC Hot-Wire"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Panel Custom UI"

    def draw(self, context):
        #variables
        layout = self.layout

        #create simple row
        row = layout.row()
        row.label(text = "Titulo Fila")

        # add button custom
        row = layout.row()
        row.scale_y = 2
        row.operator("object.button_custom", text= "Get set \n(Samuray)", icon = "HEART")

# REGISTER (PART 2)
####################################################
def register():
    bpy.utils.register_class(PANEL_CUSTOM_UI)
    bpy.utils.register_class(BUTTOM_CUSTOM)

def unregister():
    bpy.utils.unregister_class(PANEL_CUSTOM_UI)
    bpy.utils.unregister_class(BUTTOM_CUSTOM)

if __name__ == "__main__":
    register()
    

print("execute script OK!")