from pathlib import Path    #Universal path 
import xmltodict    #Read&write xml files
import shutil as sh
import os, sys
import time 
import launchPlugin as plm
import tess_foam as bf
import numpy as np
import pandas as pd
import argparse

# def get_data(filename):
#     sphraw = pd.read_csv( filename, delim_whitespace=True, header=None)
#     bbox_side = sphraw.iloc[0,:3].values
#     n_sph = sphraw.iloc[0,3]
#     centers = sphraw.iloc[1:,:3].values
#     centers, unique_i = np.unique(centers,axis=0, return_index=True)    # check for unique spheres (sometimes multiple spheres have same location and radius)
#     rads = sphraw.iloc[1:,3].values[unique_i]
#     return centers, rads, n_sph, ((0,0,0), tuple(bbox_side))


cwd = Path(os.getcwd())

parser = argparse.ArgumentParser()

parser.add_argument('--name', type=str, required=True)
parser.add_argument('--rad', type=float, required=True)
parser.add_argument('--rep', type=float, required=True)
parser.add_argument('--boxside', type=float, required=True)
parser.add_argument('--nb', type=int, required=True)


args = parser.parse_args()


alpha = np.linspace(0,1,21)
beta = np.linspace(0,1,21)

mesh = np.array(np.meshgrid(alpha,beta ))
combinations = mesh.T.reshape(-1, 2)

pOut = cwd / args.name    #'compacityTest'

pIn = Path( cwd / 'PlugIns/')

d = []
for elm in combinations:
    name = 'a_{alpha}_b_{beta}_agg'.format(alpha=int(elm[0]*100),beta=int(elm[1]*100))
    
    d.append({
        'Export' : str(pOut / (name+'.txt')),
        'OUTPREV': str(pOut / (name+'.fda')),
        'OUT' : str(pOut / (name+'.fda')),
        'NB' : int(args.nb),
        'NBType' : 'Constante',
        'Repul' : args.rep,
        'R' : args.rad,
        'RType' : 'Constante',
        'Beta' : np.round(elm[1],2),
        'Alpha' : np.round(elm[0],2),
        'val' : 255,
        'Periodic' : True,
        'W' : int(args.boxside)
        })

print('creating folder',pOut)

try:
    os.makedirs(pOut, exist_ok = True)
    print("Directory '%s' created successfully" %pOut.name)
except OSError as error:
    print("Directory '%s' already exist")


runtime = []

for el,i in zip(d,range(len(d))):
    t1 = time.time()
    print('\n')
    print('NAME:',Path(el['Export']).name.split('.txt')[0])
    aggSph = plm.run_plugin('RMM_AggSPh', el, pIn,pOut)
    aggSph.copy_exe()
    aggSph.edit_xml()
    aggSph.run_exe()
    os.remove(el['OUT'])
    t2 = time.time()
    runtime.append(t2-t1)
    print('runtime:',runtime[-1])
    print('\n')
    print('object %d/%d - %d object left' % (i,len(d), len(d)-i))
    print('\n')

print('\nmean runtime is: ', np.round(np.array(runtime).mean()))
