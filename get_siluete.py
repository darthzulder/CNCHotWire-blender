import bpy
import bmesh
import math

bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

me = bpy.context.object.data
bm = bmesh.from_edit_mesh(me)

bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5), verts=bm.verts)

bm.verts.ensure_lookup_table()

bm = bmesh.from_edit_mesh(me)
# index of the start vertex
initial = bm.verts[0]

vert = initial
prev = None
for i in range(len(bm.verts)):
    print(vert.index, i)
    vert.index = i
    next = None
    adjacent = []
    for v in [e.other_vert(vert) for e in vert.link_edges]:
        if (v != prev and v != initial):
            next = v
    if next == None: break
    prev, vert = vert, next

bm.verts.sort()

bmesh.update_edit_mesh(me)

bpy.ops.object.mode_set(mode='OBJECT')