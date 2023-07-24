import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import rcParams
from math import cos, sin
from shapely.ops import cascaded_union
from shapely import geometry
from matplotlib import patches

n=100
t = np.linspace(0, np.pi*2, n)
r = np.linspace(0, 1.0, n)

x = r * np.cos(t)
y = r * np.sin(t)

z = np.sin(-x*y)
fig = plt.figure()
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122, projection='3d')

polygons = list()
# Create a set of valid polygons spanning every combination of
# four xy pairs
for k in range(1, len(x)):
    for j in range(1, len(x)):
        try:
            polygons.append(geometry.Polygon([(x[k], y[k]), (x[k-1], y[k-1]), 
                                              (x[j], y[j]), (x[j-1], y[j-1])]))
        except (ValueError, Exception):
            pass

# Check for self intersection while building up the cascaded union
union = geometry.Polygon([])
for polygon in polygons:
    try:
        union = cascaded_union([polygon, union])
    except ValueError:
        pass

xp, yp = union.exterior.xy

ax1.plot_trisurf(x, y, z)
ax1.set_title(r"$z=sin(-x*y)$")
ax2.plot_trisurf(x, y, np.zeros_like(x))
ax2.set_title(r"$z=0$")
plt.show()   # Show surface and projection

fig, ax = plt.subplots(1, figsize=(8, 6))
ax.add_patch(patches.Polygon(np.stack([xp, yp], 1), alpha=0.6))
ax.plot(xp, yp, '-', linewidth=1.5)
plt.show()   # Show outline 