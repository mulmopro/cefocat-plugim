import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *

print('importing geometry')
bpy.ops.import_mesh.stl(filepath='./foamSTL.stl')

obj = C.scene.objects
foam = obj[0]

print('Origin to geometry\n')
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
foam.location = (0, 0, 0) 

mag0 = obj[0].dimensions.magnitude
print('diagonal magnitude = ',mag0)

print('separate into loose parts\n')
bpy.ops.mesh.separate(type='LOOSE')

bpy.ops.object.select_all(action='DESELECT')

for o in obj:
    o.select_set(True)
    if o.dimensions.magnitude < mag0*0.95:
        print('deleteting object', o.name,'with bounding diagonal=',o.dimensions.magnitude,'< ',mag0)
        bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')

if len(obj) == 1:
    bpy.ops.object.select_all(action='SELECT')

print('exporting geometry')
bpy.ops.export_mesh.stl(filepath="foamClean.stl", use_selection=True)
