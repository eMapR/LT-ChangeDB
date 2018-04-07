# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 08:35:19 2018

@author: braatenj
"""

import imp
import subprocess


# =============================================================================
# 	Define the dependent libraries
# =============================================================================

libs = [
  'pandas',
  'rasterstats',
  'rasterio',
  'shapely',
  'fiona',
  'shapely',
  'gdal'
]




# =============================================================================
# 	Verify we have conda-forge channel
# =============================================================================

cmd = 'conda config --add channels conda-forge'
subprocess.call(cmd, shell=True)




# =============================================================================
# 	Verify we have all the dependent libraries.
# =============================================================================

for lib in libs:
  found = False
  while (found == False):
    try:
      print('\nChecking to see if '+lib+' is installed...\n')
      blank = imp.find_module(lib)
      found = True
    except ImportError:
      print(lib+' is not installed, starting install...\n')
      cmd = 'conda install -c conda-forge '+lib
      subprocess.call(cmd, shell=True)
      try:     
        blank = imp.find_module(lib)
        found = True
      except ImportError:
        print('\nIt looks like you didn\'t choose to install it, try again\n')
        found = False




# import GDAL to check on bindings for some methods
from osgeo import gdal
error = 0

# =============================================================================
# 	Verify we have next gen bindings with the sievefilter method.
# =============================================================================

try:
  print('Checking to see if gdal.SieveFilter() is available...\n')
  blank = gdal.SieveFilter
except:
  print('   ERROR: gdal.SieveFilter() is not available. You are likely using "old gen"')
  print('          bindings or an older version of the next gen bindings\n')
  error += 1



# =============================================================================
# 	Verify we have next gen bindings with the polygonize method.
# =============================================================================

try:
  print('Checking to see if gdal.Polygonize() is available...\n')
  blank = gdal.Polygonize
except:
  print('   ERROR: gdal.Polygonize() is not available.  You are likely using "old gen"')
  print('          bindings or an older version of the next gen bindings\n')
  error += 1
  
if error > 0:
  print('Please fix the errors before continuing with the workflow\n')
