# cefocat-plugim
Creation of foam-like geometries using plugIm! (https://www.plugim.fr/) -- Windows only

#### How to use
On a command prompt or Windows PowerShell type:

Edit the xml file with all the required parmeters: a template is provided.

`python .\geoGenArgPostTort.py --name .\xmlTemplate.xml`

A directory is created, named as reported in the xml file, containing:
* original TIFF file
* padded TIFF file
* uncleaned STL file generated with marching cubes algorithm from the padded TIFF file
* .txt file with porosity and specific surface data:
    * porosity is expressed as the solid fraction Vv--> real porsity is 1-Vv)
    * specific surface is reported in voxel^2 / voxel^3  
    * specific surface and porosity in m^2/m^3 (macroDescriptors.txt)
* .txt file with tortuosity data

To clean the STL file from loose parts use blender in background launching the `separate_loose.py` script, within the directory containing the STL file:

`blender -b -P separate_loose.py`
