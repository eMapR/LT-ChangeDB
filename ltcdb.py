# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 12:04:05 2018

@author: braatenj
"""

from osgeo import gdal
from shutil import copyfile
import Tkinter, tkFileDialog
import subprocess
import os
import numpy as np
import sys
import math


def make_output_blanks(inputFtv, outPuts, adj):
  #inputFtv = vertYrsFile
  src_ds = gdal.Open(inputFtv)
  tx = src_ds.GetGeoTransform()
  prj = src_ds.GetProjection()
  driver = src_ds.GetDriver()
  band = src_ds.GetRasterBand(1)
  xsize = band.XSize
  ysize = band.YSize
  nBands = src_ds.RasterCount
  src_ds = None
  
  nBands += adj
  for i, thisOut in enumerate(outPuts):
    if i == 0:
      # make a new file
      copyThis = thisOut
      dst_ds = driver.Create(thisOut, xsize, ysize, nBands, band.DataType)
      dst_ds.SetGeoTransform(tx)
      dst_ds.SetProjection(prj)
      dst_ds = None
    else:
      copyfile(copyThis, thisOut)
  return nBands


def get_info(name):
  pieces = name.split('-')[0:7]
  return {'key': pieces[0],
          'value': pieces[1],
          'indexID': pieces[2],
          'nVert': int(pieces[3]),
          'startYear':int(pieces[4][0:4]),
          'endYear':int(pieces[4][4:8]),
          'startDay':pieces[5][0:4],
          'endDay':pieces[5][4:8],
          'name': '-'.join(pieces)}

 
def write_array(dsOut, band, data, x, y):
  dataBand = dsOut.GetRasterBand(band+1)
  data = data[band, :, :]
  dataBand.WriteArray(data, x, y)
  
  
  
def get_dir(message):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisDir = os.path.normpath(str(tkFileDialog.askdirectory(initialdir = "/",title = message)))
  root.destroy()
  return thisDir


def get_file(message):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisFile = os.path.normpath(str(tkFileDialog.askopenfilename(initialdir = "/",title = message)))
  root.destroy()
  return thisFile


def get_delta(vertVals):
  segStartVal = vertVals[:-1]
  segEndVal = vertVals[1:]
  segDelta = segEndVal - segStartVal
  return segDelta


def make_vrt(chunkFiles, vrtFile):
  listFile = vrtFile.replace('.vrt', '_filelist.txt')
  tileList = open(listFile, 'w')
  for fn in chunkFiles:
    tileList.write(fn+'\n')
  tileList.close()
  
  cmd = 'gdalbuildvrt -q -input_file_list '+listFile+' '+vrtFile
  subprocess.call(cmd, shell=True)
  
  
#def add_field(layer, fieldName, dtype):
#  field = ogr.FieldDefn(fieldName, dtype)
#  layer.CreateField(field)
#  return layer

def year_to_band(bname):
  info = get_info(bname)
  startYear = info['startYear']
  endYear = info['endYear']
  nYears = (endYear - startYear)+1
  yearIndex = np.array([0]*(startYear)+range(0, nYears))
  return yearIndex


def update_progress(progress):
  sys.stdout.write( '\r   {0}% {1}'.format(int(math.floor(progress*100)), 'done'))
  sys.stdout.flush()