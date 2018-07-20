# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 15:32:55 2018

@author: braatenj
"""

import os
import subprocess
import zipfile
from glob import glob
import sys
import time 


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb



headDir = ltcdb.get_dir("Select the project head folder")
if headDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')

vectorDir = os.path.join(headDir, 'vector')
if not os.path.isdir(vectorDir):
  sys.exit('ERROR: Can\'t find the vector folder.\nTrying to find it at this location: '+vectorDir+'\nIt\'s possible you provided an incorrect project head folder.\nPlease re-run the script and select the project head folder.')

fileName = ltcdb.get_file("Select Vector File To Prepare", vectorDir)
if fileName == '.':
  sys.exit('ERROR: No vector file was selected.\nPlease re-run the script and select a vector file.')


startTime = time.time()

bname = os.path.basename(os.path.splitext(fileName)[0])
standardFileShp = os.path.normpath(os.path.join(vectorDir, bname+'_ltgee_epsg4326.shp'))
standardFileKml = standardFileShp.replace('.shp', '.kml')

                            

shpCmd = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:4326 '+ standardFileShp +' '+ fileName
subprocess.call(shpCmd, shell=True)

zipThese = glob(vectorDir+'/*_ltgee_epsg4326*')

with zipfile.ZipFile(os.path.join(vectorDir, bname+'_ltgee.zip'), 'w') as zipIt:
  for f in zipThese:   
    zipIt.write(f, os.path.basename(f))
    
print('\nDone!')      
print("LT-GEE vector setup took {} minutes".format(round((time.time() - startTime)/60, 1)))    
