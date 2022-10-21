from pathlib import Path    #Universal path 
import xmltodict    #Read&write xml files
import shutil as sh
import os, sys
import time 
import launchPlugin as plm
import tess_foam as bf
import argparse
import postprocess as pp

def readxml(xmlfile):
    with open(xmlfile,'r') as f:
        parxml = f.read()
        parameters = xmltodict.parse(parxml)
        for elm in parameters['par']:
            parameters['par'][elm] = dict(parameters['par'][elm])
        parameters['par'] = dict(parameters['par'])
        parameters = parameters['par']
    return parameters

parser = argparse.ArgumentParser()

parser.add_argument('--name', type=str, required=True)
args = parser.parse_args()

vx_res = 50e-06
print('WARNING: voxel resulution is set to',vx_res,', you may need to change it!!')

t0 = time.time()

cwd = Path(os.getcwd())

par = readxml(args.name)

# with open('mondiale11.xml','r') as f:
#     parxml = f.read()
#     par = xmltodict.parse(parxml)
#     for elm in par['par']:
#         par['par'][elm] = dict(par['par'][elm])
#     par['par'] = dict(par['par'])
#     par = par['par']

pOut = Path(cwd / par['paths']['pOut'])
pIn = Path( cwd / par['paths']['pIn'])

print('creating folder',pOut)
# os.mkdir(pOut)
try:
    os.makedirs(pOut, exist_ok = True)
    print("Directory '%s' created successfully" %pOut.name)
except OSError as error:
    print("Directory '%s' already exist")


aggSphDict = {
        'Export' : str(pOut / 'sphPackCoord.txt'),
        'OUTPREV': str(pOut / 'sphPackPreview.fda'),
        'OUT' : str(pOut / 'sphPackOutput.fda'),
        'NB' : par['aggSph']['NB'],
        'NBType' : 'Constante',
        'Repul' : par['aggSph']['Repul'],
        'R' : par['aggSph']['R'],
        'RType' : 'Constante',
        'Beta' : par['aggSph']['Beta'],
        'Alpha' : par['aggSph']['Alpha'],
        'val' : 255,
        'Periodic' : True,
        'W' : par['aggSph']['W']
        }

nodEdgDict = {
    'FileNameFull': 'ballSticks.sb',
    'FileName': 'ballSticks',
    'IN': str(pOut / 'ballSticks.sb') , 
    'OUT': str(pOut / 'ballSticks.fda'),
    'OUTPREV': str(pOut / 'prevBallSticks.fda')  
    }

morphDict = {
#     'FileNameFull': 'test1.sb',
#     'FileName': 'test1',
    'IN': str(pOut / 'ballSticks.fda') , 
    'OUT': str(pOut / 'morphOut.fda'),
    'OUTPREV': str(pOut / 'prevMorphOut.fda'),
    'Operation': par['morph']['Operation'],
    'tv': par['morph']['tv']
	}

surfaceDict = {
     'Export': str(pOut / 'surfaceArea3d.txt'),
     'FileNameFull': 'morphOut.fda',
     'FileName': 'morphOut',
     'FileDir':  str(pOut),
     'IN': str(pOut / 'morphOut.fda') ,
     'OUT': str(pOut / 'morphOutSurf.fda'),
     'OUTPREV': str(pOut / 'morphOutSurfPrev.fda')  
    }

tiffDict = {
    'IN': str(pOut / 'morphOut.fda') , 
    'OUT': str(pOut / 'foamTest.tif'),  
}


### Launch sphere packing plugin

aggSph = plm.run_plugin('RMM_AggSPh', aggSphDict, pIn,pOut)
aggSph.copy_exe()
aggSph.edit_xml()
aggSph.run_exe()

### Launch tessellation

bf.bfoam(pOut,par['tess']['R_node'],par['tess']['R_strut'],iters=int(par['tess']['iter']), periodic=False)

### Launch ball&Sticks model creation
ballSticks = plm.run_plugin('CreateFDAFromRandModelTXT', nodEdgDict, pIn, pOut)
ballSticks.copy_exe()
ballSticks.edit_xml()
ballSticks.run_exe()

### Launch morphology operations

morphOps = plm.run_plugin('BinaryGeodesicMorpho3D', morphDict, pIn, pOut)
morphOps.copy_exe()
morphOps.edit_xml()
morphOps.run_exe()

### Launch surface area calculation

surfArea = plm.run_plugin('3DSurfaceArea', surfaceDict, pIn, pOut)
surfArea.copy_exe()
surfArea.edit_xml()
surfArea.run_exe()

### Launch tiff creation

fdaToTIFF = plm.run_plugin('FDAToTIFF', tiffDict, pIn, pOut)
fdaToTIFF.copy_exe()
fdaToTIFF.edit_xml()
fdaToTIFF.run_exe()

t1 = time.time()
print('Total runtime is', t1 - t0, 'seconds')

pp.postprocess(pOut / 'foamtest.tif', vx_res)