# -*- coding: utf-8 -*-
"""
Created on Tue Mar 06 14:09:32 2018

@author: braatenj
"""

import time
import os
import fnmatch
import subprocess
import sys
from osgeo import ogr
import Tkinter, tkFileDialog



def get_info(name):
  pieces = name.split('-')[0:6]
  return {'key': pieces[0],
          'value': pieces[1],
          'indexID': pieces[2],
          'nVert': int(pieces[3]),
          'startYear':int(pieces[4][0:4]),
          'endYear':int(pieces[4][4:8])}





root = Tkinter.Tk()
chunkDir = str(tkFileDialog.askdirectory(initialdir = "/",title = "Select the folder that contains LT-GEE files\n\n(*\\raster\\prep)"))
root.destroy()
if chunkDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')


# find the tif chunks
tifs = []
for root, dirnames, filenames in os.walk(chunkDir):
  for filename in fnmatch.filter(filenames, '*.tif'):
    tifs.append(os.path.join(root, filename))

if len(tifs) == 0:
  sys.exit('ERROR: There are no TIF files in the folder selected.\nPlease fix this.')

root = Tkinter.Tk()
outDir = str(tkFileDialog.askdirectory(initialdir = "/",title = "Select folder to place LT segmentation outputs in\n\n(*\\raster\\landtrendr\segmentation)"))
root.destroy()
if outDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')
  
#TODO check for existing files

"""
root = Tkinter.Tk()
clipFile = str(tkFileDialog.askopenfilename(initialdir = "/",title = "Select standardized vector file\n\n(*\\vector\\*ltgee*.shp)"))
root.destroy()
"""
  
#TODO check to make sure that it is a .shp and that it has *ltgee* possibly check for epsg5070 proj - should be file is *ltgee*

"""
# get the arguments
arg = sys.argv
chunkDir = arg[1]
outDir = arg[2]  
clipFile = arg[3]
"""


#chunkDir = '/vol/v1/proj/stem_improv_paper/raster/prep'
#outDir = '/vol/v1/proj/stem_improv_paper/raster/r0701' 
#clipFile = '/vol/v1/proj/stem_improv_paper/vector/regions/study_regions.shp'
#key = 'epa_code'
#value = 'r0701'
#indexID = 'nbr'
#nVert = 7
#startYear = 1984
#endYear = 2016

start_time = time.time()
######################################################################

# define the projection
proj = 'EPSG:5070'

# make sure path parts are right
if chunkDir[-1] != '/':
  chunkDir += '/'
if outDir[-1] != '/':
  outDir += '/'

# set the unique names 
names = list(set(['-'.join(fn.split('-')[0:6]) for fn in tifs])) 


# loop through each unique names, find the matching set, merge them as vrt, and then decompose them
commands = [] #record all commands to run
for name in names:
  #name = names[0]  
  runName = os.path.splitext(os.path.basename(name))[0]
  thisOutDir = os.path.join(outDir, runName)
  if not os.path.exists(thisOutDir):
    os.mkdir(thisOutDir)
  
  print('\nWorking on segmentation: '+runName)
  # find the files that belong to this set  
  matches = []
  for tif in tifs:   
    if name in tif:
      matches.append(tif)

  # get info about the GEE run
  info = get_info(runName)

  # make a list of tile tifs
  vrtFile = chunkDir+runName+'.vrt'
  tileListFile = vrtFile.replace('.vrt', '_filelist.txt')
  tileList = open(tileListFile, 'w')
  for match in matches:
    tileList.write(match+'\n')
  tileList.close()


  # create vrt
  cmd = 'gdalbuildvrt -q -input_file_list '+tileListFile+' '+vrtFile
  print('   Building virtual raster')
  subprocess.call(cmd, shell=True)


  # define the list of replacement types in the new out images    
  outTypes = ['vert_yrs.tif',
              'vert_src.tif',
              'vert_fit.tif',
              'ftv_idx.tif',            
              'ftv_tcb.tif',
              'ftv_tcg.tif',
              'ftv_tcw.tif']


  # make a list of band ranges for each out type
  vertStops = []
  for vertType in range(4):  
    vertStops.append(vertType*info['nVert']+1)
  
  nYears = (info['endYear'] - info['startYear']) + 1
  ftvStops = []  
  for ftvType in range(1,len(outTypes)-2):  
    ftvStops.append(ftvType*nYears+vertStops[-1])
    
  bandStops = vertStops+ftvStops
  bandRanges = [range(bandStops[i],bandStops[i+1]) for i in range(len(bandStops)-1)]

  """
  # get the driver from the inShape file ext
  ext = str.lower(os.path.splitext(clipFile)[-1])
  drivers = {'.shp'    :'ESRI Shapefile', 
             '.geojson': 'GeoJSON'}           
  driver = ogr.GetDriverByName(drivers[ext])
  
  
  # read in the inShape file and get the extent of the feature defined by key and value
  dataSource = driver.Open(clipFile, 0)
  layer = dataSource.GetLayer()
  layer.SetAttributeFilter(info['key']+" = '"+info['value']+"'")
  feature = layer.GetNextFeature()  
  extent = feature.GetGeometryRef().GetEnvelope()
  
  
  # format the exent as -projwin arguments for gdal translate
  projwin = '{} {} {} {}'.format(extent[0], extent[3], extent[1], extent[2])    
  #projwin = '-2166434 2699450 -2164169 2697218'  
  """  
  
  # loop through the datasets and pull them out of the mega stack and write them to the define outDir
  print('   Unpacking file:')
  for i in range(len(outTypes)):   
    outBname = runName+'-'+outTypes[i]   
    outFile = os.path.join(thisOutDir, outBname)
    print('      '+outBname)
    bands = ' -b '+' -b '.join([str(band) for band in bandRanges[i]])
    #cmd = 'gdal_translate -q -of ENVI -a_srs ' + proj + bands + ' -projwin '+projwin+' '+ vrtFile + ' ' + outFile
    cmd = 'gdal_translate -q -of GTiff -a_srs ' + proj + bands +' '+ vrtFile + ' ' + outFile
    subprocess.call(cmd, shell=True)

print('\n')
print('\n')
print('Done!')      
print("Process took {} minutes".format(round((time.time() - start_time)/60, 1)))  

    
    
    
    
    