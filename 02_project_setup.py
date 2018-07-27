# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 11:23:22 2018

@author: braatenj
"""

import os
import sys


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder 
headDir = ltcdb.get_dir("Select or create and select a project head folder", scriptDname)
if headDir == '.':
  sys.exit()

# get the list of dirs to create
dirs = ltcdb.dir_path(headDir, 'all')

# create the dirs
for thisDir in dirs:
  if not os.path.exists(thisDir):
    os.makedirs(thisDir)
    
print('\nDone!')