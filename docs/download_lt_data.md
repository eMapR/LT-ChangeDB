---
title: Download LandTrendr Data from Google Drive
layout: default
has_children: false
nav_order: 12
---

# Download LandTrendr Data from Google Drive
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}

* TOC
{:toc}

Go to the Google Drive account associated with your Earth Engine account and find the folder that you specified for the 
`gDriveFolder` parameter when running LT-GEE. If the folder did not exist prior to running the script, the folder will be 
at the first level of the Google Drive directory. Open the folder and you should find .tif files, files associated with ESRI 
Shapefiles, and a .csv file. If your area of interest was large, there might be several .tif files for both *TSdata and *LTdata. 
If output files are large, GEE will divide them into a series of image chunks.

Download each file. Right click and select download. It’s recommended to highlight all the files that are not .tif and right 
click and select download, which will zip all the selected files and prompt a download. The .tif files should be downloaded 
individually, as it takes an incredibly long time to zip them all and download and usually it ends up missing some files. Once 
each file has finished downloading, find them on your computer and move them to the *\raster\prep\gee_chunks folder of your project 
directory. The files and folder structure should look like this:

```
Project Head (mora)
├───raster
│   ├───landtrendr
│   │   ├───change
│   │   └───segmentation
│   └───prep
│       └───gee_chunks
├───scripts
├───timesync
│   ├───prep
│   ├───raster
│   └───vector
├───vector
└───video
```


Note that you might have to allow popups in your browser to allow files to download. Go to browser settings and search for popup settings.

If any of the files from the Google Drive download were zipped for downloading make sure they are unzipped directly into the 
*\raster\prep\gee_chunks folder and the original .zip file deleted. The files in the *\raster\prep\gee_chunks folder should look 
like the following directory tree. If you have a large study area, then *LTdata* might have a series of files with number appended 
signifying various spatial subsets (chunks) of the raster. 

```
Project Head (mora)
└───raster
    ├───landtrendr
    └───prep
        └───gee_chunks
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-ClearPixelCount.tif
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.cpg
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.dbf
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.fix
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.prj
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.shp
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTaoi.shx
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-LTdata.tif
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-runInfo.csv
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.cpg
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.dbf
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.fix
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.prj
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.shp
                PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.shx
```
