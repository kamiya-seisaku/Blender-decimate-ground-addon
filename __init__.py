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

def decimate_ground_faces(context, subdivisions, depth_percent, duplicate):
    # Get the active object
    obj = context.active_object

    # Duplicate the object if the duplicate option is True
    if duplicate:
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        obj = context.active_object  # Update obj to the new duplicate

    # Store the current active object name
    original_obj_name = obj.name

    # Switch to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add a plane to use as the ground mesh
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False)
    ground = context.active_object
    ground.name = original_obj_name + "_ground"

    # Subdivide the ground mesh based on the subdivisions parameter
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions - 1)

    # Move the ground mesh below the lowest vertex of the high-poly object
    lowest_vertex_z = min(v.co.z for v in obj.data.vertices)
    ground.location.z = lowest_vertex_z - 0.01  # Slightly below the lowest vertex

    # Calculate the height of the high-poly object
    highest_vertex_z = max(v.co.z for v in obj.data.vertices)
    obj_height = highest_vertex_z - lowest_vertex_z

    # Calculate the depth for deletion based on the percentage
    deletion_depth = obj_height * (depth_percent / 100.0)

    # Move the vertices of the ground mesh up to just below the high-poly object
    bpy.ops.object.mode_set(mode='OBJECT')
    for vertex in ground.data.vertices:
        # Cast a ray upwards to find the intersection point with the high-poly object
        hit, location, normal, index = ground.ray_cast(vertex.co + ground.location, (0, 0, 1), distance=obj_height)
        if hit:
            # Move the vertex up but keep it below the high-poly object by the deletion depth
            vertex.co.z = location.z - deletion_depth - ground.location.z

    # Select the original high-poly object
    bpy.data.objects[original_obj_name].select_set(True)
    context.view_layer.objects.active = bpy.data.objects[original_obj_name]

    # Delete faces of the high-poly object that are within the deletion depth
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for poly in obj.data.polygons:
        if poly.center.z < (lowest_vertex_z + deletion_depth):
            poly.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

class OBJECT_OT_decimate_ground(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.decimateground"
    bl_label = "Decimate Ground"

    obj_name = bpy.props.StringProperty()
    subdivisions = bpy.props.IntProperty(name="Subdivisions", default=100)
    depth = bpy.props.FloatProperty(name="Depth", default=3.0)
    duplicate = bpy.props.BoolProperty(name="Duplicate", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # Find the object by name
        obj = context.scene.objects.get(self.obj_name)
        if obj is None:
            self.report({'ERROR'}, f"Object '{self.obj_name}' not found")
            return {'CANCELLED'}
        context.view_layer.objects.active = obj
        decimate_ground_faces(context, self.subdivisions, self.depth, self.duplicate)
        return {'FINISHED'}
    
class OBJECT_PT_custom_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Decimate Object Ground"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DecimateGround'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        col.prop_search(scene, "my_obj", scene, "objects", text="Target Object")

        col = layout.column()
        col.prop(scene, "subdivisions", text="Ground Mesh Subdivisions")

        col = layout.column()
        col.prop(scene, "depth", text="Mesh Deletion Depth (%)")

        col = layout.column()
        col.prop(scene, "duplicate", text="Duplicate Original Mesh")

        col = layout.column()
        # Pass the selected object name to the operator
        op = col.operator("object.decimateground", text="Run")
        op.obj_name = scene.my_obj

def register():
    bpy.utils.register_class(OBJECT_OT_decimate_ground)
    bpy.utils.register_class(OBJECT_PT_custom_panel)
    bpy.types.Scene.my_obj = bpy.props.StringProperty()
    bpy.types.Scene.subdivisions = bpy.props.IntProperty(name="Subdivisions", default=100)
    bpy.types.Scene.depth = bpy.props.FloatProperty(name="Depth", default=3.0)
    bpy.types.Scene.duplicate = bpy.props.BoolProperty(name="Duplicate", default=False)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_decimate_ground)
    bpy.utils.unregister_class(OBJECT_PT_custom_panel)
    del bpy.types.Scene.my_obj
    del bpy.types.Scene.subdivisions
    del bpy.types.Scene.depth
    del bpy.types.Scene.duplicate

if __name__ == "__main__":
    register()
