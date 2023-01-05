# -*- coding: utf-8 -*-
"""
Created on Fri May 12 13:39:27 2017
@author: braatenj
"""

from osgeo import gdal, ogr, osr
import numpy as np
import math
import subprocess
from glob import glob
import os
import sys
from shutil import copyfile


#============================FUNCTIONS===========================================
def get_dims(fileName):
    src = gdal.Open(fileName)
    ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
    sizeX = src.RasterXSize
    sizeY = src.RasterYSize
    lrx = ulx + (sizeX * xres)
    lry = uly + (sizeY * yres)
    return [ulx,uly,lrx,lry,xres,-yres,sizeX,sizeY]

def make_geo_trans(fileName, trgtDim):
    src   = gdal.Open(fileName)
    ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
    return((trgtDim[0], xres, xskew, trgtDim[1], yskew, yres))

def get_intersec(files):
    ulxAll=[]
    ulyAll=[]
    lrxAll=[]
    lryAll=[]
    for fn in files:
        dim = get_dims(fn)
        ulxAll.append(dim[0])
        ulyAll.append(dim[1])
        lrxAll.append(dim[2])
        lryAll.append(dim[3])
    return([max(ulxAll),min(ulyAll),min(lrxAll),max(lryAll)])

def get_offsets(fileName, trgtDim):
    dim = get_dims(fileName)
    xoff = math.floor(abs(dim[0]-trgtDim[0])/dim[4])
    yoff = math.ceil(abs(dim[1]-trgtDim[1])/dim[4])
    xsize = abs(trgtDim[0]-trgtDim[2])/dim[4]
    ysize = abs(trgtDim[1]-trgtDim[3])/dim[4]
    return([int(i) for i in [xoff, yoff, xsize, ysize]])

def get_band(fileName, trgtDim, band):
    offsets = get_offsets(fileName, trgtDim)
    src = gdal.Open(fileName)
    band = src.GetRasterBand(band)
    array = band.ReadAsArray(
        offsets[0],
        offsets[1],
        offsets[2],
        offsets[3])
    return(array)

def write_img(outFile, refImg, trgtDim, nBands, dataType, of):
    convertDT = {
        'uint8': 1,
        'int8': 1,
        'uint16': 2,
        'int16': 3,
        'uint32': 4,
        'int32': 5,
        'float32': 6,
        'float64': 7,
        'complex64': 10,
        'complex128': 11
    }
    dataType = convertDT[dataType]
    geoTrans = make_geo_trans(refImg, trgtDim)
    proj = gdal.Open(refImg).GetProjection()
    dims = get_offsets(refImg, trgtDim)
    driver = gdal.GetDriverByName(of)
    driver.Register()
    outImg = driver.Create(outFile, dims[2], dims[3], nBands, dataType) # file, col, row, nBands, dataTypeCode
    outImg.SetGeoTransform(geoTrans)
    outImg.SetProjection(proj)
    return(outImg)

def scale_to_8bit(img):
    mean = np.mean(img)
    stdev = np.std(img)
    n_stdev = 2
    imin = mean-(stdev*n_stdev)
    imax = mean+(stdev*n_stdev)
    if imin < 0:
        imin = 0
    img[np.where(img < imin)] = imin
    img[np.where(img > imax)] = imax
    img = np.round(((img-imin)/(imax-imin+0.0))*255)     
    return img

def scale_to_8bit_tc(img, tc):
    # standard TC stretch SR * 10000  
    n_stdev = 2  
    if tc == 'b':  
        imin = 3098-(1247*n_stdev)
        imax = 3098+(1247*n_stdev)
    if tc == 'g':
        imin = 1549-(799*n_stdev)
        imax = 1549+(799*n_stdev)
    if tc == 'w':  
        imin = -701-(772*n_stdev)
        imax = -701+(772*n_stdev)  

    img[np.where(img < imin)] = imin
    img[np.where(img > imax)] = imax
    img = np.round(((img-imin)/(imax-imin+0.0))*255)     
    return img

def write_bands(r, g, b, a, outFile, ref, trgtDim):
    outImg = write_img(outFile, ref, trgtDim, 4, 'int8', 'GTIFF')
    outBand = outImg.GetRasterBand(1) 
    outBand.WriteArray(r)
    outBand = outImg.GetRasterBand(2) 
    outBand.WriteArray(g)
    outBand = outImg.GetRasterBand(3) 
    outBand.WriteArray(b)
    outBand = outImg.GetRasterBand(4) 
    outBand.WriteArray(a)
    outImg = None

def transform_coords(epsgIn, epsgOut, x, y):
  # create a geometry from coordinates
  point = ogr.Geometry(ogr.wkbPoint)
  point.AddPoint(x, y)
  
  # create coordinate transformation
  inSpatialRef = osr.SpatialReference()
  inSpatialRef.ImportFromEPSG(int(epsgIn.split(':')[1]))
  
  outSpatialRef = osr.SpatialReference()
  outSpatialRef.ImportFromEPSG(int(epsgOut.split(':')[1]))
  
  coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
  
  # transform point
  point.Transform(coordTransform)
  
  # print point in EPSG 4326
  return (point.GetX(),point.GetY())

#===============================================END OF FUNCTIONS==========================


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder
headDir = ltcdb.get_dir("Select the project head folder", scriptDname)
ltcdb.is_headDir(headDir)

# get dir paths we need 
vidDir = ltcdb.dir_path(headDir, 'vid')
segDir = ltcdb.dir_path(headDir, 'rLs')
vectorDir = ltcdb.dir_path(headDir, 'v')
target_srs = 'EPSG:3857' # what EPSG should the output images be - use EPSG
te_srs = 'EPSG:4326'# what EPSG are the following bounding coordinages in


