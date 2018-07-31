# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 09:15:42 2018

@author: braatenj
"""

import sys
import os
import subprocess

# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

inFile = ltcdb.get_file("Select Shapefile Polygon File To Convert to Centroids", filetypes = [("shp files","*.shp")])
if inFile == '.':
  sys.exit('ERROR: No vector file was selected.\nPlease re-run the script and select a vector file.')

if os.path.splitext(inFile)[1] != '.shp':
  sys.exit('ERROR: The selected vector file was not a Shapefile (.shp).\nPlease re-run the script and select a vector file.')


outFile = ltcdb.save_file('Save Centroid File As:')

#inFile = r"D:\work\proj\park_service\nccn-glkn\LT-ChangeDB_test\mora\vector\change\PARK_CODE-MORA-NBRz-7-19842017-06010930-dist_info_11mmu_8con\PARK_CODE-MORA-NBRz-7-19842017-06010930-dist_info_11mmu_8con_1992.shp"
#inFile = r"D:\work\proj\park_service\nccn-glkn\LT-ChangeDB_test\mora\vector\test\dist_info_1992.shp"
#outFile = r"D:\work\temp\___righthere11111.shp"

tableName = ('\"'+os.path.splitext(os.path.basename(inFile))[0]+'\"')
tableName = os.path.splitext(os.path.basename(inFile))[0]

cmd = 'ogr2ogr -f "ESRI Shapefile" '+outFile + ' ' + inFile + ' -dialect sqlite -sql "SELECT ST_Centroid(geometry), * FROM '+tableName+'"' 
print(cmd)
subprocess.call(cmd, shell=True)


