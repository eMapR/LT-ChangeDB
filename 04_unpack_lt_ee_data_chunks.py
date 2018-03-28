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
from osgeo import gdal
from glob import glob


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb





root = Tkinter.Tk()
chunkDir = str(tkFileDialog.askdirectory(initialdir = "/",title = "Select the folder that contains LT-GEE files\n\n(*\\raster\\prep\\gee_chunks)"))
root.destroy()
if chunkDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')
  
#TODO make sure  that there is gee_chunks in string


# find the tif chunks
tifs = []
for root, dirnames, filenames in os.walk(chunkDir):
  for filename in fnmatch.filter(filenames, '*.tif'):
    tifs.append(os.path.join(root, filename))

# are there any tif files to work with?
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
for name in names:
  #name = names[0] 
  # create output dirs
  runName = os.path.splitext(os.path.basename(name))[0]
  
  # make a dir to unpack the data
  os.pardir
  thisOutDirPrep = os.path.join(os.path.dirname(chunkDir), os.pardir, runName)
  if not os.path.exists(thisOutDirPrep):
    os.mkdir(thisOutDirPrep)
  
  # make a dir for the final data stacks 
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
  info = ltcdb.get_info(runName)


  # make a master vrt
  masterVrtFile = os.path.normpath(os.path.join(thisOutDirPrep, runName+'.vrt'))
  ltcdb.make_vrt(matches, masterVrtFile)
  
  
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


  # set some size variables
  srcVrt = gdal.Open(masterVrtFile)
  xSize = srcVrt.RasterXSize
  ySize = srcVrt.RasterYSize
  blockSize = 512
  srcVrt = None

  
  # loop through the datasets and pull them out of the mega stack and write them to the define outDir
  print('   Unpacking file:')
  for i in range(len(outTypes)):
    #i=0
    print('      '+runName+'-'+outTypes[i])
    block = 0
    for y in xrange(0, ySize, blockSize):
      #yRange = range(0, ySize, blockSize)
      #y=yRange[5]
      if y + blockSize < ySize:
        rows = blockSize
      else:
        rows = ySize - y
      for x in xrange(0, xSize, blockSize):
        #xRange = range(0, xSize, blockSize)
        #x=xRange[4]
        if x + blockSize < xSize:
          cols = blockSize
        else:
          cols = xSize - x  
        
        outBname = runName+'-'+ str(block).zfill(3)+'_'+outTypes[i]
        outFileBlock = os.path.normpath(os.path.join(thisOutDirPrep, outBname))
        bands = ' -b '+' -b '.join([str(band) for band in bandRanges[i]])
        win = '{0} {1} {2} {3}'.format(x, y, blockSize, blockSize)
        cmd = 'gdal_translate -q -of GTiff -a_srs ' + proj + ' -srcwin '+ win + ' ' + bands +' '+ masterVrtFile + ' ' + outFileBlock #
        subprocess.call(cmd, shell=True)
  
        block += 1

    blockFiles = glob(thisOutDirPrep+'/*'+outTypes[i])
    # TODO deal with not finding files 
    
    # create vrt
    outTypeVrtFile = os.path.normpath(os.path.join(thisOutDirPrep, runName+'-'+outTypes[i])).replace('.tif', '.vrt')
    ltcdb.make_vrt(blockFiles, outTypeVrtFile)
    
    # make the merged file
    outFile = os.path.normpath(os.path.join(thisOutDir, runName+'-'+outTypes[i]))
    cmd = 'gdal_translate -q -of GTiff -a_srs ' + proj + ' ' + outTypeVrtFile + ' ' + outFile #
    subprocess.call(cmd, shell=True)

    # clear the dir for the next data
    deleteThese = glob(thisOutDirPrep+'/*'+os.path.splitext(outTypes[i])[0]+'*')
    for this in deleteThese:
      os.remove(this)

print('\n')
print('\n')
print('Done!')      
print("Process took {} minutes".format(round((time.time() - start_time)/60, 1)))

  
    
    
      
