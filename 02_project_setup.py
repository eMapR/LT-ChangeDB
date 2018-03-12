# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 11:23:22 2018

@author: braatenj
"""

import os
import sys
import Tkinter, tkFileDialog



 
root = Tkinter.Tk()
dirName = str(tkFileDialog.askdirectory(initialdir = "/",title = "Select/Create a Project Folder"))
root.destroy()
if dirName == '':
  sys.exit('A "project folder" was not selected')

dirs = [
  os.path.join(dirName, 'raster'),
  os.path.join(dirName, 'vector'),
  os.path.join(dirName, 'scripts'),
  os.path.join(dirName, 'raster', 'prep'),
  os.path.join(dirName, 'raster', 'landtrendr'),
  os.path.join(dirName, 'raster', 'landtrendr', 'segmentation'),
  os.path.join(dirName, 'raster', 'landtrendr', 'change')
]

for thisDir in dirs:
  if not os.path.exists(thisDir):
    os.makedirs(thisDir)
