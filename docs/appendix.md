---
title: Appendix
layout: default
has_children: false
nav_order: 14
---

# Appendix
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}

* TOC
{:toc}

## Segmentation Raster File Names and Definitions

|Filename|Description|
|--- |--- |
|*clear_pixel_count.tif|A raster that describes the number of pixels that were included in the calculation of the composite for a given pixel per year. There are as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order.|
|*ftv_tcb.tif|Annual time series of Tasseled Cap Brightness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order.|
|*ftv_tcg.tif|Annual time series of Tasseled Cap Greenness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order.|
|*ftv_tcw.tif|Annual time series of Tasseled Cap Wetness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order.|
|*ftv_tcb_delta.tif|A multi-band raster dataset that describes the Tasseled Cap Brightness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.|
|*ftv_tcg_delta.tif|A multi-band raster dataset that describes the Tasseled Cap Greenness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.|
|*ftv_tcw_delta.tif|A multi-band raster dataset that describes the Tasseled Cap Wetness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.|
|*seg_rmse.tif|A single band raster that describes the overall LandTrendr segmentation fit in terms of root mean square error to the original time series per pixel.|
|*vert_fit_idx.tif|A multi-band raster that describes the fitted vertex values for the LandTrendr segmentation index for each segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.|
|*vert_fit_tcb.tif|A multi-band raster that describes the fitted vertex values for Tasseled Cap Brightness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.|
|*vert_fit_tcg.tif|A multi-band raster that describes the fitted vertex values for Tasseled Cap Greenness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.|
|*vert_fit_tcw.tif|A multi-band raster that describes the fitted vertex values for Tasseled Cap Wetness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.|
|*vert_yrs.tif|A multi-band raster that describes the year of each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.|

## Annual Change Raster File Names and Definitions

These files are not really useful on their own. They are containers that make attributing change polygons with segment information efficient. They are multi-band GeoTIFF raster files with a band for each year that a change onset can be detected (changes cannot be detected until the second year of the time series). Each file describes some aspect of a change segment and correspond to each other. If for a given year and pixel, no change onset is detected, then the pixel value for the year/band across all files will be null. If, however, a change onset is detected for a given year/band the pixel across all files will be filled with attributes about the change, like, the year of change onset detection, the magnitude of change, the duration of change, the pre-change segment spectral value, and the post-change segment value. The spectral values include the index that LandTrendr segmented the time series on and tasseled cap brightness, greenness, and wetness (fit to the vertices of the the LandTrendr-segmented index). There is also a comma delimited file that describes this file that is used in the script 07_append_zonal_stats.py as a list of parameter arguments. It is described further in the [Attribute Controller](#heading=h.g06pygirthjs) section below.

|Filename|Description|
|--- |--- |
|*change_attributes.csv|A change polygon attribute control file. It contains a list of raster files that represent attributes to be summarized per polygon. It contains file paths  and arguments that instruct the program on how to handle the file. You can find more information about this file HERE|
|*change_dur.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the temporal duration (years) of a change segment identified as starting on a given year/band.|
|*change_idx_mag.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of the index that was used to segment the time series) of a change segment identified as starting on a given year/band.|
|*change_tcb_mag.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap brightness) of a change segment identified as starting on a given year/band.|
|*change_tcb_post.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap brightness) for the vertex defining the end of a change segment identified as starting on a given year/band.|
|*change_tcb_pre.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap brightness) for the vertex defining the start of a change segment identified as starting on a given year/band.|
|*change_tcg_mag.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap greenness) of a change segment identified as starting on a given year/band.|
|*change_tcg_post.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap greenness) for the vertex defining the end of a change segment identified as starting on a given year/band.|
|*change_tcg_pre.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap greenness) for the vertex defining the start of a change segment identified as starting on a given year/band.|
|*change_tcw_mag.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap wetness) of a change segment identified as starting on a given year/band.|
|*change_tcw_post.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap wetness) for the vertex defining the end of a change segment identified as starting on a given year/band.|
|*change_tcw_pre.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap wetness) for the vertex defining the start of a change segment identified as starting on a given year/band.|
|*change_yrs.tif|The values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the year that change onset was detected value for a change segment identified as starting on a given year/band.|

## Polygon Field Names and Definitions

Polygon attributes are defined in the *attributes.csv file found in the <project head>\vector\change\<run name> directory. During step 5 (script 05_extract_annual_change.py) it is copied to this location from the <project head>\raster\landTrendr\change\<run name> directory. It controls what get summarized for each polygon. By default, it is initially populated with information from segmentation, but you can add you own variables to the list, like elevation, slope, etc. 

