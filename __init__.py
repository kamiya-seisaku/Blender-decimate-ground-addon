bl_info = {
    "name": "Decimate Ground Faces",
    "author": "kamiya seisaku",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > N panel > Decimate Tab",
    "description": "Decimates an object using a grid method",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

def main(context, operator, obj_name):
    # This is where you would call your decimation function
    # For now, it just prints the name of the selected object
    print("Decimating Ground Faces:", obj_name)

class OBJECT_OT_decimate(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.decimate"
    bl_label = "Decimate Object"

    obj_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context, self, self.obj_name)
        return {'FINISHED'}

class OBJECT_PT_custom_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Decimate Object"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Decimate'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.prop_search(context.scene, "my_obj", context.scene, "objects")

        col = layout.column()
        col.operator("object.decimate", text="Run")

def register():
    bpy.utils.register_class(OBJECT_OT_decimate)
    bpy.utils.register_class(OBJECT_PT_custom_panel)
    bpy.types.Scene.my_obj = bpy.props.StringProperty()

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_decimate)
    bpy.utils.unregister_class(OBJECT_PT_custom_panel)
    del bpy.types.Scene.my_obj

if __name__ == "__main__":
    register()