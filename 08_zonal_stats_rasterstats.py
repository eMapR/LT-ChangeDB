# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 14:48:18 2018

@author: braatenj
"""


from rasterstats import zonal_stats



shpFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\polygon\band_9.shp"
rasterFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_idx_mag.tif"


stats = zonal_stats(shpFile, rasterFile, band=9,
                    stats=['min', 'max', 'mean', 'std', 'sum', 'count'])

stats[80]