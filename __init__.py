# ADD-ON
####################################################

bl_info = {
    "name": "CNC HotWire Preparetion",
    "description": "Change origin Position ",
    "author": "nbravo",
    "version": (1, 0),
    "blender": (2, 93, 1),
    "location": "View3D > UI",
    "warning":"(in ALFA production)",
    "doc_url":"",
    "category": "User"
}
print("----------Instalado-----------")
import bpy
from . import funcs
from .state import GlobalState, register as register_state
#funcs = bpy.data.texts["funcs.py"].as_module()

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
        row.label(text = "ROW")

        # add button custom
        row = layout.row()
        row.scale_y = 2
        row.operator("object.button_custom", text= "Get set", icon = "HEART")

# REGISTER (PART 2)
####################################################
def register():
    register_state()
    bpy.utils.register_class(PANEL_CUSTOM_UI)
    bpy.utils.register_class(BUTTOM_CUSTOM)

def unregister():
    bpy.utils.unregister_class(PANEL_CUSTOM_UI)
    bpy.utils.unregister_class(BUTTOM_CUSTOM)

if __name__ == "__main__":
    register()