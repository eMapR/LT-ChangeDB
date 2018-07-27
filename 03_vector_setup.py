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


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder
headDir = ltcdb.get_dir("Select the project head folder", scriptDname)
ltcdb.is_headDir(headDir)

# get dir paths we need 
vectorDir = ltcdb.dir_path(headDir, 'v')

# select a vector file
fileName = ltcdb.get_file("Select Vector File To Prepare", vectorDir, [("Shapefile","*.shp"), ("GeoJSON","*.geojson")])
if fileName == '.':
  sys.exit('ERROR: No vector file was selected.\nPlease re-run the script and select a vector file.')

# start tracking time
startTime = time.time()

# make new shapefile name
bname = os.path.basename(os.path.splitext(fileName)[0])
standardFileShp = os.path.normpath(os.path.join(vectorDir, bname+'_ltgee_epsg4326.shp'))

# standardize projection and format for GEE
shpCmd = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:4326 '+ standardFileShp +' '+ fileName
cmdFailed = subprocess.call(shpCmd, shell=True)
ltcdb.is_success(cmdFailed)

# find files to zip
zipThese = glob(vectorDir+'/*_ltgee_epsg4326*')
if len(zipThese) == 0:
  sys.exit('ERROR: There were no *_ltgee_epsg4326* files found in dir:\n'+ vectorDir+'\nNo files to zip.')

# zip files
with zipfile.ZipFile(os.path.join(vectorDir, bname+'_ltgee.zip'), 'w') as zipIt:
  for f in zipThese:   
    zipIt.write(f, os.path.basename(f))
    
print('\nDone!')