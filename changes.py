import bpy

def decimate_ground_faces(context, subdivisions, depth_percent, duplicate):
    # Get the active object
    obj = context.active_object

    # Duplicate the object if the duplicate option is True
    if duplicate:
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        obj = context.active_object  # Update obj to the new duplicate

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Add a plane to use as the ground mesh
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False)
    ground = context.active_object

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
        hit, location, _, _, _, _ = ground.ray_cast(vertex.co, (0, 0, 1), distance=obj_height)
        if hit:
            # Move the vertex up but keep it below the high-poly object by the deletion depth
            vertex.co.z = location.z - deletion_depth

    # Delete faces of the high-poly object that are within the deletion depth
    bpy.context.view_layer.objects.active = obj
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

# Update the main function to call the decimation function with the correct parameters
def main(context, operator, obj_name, subdivisions, depth, duplicate):
    # Find the object by name
    obj = context.scene.objects.get(obj_name)
    if obj is None:
        operator.report({'ERROR'}, f"Object '{obj_name}' not found")
        return
    context.view_layer.objects.active = obj
    decimate_ground_faces(context, subdivisions, depth, duplicate)
