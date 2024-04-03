import bpy
import bmesh
from mathutils import Vector

#constants
fine_object_name = 'Cube'
resolution = 100

# Get the fine object
fine_object = bpy.data.objects[fine_object_name]

# Calculate the bounding box dimensions
bbox_corners = [fine_object.matrix_world @ Vector(corner) for corner in fine_object.bound_box]
length = max(bbox_corners, key=lambda c: c.x).x - min(bbox_corners, key=lambda c: c.x).x
width = max(bbox_corners, key=lambda c: c.y).y - min(bbox_corners, key=lambda c: c.y).y
height = max(bbox_corners, key=lambda c: c.z).z - min(bbox_corners, key=lambda c: c.z).z

print(length, width, height)
#import pdb as p; p.set_trace()

# Determine the larger dimension and calculate the grid size
larger_dimension = max(length, width)
grid_size = larger_dimension / resolution

# Create a new grid object
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, size=larger_dimension)
grid_object = bpy.context.object

# Move the grid below the lowest vertex of the fine object
lowest_z = min(bbox_corners, key=lambda c: c.z).z
grid_object.location.z = lowest_z - 0.01  # Slightly below to avoid z-fighting

# Switch to edit mode
bpy.context.view_layer.objects.active = grid_object
bpy.ops.object.mode_set(mode='EDIT')

# Get the bmesh representation
bm = bmesh.from_edit_mesh(grid_object.data)

# Move each vertex of the grid up until it hits the fine object
for vert in bm.verts:
    # Start from the grid vertex position
    start_point = grid_object.matrix_world @ vert.co
    # End point is directly above the start point
    end_point = start_point + Vector((0, 0, height))
    
    # Cast a ray from the start point to the end point
    hit, location, normal, index = fine_object.ray_cast(start_point, end_point)
    
    # If the ray hits the fine object, move the vertex up
    if hit:
        # Convert the hit location to local space of the grid object
        local_hit = grid_object.matrix_world.inverted() @ location
        vert.co.z = local_hit.z

# Update the mesh
bmesh.update_edit_mesh(grid_object.data)

# Switch back to object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Print a success message
print("The grid has been created and vertices moved.")
