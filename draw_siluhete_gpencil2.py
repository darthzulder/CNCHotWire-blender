import bpy
from mathutils import Vector

def create_grease_pencil_stroke(points):
    gp_data = bpy.data.grease_pencils.new("MyGreasePencil")
    gp_obj = bpy.data.objects.new("MyGreasePencil", gp_data)
    bpy.context.scene.collection.objects.link(gp_obj)
    bpy.context.view_layer.objects.active = gp_obj
    gp_obj.select_set(True)

    gp_layer = gp_data.layers.new(name="Layer 1")
    gp_frame = gp_layer.frames.new(frame_number=1)

    gp_stroke = gp_frame.strokes.new()
    gp_stroke.points.add(count=len(points))

    for i, point in enumerate(points):
        gp_stroke.points[i].co = point

    bpy.context.view_layer.update()

def project_points_on_surface(obj, num_points):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]

    if not verts:
        return []

    x_min = min(v.x for v in verts)
    x_max = max(v.x for v in verts)
    x_range = x_max - x_min

    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        x_target = x_min + t * x_range

        projected_points = []
        for v1, v2 in zip(verts, verts[1:]):
            if v1.x == v2.x:
                continue

            if (v1.x <= x_target <= v2.x) or (v2.x <= x_target <= v1.x):
                t = (x_target - v1.x) / (v2.x - v1.x)
                z = v1.z + t * (v2.z - v1.z)
                projected_points.append(Vector((x_target, 0, z)))

        points.extend(projected_points)

    return points

# Get the selected 3D object
obj = bpy.context.active_object

# Check if the object is a mesh
if obj and obj.type == 'MESH':
    # Number of points for the line
    num_points = 50

    # Get points projected on the surface of the object
    surface_points = project_points_on_surface(obj, num_points)

    # Create Grease Pencil stroke
    create_grease_pencil_stroke(surface_points)
else:
    print("Please select a 3D object with mesh data.")
