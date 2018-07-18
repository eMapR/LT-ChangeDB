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
  'gdal'
]

error = 0


# =============================================================================
# 	Verify we have conda-forge channel
# =============================================================================

cmd = 'conda config --add channels conda-forge'
subprocess.call(cmd, shell=True)




# =============================================================================
# 	Verify we have all the dependent libraries.
# =============================================================================

for lib in libs:
  #found = False
  #while (found == False):
    try:
      print('\nChecking to see if '+lib+' is installed...')
      blank = imp.find_module(lib)
      print('    '+lib+' is installed')
    except ImportError:
      print('    '+lib+' is NOT installed')
      error += 1


# import GDAL to check on bindings for some methods
try:
  blank = imp.find_module('gdal')

  from osgeo import gdal
  
  
  # =============================================================================
  # 	Verify we have next gen bindings with the sievefilter method.
  # =============================================================================
  
  try:
    print('\nChecking to see if gdal.SieveFilter() is available...')
    blank = gdal.SieveFilter
    print('    gdal.SieveFilter() is available')
  except:
    print('   ERROR: gdal.SieveFilter() is not available. You are likely using "old gen"')
    print('          bindings or an older version of the next gen bindings\n')
    error += 1
  
  
  
  # =============================================================================
  # 	Verify we have next gen bindings with the polygonize method.
  # =============================================================================
  
  try:
    print('\nChecking to see if gdal.Polygonize() is available...')
    blank = gdal.Polygonize
    print('    gdal.Polygonize() is available')
  except:
    print('   ERROR: gdal.Polygonize() is not available. You are likely using "old gen"')
    print('          bindings or an older version of the next gen bindings\n')
    error += 1

except:
  if error > 0:
    print('Please fix the errors before continuing with the workflow\n')

