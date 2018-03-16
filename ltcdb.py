# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 12:04:05 2018

@author: braatenj
"""

from osgeo import gdal
from shutil import copyfile


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
  print(nBands)
  return nBands


def get_info(name):
  pieces = name.split('-')[0:6]
  return {'key': pieces[0],
          'value': pieces[1],
          'indexID': pieces[2],
          'nVert': int(pieces[3]),
          'startYear':int(pieces[4][0:4]),
          'endYear':int(pieces[4][4:8])}

 
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
  thisDir = str(tkFileDialog.askdirectory(initialdir = "/",title = message))
  root.destroy()
  return thisDir