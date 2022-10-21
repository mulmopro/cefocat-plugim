import numpy as np
import tess as t
import pandas as pd
import pickle as pk
import time, sys, os
from pathlib import Path

# Funtions
    
def foam_iter(ctr,rd,box,itr=250, per=False):
    for i in range(itr):
        foam_it = t.Container(ctr, limits=box, periodic=per, radii=rd)
        ctr = np.array([item.centroid() for item in foam_it])
        rd = np.array([item.radius for item in foam_it])
    return foam_it

"""
This function takes all the faces vertices list of each cell in the tessellation
and reconstruct the edges connecivity. It return a list of list, in which each
element is the connection between two points in the cell vertices list
"""


def edgy(faces):
    edges = [[], []]
    for facet in faces:
        edges[0].extend(facet[:-1]+[facet[-1]])
        edges[1].extend(facet[1:]+[facet[0]])

    edges = np.vstack(edges).T
    edges = np.sort(edges, axis=1)
    edges = edges[:, 0] + 1j*edges[:, 1]  # Convert to imaginary
    edges = np.unique(edges)  # Remove duplicates
    edges = np.vstack((np.real(edges), np.imag(edges))).T  # Back to real

    return edges


"""
This function return only unique pairs of edges using sets
"""


def uniquify(edges):
    new = [tuple(row) for row in edges.reshape(len(edges), 6)]
    unique = list(dict.fromkeys(new))
    out = np.array(unique).reshape(len(unique), 2, 3)
    return out


"""
This function return only unique vertices of the foam calculated frome edges
"""


def getPoints(edges):
    pp = edges.reshape(len(edges)*2, 3)
    pp_tup = [tuple(row) for row in pp]
    pp_unq = list(dict.fromkeys(pp_tup))
    return np.array(pp_unq)


"""
This function takes 4 INPUTS: 
- the tessellation container, 'foam'
- number of decimal to which round the coordinates (default is 5)
- which additional outputs enable ( default is False)
return up to 3 output:
- All the edges regrouped in a single array
- If 'edge_class=True': all the edges, in the form of Geom.py class,
    regrouped in a single list
- If 'edge_cell=True':all the edges, regrouped per cell, in a single array
"""


def allEdgy(cells, decim=5):
    faces = [elem.face_vertices() for elem in cells]
    vertices = [np.array(elem.vertices()) for elem in cells]
    links = [np.array(edgy(elem), dtype=int) for elem in faces]
    edges_cells = [elem[item] for elem, item in zip(vertices, links)]
    edge_unsort = np.around(np.vstack(edges_cells), decimals=decim)
    edge_sorted = np.array([t[::-1] if ((t[0, 0] < t[1, 0]) or (t[0, 0] == t[1, 0]
                                                                and t[0, 1] < t[1, 1]) or (t[0, 0] == t[1, 0])
                                        and t[0, 1] == t[1, 1] and t[0, 2] < t[1, 2])
                            else t for t in edge_unsort])
    allEdges = uniquify(edge_sorted)
    return allEdges

def get_data(filename):
    sphraw = pd.read_csv( filename, delim_whitespace=True, header=None)
    bbox_side = sphraw.iloc[0,:3].values
    n_sph = sphraw.iloc[0,3]
    centers = sphraw.iloc[1:,:3].values
    centers, unique_i = np.unique(centers,axis=0, return_index=True)    # check for unique spheres (sometimes multiple spheres have same location and radius)
    rads = sphraw.iloc[1:,3].values[unique_i]
    return centers, rads, n_sph, ((0,0,0), tuple(bbox_side))


def write_obj( filename, coord, radius, newBox, obj):
    
    obj_type = {'node': {'type': 1, 'columns': [ 'cx', 'cy', 'cz', 'r', 'idx' ]
                        },
                'edge': {'type': 5, 'columns':['sx','sy','sz','ex','ey','ez','r','idx']
                        }
        }[obj]
    
    if obj == 'edge':
        df = np.array([( item.flatten()) for item in coord ])
    else:
        df = coord
    
    df = np.insert( df, df.shape[-1], radius, axis=1)
    df = np.insert( df, df.shape[-1], range(len(df)), axis=1)
    df = pd.DataFrame( df, columns=obj_type['columns'])
    df = df.astype({ 'r': 'int64', 'idx': 'int64'})
    
    df_head = np.append( newBox[-1], [ len(coord), obj_type['type'] ]).astype(int)
    
    if not os.path.exists(filename):
        np.savetxt(filename, df_head.reshape(1, df_head.shape[0]), fmt='%d', delimiter=' ')
        df.to_csv(filename, mode='a', float_format='%.4f',sep=' ',index=False,header=False)
    else:
        with open(filename,'a') as f:
            np.savetxt(f,df_head.reshape(1, df_head.shape[0]), fmt='%d', delimiter=' ')
        df.to_csv(filename, mode='a', float_format='%.4f',sep=' ',index=False,header=False)


def delBoundEdges(edges, bound):    # new function remove boundary edges
    mp = edges.mean(axis=1)
    idx = ((mp == bound[0]).any(axis=1) | (mp == bound[-1]).any(axis=1))
    return idx


def bfoam(dest_p, sph_r, edg_r, iters=1, periodic=False):
    t0 = time.time()

    f_dataIN = dest_p / 'sphPackCoord.txt'
    f_dataOUT = dest_p / 'ballSticks.sb'

    print('Get input data...')
    centers, rads, n_sph, BoxTess = get_data(f_dataIN)

    print('Performing tessellation...')
    foam = foam_iter(centers, rads, BoxTess, itr=iters,per=periodic)

    allEdges = allEdgy(foam, decim=4)
    allEdges = allEdges[~delBoundEdges(allEdges, np.unique(BoxTess))]   # Remove boundary edges
    allPoints = getPoints(allEdges)

    pp = allPoints - allPoints.min(axis=0) #.round().astype(int)
    ee = allEdges - allPoints.min(axis=0)
    newBox = np.ceil(np.vstack([pp.min(axis=0),pp.max(axis=0)])).astype(int)

    print('Writing output text file')
    write_obj(f_dataOUT, pp, sph_r, newBox, 'node')
    write_obj(f_dataOUT, ee, edg_r, newBox, 'edge')

    t1 = time.time()

    print('Total runtime is', t1 - t0, 'seconds')
    print('Total nodes =', len(pp))
    print('Total struts =', len(ee))
    print('Total cells = ', len(foam))
    print('Nodes R = ', sph_r)
    print('Struts R = ', edg_r)
    