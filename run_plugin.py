import subprocess, sys, os   #interface with the OS
from pathlib import Path    #Universal path 
import xmltodict    #Read&write xml files
import shutil as sh

class run_plugin(object):
    def __init__(self, plugin, par, pathIN, pathOUT):
        '''This class carries out all the operations required to run a PlugIm! module outside it using python code '''
    
        self.plugin = plugin    # name of the plugin
        self.par = par    # dictionary of the parameters to modify
        self.pathIN = Path(pathIN)    # Paths of the file to copy: ex. C:\Users\Enrico\PlugIm\plugim\PlugIns
        self.pathOUT = Path(pathOUT)
        self.fExe = self.plugin + '.exe'
        self.fXml = self.plugin + 'PAR.xml'
    
    def copy_exe(self):
        '''This method copy the plugIN .exe file into the working directory'''
        
        pIn = self.pathIN / self.plugin / self.fExe
        pOut = self.pathOUT / fExe
        
        try:
            sh.copyfile(pIn, pOut)
            print(fExe,'copied into', pOut.parent)

        except OSError as e:
            os.mkdir(self.pathOUT)
            print('copying',fExe,' into', pOut.parent)
            sh.copyfile(pIn, pOut)
    
    
    def edit_xml(self):
        '''This method edit the plugIN .xml ile of the parameters and write it in the working directory'''
        
        pIn = self.pathIN / self.plugin / self.fXml
        pOut = self.pathOUT / fXml
        
        print('Reading the', fXml,' file')
        
        try :
            with open( pIn, 'r') as f:
                xmlf = f.read()
                xmlPar = xmltodict.parse(xmlf)
        except OSError as e:
            print('Directory:', pIn.parent,' not found!')
            
        print('Setting the new parameters...')
        for key in self.par:
            xmlPar['Root'][key]['@Value'] = self.par[key]
        
        print('Creating new file at working directory')
        try:
            with open( pOut, 'w') as f:
                f.write(xmltodict.unparse(xmlPar, pretty=True))
            print('Done!')
        except OSError as e:
            print('Directory:',pOut.parent,'not found!')
        
    def run_exe(self):
        '''This method run the plugin .exe file using the new parameters, it output the '''
        
        try:
            print('Trying running plugin...')
            p = subprocess.run( [self.pathOUT / self.fExe], capture_output=True, text=True)
            returnCode = p.check_returncode()
            out = p.stdout.split('\n')
            print('Return_code=', returnCode)
            print(*out, sep='\n', end='\n')
        except:
            print('Something went wrong!')
            print('Return_code=', returnCode)
            print(*out, sep='\n', end='\n')
