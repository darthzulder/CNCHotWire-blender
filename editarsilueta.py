import bpy
import bmesh

# Select the plane object
obj = bpy.context.active_object

# Make sure you're in Edit Mode
bpy.ops.object.mode_set(mode='EDIT')
# Change back to Vertex selection mode
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action = 'DESELECT')

# Create a new bmesh from the mesh data
bm = bmesh.from_edit_mesh(obj.data)

# Deselect all vertices
for v in bm.verts:
    v.select = False

# Find the lowest Z coordinate among all vertices
lowest_z = min(v.co.z for v in bm.verts)


indices = []

# Select the vertices that have the lowest Z coordinate
lowest_z_vertices = [v for v in bm.verts if v.co.z == lowest_z]
for v in lowest_z_vertices:
    v.select = True
    indices.append(v.index)

# Find the vertex with the minimum X coordinate among the selected vertices
min_x_vertex = min(lowest_z_vertices, key=lambda v: v.co.x)

# Find the vertex with the maximum X coordinate among the selected vertices
max_x_vertex = max(lowest_z_vertices, key=lambda v: v.co.x)

for e in bm.edges:
    if e.verts[0].index in indices and e.verts[1].index in indices:
        e.select = True
        break

# Change to Edge selection mode
bpy.ops.mesh.select_mode(type="EDGE")

# Elimina los bordes seleccionados
bpy.ops.mesh.delete(type='EDGE')

# Change back to Vertex selection mode
bpy.ops.mesh.select_mode(type="VERT")

# Extrude the minimum X vertex -2 in the X direction
#min_x_vertex.co.x -= 0.2
newvert = bm.verts.new((4, min_x_vertex.co.y, 0))
newedge = bm.edges.new([min_x_vertex, newvert])

# Extrude the maximum X vertex +2 in the X direction
#max_x_vertex.co.x += 0.2
newvert = bm.verts.new((8, max_x_vertex.co.y, 00))
newedge = bm.edges.new([max_x_vertex, newvert])

# Update the bmesh and exit Edit Mode
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
