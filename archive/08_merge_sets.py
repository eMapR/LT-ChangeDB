# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 20:56:26 2018

@author: braatenj
"""

import fnmatch
import subprocess
import sys
import os
import Tkinter, tkFileDialog



def get_dir(message):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisDir = str(tkFileDialog.askdirectory(initialdir = "/",title = message))
  root.destroy()
  return thisDir
  


changeDir = get_dir("Select the folder that contains annual change files\n\n(*\\raster\\landtrendr\\change\\*)")
if changeDir == '':
  sys.exit('ERROR: No folder containing annual change files was selected.\nPlease re-run the script and select a folder.')
changeDir = os.path.normpath(changeDir)


# find the tif chunks
changeFiles = []
for root, dirnames, filenames in os.walk(changeDir):
  for filename in fnmatch.filter(filenames, '*annual*.shp'):
    changeFiles.append(os.path.join(root, filename))

changeDirPieces = changeDir.split(os.sep)
outDir = os.sep.join(changeDirPieces[0:-3])+os.sep+'vector'

bname = os.path.basename(changeFiles[0])
bnamePieces = bname.split('-')
outName = '-'.join(bnamePieces[0:2] + bnamePieces[-5:]).replace('annual', 'annual_combined')
outPath = os.path.join(outDir, 'change.shp')

mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + outPath + ' ' + changeFiles[0]
subprocess.call(mergeCmd, shell=True)
if len(changeFiles) > 1:
  for i in range(1, len(changeFiles)):
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + outPath + ' ' + changeFiles[i]  
    subprocess.call(mergeCmd, shell=True)
    
    
