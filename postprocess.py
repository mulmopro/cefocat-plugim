import numpy as np
from skimage import io
import os
from skimage.measure import marching_cubes
from skimage.measure import mesh_surface_area
import tifffile as tif

def surf(image):
    verts,faces,_,_ = marching_cubes(image,0)
    surface = mesh_surface_area(verts,faces)
    return surface, verts, faces

def sv_calc(surface, voxsize, boxsize):
    vx_vol = voxsize ** 3
    vx_surf = voxsize ** 2
    spec_surf = ( surface * vx_surf )/ (vx_vol * boxsize ** 3 )
    return spec_surf

def export_stl(verts, trifaces,filename):
    mesh = trimesh.Trimesh(vertices=verts, faces=trifaces)
    mesh_stl = mesh.export(filename+'.stl')

def binarize(im, threshold):
    boolean = im > threshold
    binarized = np.multiply(boolean, 1)
    return binarized

def por(mat):
    por = 1 - mat.mean()
    return por

def sv_calc_uneven(surface, voxsize, boxsize):
    vx_vol = voxsize ** 3
    vx_surf = voxsize ** 2
    spec_surf = ( surface * vx_surf )/ (vx_vol * np.prod(boxsize) )
    return spec_surf


def padding(img, padsize):
	pad = np.pad(img, 2, 'constant', constant_values=0)
	return pad


def postprocess(img, vx_res):
	print('\npostprocessing the image')
	im =io.imread(img)
	s, v, f = surf(im)
	sv = sv_calc_uneven(s, vx_res, im.shape)
	por = 1- (im/255).mean()
	print('\nporosity =',por)
	print('\nspecific surface =', sv)
	print('\n')



