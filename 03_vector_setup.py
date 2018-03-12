# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 15:32:55 2018

@author: braatenj
"""

import os
import subprocess
import Tkinter, tkFileDialog
import sys
import zipfile
from glob import glob


#### At this point the fields need to be set to allow unique id
#### do we need to collapse muliple feature to one?


root = Tkinter.Tk()
fileName = str(tkFileDialog.askopenfilename(initialdir = "/",title = "Select Vector File To Prepare"))
root.destroy()

root = Tkinter.Tk()
outDirName = str(tkFileDialog.askdirectory(initialdir = "/",title = "Select Vector Output Folder"))
root.destroy()

bname = os.path.basename(os.path.splitext(fileName)[0])
standardFileShp = os.path.normpath(os.path.join(outDirName, bname+'_ltgee_epsg5070.shp'))
standardFileKml = standardFileShp.replace('.shp', '.kml')

                            
#kmlCmd = 'ogr2ogr -f "KML" ' + standardFileKml +' '+ fileName
#subprocess.call(kmlCmd, shell=True)

shpCmd = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:5070 '+ standardFileShp +' '+ fileName
subprocess.call(shpCmd, shell=True)

zipThese = glob(outDirName+'/*_ltgee_epsg5070*')

with zipfile.ZipFile(os.path.join(outDirName, bname+'_ltgee.zip'), 'w') as zipIt:
  for f in zipThese:   
    zipIt.write(f, os.path.basename(f))
    
    
