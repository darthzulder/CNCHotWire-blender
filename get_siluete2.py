import bpy
import bmesh
import math

# Set CNC margin
CNC_margin = 2

# Get the selected object
selected_object = bpy.context.active_object

# Move the 3D cursor below the selected object by the CNC_margin amount
loc_x, loc_y, loc_z = selected_object.location
bpy.context.scene.cursor.location = (loc_x, loc_y - CNC_margin, 0)

# Create a plane to serve as the cutter plane
bpy.ops.mesh.primitive_plane_add(size=3)
siluete = bpy.context.object
siluete.name = "cutterPlane.001"
siluete.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(scale=True)
siluete.hide_select = True

# Add a Multiresolution modifier with 8 levels
Multires_01 = siluete.modifiers.new(name="Multires_01", type='MULTIRES')
for i in range(8):
    bpy.ops.object.multires_subdivide(modifier=Multires_01.name, mode='SIMPLE')

# Add a Subdivision Surface modifier with 'SIMPLE' subdivision type
#SubdivicionSurf_01 = siluete.modifiers.new(name="SubdivicionSurf_01", type='SUBSURF')
#SubdivicionSurf_01.subdivision_type = 'SIMPLE'

# Add a Shrinkwrap modifier to project the cutter plane onto the selected object
Srinkwrap_01 = siluete.modifiers.new(name="Srinkwrap_01", type='SHRINKWRAP')
Srinkwrap_01.target = selected_object
Srinkwrap_01.wrap_method = 'PROJECT'
Srinkwrap_01.wrap_mode = 'ON_SURFACE'
Srinkwrap_01.use_project_y = True
Srinkwrap_01.offset = -2

# Reset 3D cursor position
bpy.context.scene.cursor.location = (loc_x, loc_y, 0)

# Create a second plane to serve as the silhouette cutter
bpy.ops.mesh.primitive_plane_add(size=2)
cutter = bpy.context.object
cutter.name = "siluete.001"
cutter.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(scale=True)

# Add a Boolean modifier to intersect the silhouette cutter with the projected plane
Boolean_01 = cutter.modifiers.new(name="Boolean_01", type='BOOLEAN')
Boolean_01.operation = 'INTERSECT'
Boolean_01.solver = 'FAST'
Boolean_01.object = siluete

# Apply the Boolean modifier to create the silhouette
bpy.ops.object.modifier_apply(modifier=Boolean_01.name)

# Set the origin of the silhouette cutter to the center of mass
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

# Enter Edit Mode to reorder vertices
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# Get the mesh data and create a BMesh
me = bpy.context.object.data
bm = bmesh.from_edit_mesh(me)

# Dissolve vertices within a certain angle limit
bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5), verts=bm.verts)

# Reorder vertices
bm.verts.ensure_lookup_table()

# Index of the start vertex
initial = bm.verts[0]

vert = initial
prev = None
for i in range(len(bm.verts)):
    vert.index = i
    next = None
    adjacent = []
    for v in [e.other_vert(vert) for e in vert.link_edges]:
        if (v != prev and v != initial):
            next = v
    if next == None:
        break
    prev, vert = vert, next

# Sort vertices
bm.verts.sort()

# Update the mesh
bmesh.update_edit_mesh(me)

# Exit Edit Mode
bpy.ops.object.mode_set(mode='OBJECT')

# select object to scale
siluete = bpy.context.active_object

# scale to all axis
scale_factor = 1.1
siluete.scale[0] *= scale_factor
siluete.scale[1] *= scale_factor
siluete.scale[2] *= scale_factor

# Aplicar la escala al objeto
bpy.ops.object.transform_apply(scale=True)

# Create a plane to serve as the cutter plane
bpy.ops.mesh.primitive_plane_add(size=3)
plane_base = bpy.context.object
plane_base.name = "cutterPlane.001"
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.select_all(action='DESELECT')    
siluete.select_set(True)
bpy.context.view_layer.objects.active = siluete

# Add a Boolean modifier to intersect the silhouette cutter with the projected plane
Boolean_02 = siluete.modifiers.new(name="Boolean_02", type='BOOLEAN')
Boolean_02.solver = 'EXACT'
Boolean_02.object = plane_base

# Apply the Boolean modifier to create the silhouette
bpy.ops.object.modifier_apply(modifier=Boolean_02.name)


#---------------------------edit sluete------------------
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
newvert = bm.verts.new((8, max_x_vertex.co.y, 0))
newedge = bm.edges.new([max_x_vertex, newvert])

# Update the bmesh and exit Edit Mode
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')