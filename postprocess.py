import numpy as np
from skimage import io
import os
from skimage.measure import marching_cubes
from skimage.measure import mesh_surface_area
import tifffile as tif
import time
import trimesh 

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
    mesh_stl = mesh.export(filename)

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
	pad = np.pad(img, padsize, 'constant', constant_values=0)
	return pad


def macroPar(img, vx_res, pOut):
    print('\npostprocessing the image')
    im =io.imread(img)
    s, v, f = surf(im)
    sv = sv_calc_uneven(s, vx_res, im.shape)
    por = 1- (im/255).mean()
    # impad = padding(im,2).astype(np.uint8)
    # tif.imwrite( pOut / 'paddedFoam.tif', impad, dtype=np.uint8) #,compression=5
    # t0 = time.time()
    # export_stl(v,f, pOut / 'foamSTL')
    # t1 = time.time()
    print('\nporosity =',por)
    print('\nspecific surface =', sv)
    # print('\nTotal stl creation time is', t1 - t0, 'seconds')
    print('\n')

def padSTL(img, pOut):
    im =io.imread(img)
    impad = padding(im,2).astype(np.uint8)
    tif.imwrite( pOut / 'paddedFoam.tif', impad, dtype=np.uint8) #,compression=5
    s, v, f = surf(impad)
    t0 = time.time()
    export_stl(v,f, pOut / 'foamSTL.stl')
    t1 = time.time()
    print('\nTotal stl creation time is', t1 - t0, 'seconds')

