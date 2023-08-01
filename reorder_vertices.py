import bpy
import bmesh

#must be in EDIT mode
me = bpy.context.object.data
bm = bmesh.from_edit_mesh(me)

# index of the start vertex SELECT the specific vertex
initial = bm.verts[iniver]

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