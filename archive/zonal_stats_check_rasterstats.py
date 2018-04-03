# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 10:43:06 2018

@author: braatenj
"""

from rasterstats import zonal_stats

shpFile = r"D:\work\temp\junk\band6_1990_feature_15.shp"
rasterFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_idx_mag.tif"


stats = zonal_stats(shpFile, rasterFile, band=6,
                    stats=['count', 'sum', 'mean', 'median', 'std', 'min', 'max'])

stats[0]