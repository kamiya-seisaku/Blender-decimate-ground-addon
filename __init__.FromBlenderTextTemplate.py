import bpy
from bpy.props import StringProperty
import pdb

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

#    fine_obj_name: StringProperty(
#        name="Fine object name",
#        size=3,
#    )

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

class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Layout Demo"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        layout.label(text="Big Button key:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.decimateground")
        row.operator.fine_obj_name = "Suzanne"

def register():
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(OBJECT_OT_decimate_ground)


def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(OBJECT_OT_decimate_ground)


if __name__ == "__main__":
    register()