# find the polygon
vector = glob(os.path.join(vectorDir, '*LTaoi.shp'))
if len(vector) != 1:
  sys.exit('ERROR: There was a problem finding the "*LTaoi.shp" file in the project "vector" folder.') 

vector = vector[0]

# list the run directories in the seg folder 
ltRunDirs = [os.path.join(segDir, thisRunDir) for thisRunDir in os.listdir(segDir)]

# get the min change for each 
for segDir in ltRunDirs:
  info = ltcdb.get_info(os.path.basename(segDir))
  startYear = info['startYear']
  endYear = info['endYear']

  # find the ftv_tc files
  tcbFtv = glob(os.path.join(segDir,'*ftv_tcb.tif'))
  tcgFtv = glob(os.path.join(segDir,'*ftv_tcg.tif'))
  tcwFtv = glob(os.path.join(segDir,'*ftv_tcw.tif'))

  # make sure the tc ftv fiels are found
  for fn, srch in zip([tcbFtv, tcgFtv, tcwFtv], ['*ftv_tcb.tif', '*ftv_tcg.tif', '*ftv_tcw.tif',]):
    if len(fn) != 1:
      sys.exit('ERROR: There was no '+srch+' file in the folder selected.\nPlease fix this.') 
  
    tcb = tcbFtv[0]
    tcg = tcgFtv[0]
    tcw = tcwFtv[0]
    
  # figure out whta dirs are in the vidDir
  vidDirs = os.listdir(vidDir)  
  lenVids = len(vidDirs)
  outDir = os.path.join(vidDir, 'v'+'{:02}'.format(lenVids))
  outDirTmp = os.path.join(outDir, 'tmp')
  outDirFrames = os.path.join(outDir, 'frames')

  # make sure the outDir exists
  for thisDir in [outDir, outDirTmp, outDirFrames]:
    if not os.path.exists(thisDir):
      os.makedirs(thisDir)
       
  # write out the polygon
  outShape3857 = vector.replace('.shp','-EPSG3857.shp')
  if not os.path.exists(outShape3857):
    cmd = 'ogr2ogr -t_srs EPSG:3857 '+outShape3857+" "+vector
    subprocess.call(cmd, shell=True)

  # get the boundring coords plus buffer
  vDriver = ogr.GetDriverByName("ESRI Shapefile")
  sSrc = vDriver.Open(outShape3857, 0)
  sLayer = sSrc.GetLayer()
  trgtDim = sLayer.GetExtent()
   
  # get lon and lat coords for use in leaflet placement
  ulWGS = transform_coords(target_srs, 'EPSG:4326', trgtDim[0], trgtDim[3])
  lrWGS = transform_coords(target_srs, 'EPSG:4326', trgtDim[1], trgtDim[2])
  print(ulWGS)
  print(lrWGS)
  te = '-te {} {} {} {} '.format(ulWGS[0], lrWGS[1], lrWGS[0], ulWGS[1])
  with open(os.path.join(outDir,'bounds.js'), "w") as js:
      js.write('var bounds = L.latLngBounds([['+str(ulWGS[1])+', '+str(ulWGS[0])+'], ['+str(lrWGS[1])+', '+str(lrWGS[0])+']]);')


  for fn in [tcb, tcg, tcw]:
    
    outFile = os.path.join(outDirTmp, os.path.splitext(os.path.basename(fn))[0] + '_small.tif')
    #cmd = 'gdalwarp -s_srs '+source_srs+' -t_srs '+target_srs+' -of GTiff -r near '+fn+' '+outFile
    #cmd = 'gdalwarp -t_srs '+target_srs+' -of GTiff -r near '+fn+' '+outFile
    cmd = 'gdalwarp -multi -t_srs '+target_srs+' -of GTiff -r near -te_srs '+te_srs+' '+te+fn+' '+outFile    
    print(cmd)
    subprocess.call(cmd, shell=True)
  
  # find the small files, get the dims, and read in the src   
  smallFiles = glob(os.path.join(outDirTmp,'*_small.tif'))
  smallFiles.sort()
  trgtDim = get_intersec(smallFiles)
  src_ds = gdal.Open(smallFiles[0])
  nBands = src_ds.RasterCount
  src_ds = None
  
  # below streches each image's band using the "scale_to_8bit_tc" function. 
  print('making RGB images')
  for band in range(nBands):
    band += 1
    r = scale_to_8bit_tc(get_band(smallFiles[0], trgtDim, band), 'b')
    g = scale_to_8bit_tc(get_band(smallFiles[1], trgtDim, band), 'g')
    b = scale_to_8bit_tc(get_band(smallFiles[2], trgtDim, band), 'w')
    a = np.add(np.add(r, g),b)
    a[np.where(a > 0)] = 255
    
    outFileTif = os.path.join(outDirTmp, 'tc_rgb_'+str(startYear+band-1)+'.tif')
    outFilePng = os.path.join(outDirFrames, 'tc_rgb_'+str(startYear+band-1)+'.png')
    write_bands(r, g, b, a, outFileTif, smallFiles[0], trgtDim)
    cmd = 'gdal_translate -of PNG '+outFileTif+' '+outFilePng
    print(cmd)
    subprocess.call(cmd, shell=True)

  # remove files and dirs    
  files = glob(os.path.join(outDirFrames,'*.aux.xml'))     
  for fn in files:
    os.remove(fn)
  
  files = glob(os.path.join(outDirTmp,'*'))     
  for fn in files:
    os.remove(fn)
  
  os.rmdir(outDirTmp)

  htmlO = os.path.join(scriptDname,'tc_time_series.html')
  htmlC = os.path.join(outDir,'tc_time_series.html')
  copyfile(htmlO, htmlC)

  
