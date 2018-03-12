# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 08:35:19 2018

@author: braatenj
"""

import imp
import subprocess



# =============================================================================
# 	Verify we have conda-forge channel
# =============================================================================
cmd = 'conda config --add channels conda-forge'
subprocess.call(cmd, shell=True)



# =============================================================================
# 	Verify we have GDAL
# =============================================================================
found = False
while (found == False):
  try:
    print('\nChecking to see if GDAL is installed...\n')
    blank = imp.find_module('gdal')
    found = True
  except ImportError:
    print('GDAL is not installed, starting install...\n')
    cmd = 'conda install -c conda-forge gdal'
    subprocess.call(cmd, shell=True)
    try:     
      blank = imp.find_module('gdal')
      found = True
    except ImportError:
      print('\nIt looks like you didn\'t choose to install it, try again\n')
      found = False


    
# =============================================================================
# 	Verify we have NumPy
# =============================================================================  
found = False
while (found == False):   
  try:
    print('\nChecking to see if NumPy is installed...\n')
    blank = imp.find_module('numpy')
    found = True
  except ImportError:
    print('NumPy is not installed, starting install...\n')
    cmd = 'conda install -c conda-forge numpy'
    subprocess.call(cmd, shell=True)
    try:     
      blank = imp.find_module('numpy')
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