### Attributes controller 

attributes.csv file column descriptions (no field names or header on the file)

|Column Number|Description|
|--- |--- |
|1|Raster attribute data source|
|2|Attribute field name (max 10 characters)|
|3|Code for whether variable is continuous (con) or categorical (cat)|
|4|A switch for how the variable should be handled. Generally, if you add your own variables, you’ll use static which means that the raster band does not change depending on what the change polygon year of detection is|
|5|A code what what the datatype is - integer (int) or float (float)|
|6|Which band to use. O mean that the band should be tied to yod, a barred series indicates bands past yod’s band, and a single value > 0 mean use that band number from the source|
|7|A boolean switch to turn the summary attribute on (1) or off (0). If off (0), then the attribute will not be included in the shapefile|

*attributes.csv attribute field name description  

|Attribute Code|Attribution description|Diagram Code|
|--- |--- |--- |
|yod|The year of disturbance detection|1|
|annualID|Sequential patch identification number per year. Values range from 1 to the total number of patches in a given year.|NA|
|index|The spectral index code from which LandTrendr spectral-temporal segmentation was based on|NA|
|uniqID|Unique polygon ID - Concatenation of index, yod, and annualID|NA|
|durMn|Change segment duration mean|3|
|durSd|Change segment duration standard deviation|3|
|idxMagMn|Spectral segmentation index change magnitude mean|2|
|idxMagSd|Spectral segmentation index change magnitude standard deviation|2|
|tcbMagMn|Tasseled cap brightness change magnitude mean|2|
|tcbidxMagSd|Tasseled cap brightness change magnitude standard deviation|2|
|tcgMagMn|Tasseled cap greenness change magnitude mean|2|
|tcgMagSd|Tasseled cap greenness change magnitude standard deviation|2|
|tcwMagMn|Tasseled cap greenness change magnitude mean|2|
|tcwMagSd|Tasseled cap greenness change magnitude standard deviation|2|
|idxPreMn|Spectral segmentation index pre-change mean|4|
|idxPreSd|Spectral segmentation index pre-change standard deviation|4|
|tcbPreMn|Tasseled cap brightness pre-change mean|4|
|tcbPreSd|Tasseled cap brightness pre-change standard deviation|4|
|tcgPreMn|Tasseled cap greenness pre-change mean|4|
|tcgPreSd|Tasseled cap greenness pre-change standard deviation|4|
|tcwPreMn|Tasseled cap wetness pre-change mean|4|
|tcwPreSd|Tasseled cap wetness pre-change standard deviation|4|
|tcbPstMn|Tasseled cap brightness post-change mean|5|
|tcbPstSd|Tasseled cap brightness post-change standard deviation|5|
|tcgPstMn|Tasseled cap greenness post-change mean|5|
|tcgPstSd|Tasseled cap greenness post-change standard deviation|5|
|tcwPstMn|Tasseled cap wetness post-change mean|5|
|tcwPstSd|Tasseled cap wetness post-change standard deviation|5|
|area|Patch area (meters square)|NA|
|perim|Patch perimeter (m)|NA|
|Shape|A measure of patch shape complexity (perimeter of patch divided by the perimeter of a circle with the same area as the patch)|NA|
|tcbPst--Mn|Tasseled cap brightness post-change xx years mean|6, 7, 8, 9|
|tcbPst--Sd|Tasseled cap brightness post-change xx years standard deviation|6, 7, 8, 9|
|tcgPst--Mn|Tasseled cap greenness post-change xx years mean|6, 7, 8, 9|
|tcgPst--Sd|Tasseled cap greenness post-change xx years standard deviation|6, 7, 8, 9|
|tcwPst--Mn|Tasseled cap greenness post-change xx years mean|6, 7, 8, 9|
|tcwPst--Sd|Tasseled cap greenness post-change xx years standard deviation|6, 7, 8, 9|



![image alt text](image_59.png)

Diagram of a segmented pixel time series showing the attributes regarding a segment of interest. Attributed codes are referenced in the above table: *attributes.csv attribute field name description  

[http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/](http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/)

[http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/spatialite_gui-4.3.0a-win-amd64.7z](http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/spatialite_gui-4.3.0a-win-amd64.7z)

SELECT *, ST_IsValidReason(geometry)

FROM dist1992

WHERE NOT ST_IsValid(geometry)
