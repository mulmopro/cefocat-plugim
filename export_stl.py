import numpy as np
from skimage.measure import marching_cubes
from skimage.measure import mesh_surface_area
import trimesh 
from skimage import io

def binarize(im, threshold):
    boolean = im > threshold
    binarized = np.multiply(boolean, 1)
    return binarized

def surf(image):
    verts,faces,_,_ = marching_cubes(image,0)
    surface = mesh_surface_area(verts,faces)
    return surface, verts, faces

def export_stl(verts, trifaces,fileout):
    mesh = trimesh.Trimesh(vertices=verts, faces=trifaces)
    mesh_stl = mesh.export(fileout+'.stl')

def sv_calc(surface, voxsize, boxsize):
    vx_vol = voxsize ** 3
    vx_surf = voxsize ** 2
    spec_surf = ( surface * vx_surf )/ (vx_vol * boxsize ** 3 )
    return spec_surf

im = io.imread(filein)

im = np.logical_not(binarize(im, 254))

cutvx = 10
cut = im[cutvx:-cutvx, cutvx:-cutvx, cutvx:-cutvx]

pad = np.pad(im, 2, 'constant', constant_values=True)

