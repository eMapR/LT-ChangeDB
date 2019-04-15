---
title: Generate LandTrendr Data
layout: default
has_children: false
nav_order: 11
---

# Generate LandTrendr Data
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}

* TOC
{:toc}

We’ll run LT-GEE (LandTrendr on Google Earth Engine) to segment a selected Landsat spectral time series band 
or index and then fit to the vertices that are identified, tasseled cap brightness, greenness, and wetness 
(Crist, 1985). All of the data necessary for populating an annual change database will be assembled in a 
single image with >100 bands that will be exported to the Google Drive account associated with your EE account 
and then downloaded locally.

1. Open the GEE [IDE](https://code.earthengine.google.com/) and expand the **user/emaprlab/NPS-LT-ChangeDB** 
repository in the **Scripts** tab found on the left panel. Note that the repository will be under your **Reader **directory.

![image alt text](image_45.png)

2. Copy the master **Get LT-ChangeDB Segmentation Data** script file found in the **Scripts** subfolder to 
the **LT-ChangeDB** folder you created in a previous step, so you can edit and save it (the master copy is 
read only and used as a template by everyone using this system). To copy the file: click, hold, and drag 
the file from **user/emaprlab/NPS-LT-ChangeDB:Scripts/** repository to your **LT-ChangeDB **folder.

![image alt text](image_46.png)

3. Click on the **Get LT-ChangeDB Segmentation Data** script file you just copied to your **LT-ChangeDB **folder. 
When it loads in the editor it will look like this:

![image alt text](image_47.png)

1. There are two sections to this script file: an **inputs** section and a **processing **section. You’ll edit 
the parameters in the **inputs **section to define the area to run LandTrendr on, over what period of years, 
over what season, what to mask, how to perform segmentation, and optionally set output coordinate reference 
information, as well as excluding images.

2. Edit the inputs as desired. Use the following tables of definitions to help you set the parameters.

## Collection building parameters

The following parameters control the building of annual image collections that are composited and provided 
as input to LandTrendr for spectral-temporal segmentation.

<table>
  <tr>
    <td>Parameter</td>
    <td>Type</td>
    <td>Definition</td>
  </tr>
  <tr>
    <td>featureCol*</td>
    <td>String</td>
    <td>The path to the area of interest file that was uploaded in a previous step. See the instructions* 
	below for identifying the path. </td>
  </tr>
  <tr>
    <td>featureKey</td>
    <td>String</td>
    <td>The feature attribute that will define the study area over which to run LandTrendr. A field name 
	from the attribute table of the uploaded shapefile. See Vector Setup section.</td>
  </tr>
  <tr>
    <td>featureValue</td>
    <td>String</td>
    <td>The value from the attribute field set as featureKey that defines  the study area over which to 
	run LandTrendr. See Vector Setup section. </td>
  </tr>
  <tr>
    <td>runName</td>
    <td>String</td>
    <td>A unique name for this LandTrendr/project run. Example 'v1' (you might want to try different parameters 
	sets, in which case you might have several versions: v1, v2, v3, etc). It should not contain any hyphens (-) 
	or special characters besides underscore (_).</td>
  </tr>
  <tr>
    <td>gDriveFolder</td>
    <td>gDriveFolder</td>
    <td>The name of the Google Drive folder that the resulting data will be sent to. If the folder does not 
	exist, it will be created on-the-fly. It will not write to subfolder of your Google Drive. The folder 
	with either be created at the first level or must exist at the first level.</td>
  </tr>
  <tr>
    <td>startYear </td>
    <td>Integer</td>
    <td>The start year of the annual time series over which LandTrendr will operate.</td>
  </tr>
  <tr>
    <td>endYear </td>
    <td>Integer</td>
    <td>The end year of the annual time series over which LandTrendr will operate.</td>
  </tr>
  <tr>
    <td>startDay </td>
    <td>String</td>
    <td>The minimum date in the desired seasonal range over which to generate annual composite. Formatted 
	as 'mm-dd'.</td>
  </tr>
  <tr>
    <td>endDay </td>
    <td>String</td>
    <td>The maximum date in the desired seasonal range over which to generate annual composite. Formatted 
	as 'mm-dd'.</td>
  </tr>
  <tr>
    <td>index </td>
    <td>String</td>
    <td>The spectral index or band from the list of index codes to be segmented by LandTrendr.</td>
  </tr>
  <tr>
    <td>maskThese</td>
    <td>List</td>
    <td>A list of strings that represent names of images features to mask. Features can include 'cloud', 
	'shadow', 'snow', 'water'.</td>
  </tr>
</table>


**FeatureCol* parameter: this is defined as the path to the shapefile asset you uploaded to GEE in a 
[previous step](#heading=h.qv236ea764hk). To get the path, open the **Assets **tab found in the left panel of 
the GEE IDE, click on the AOI file name you’d like to use, which will open up a metadata window, copy the **Table ID** 
and paste it as the **FeatureCol** parameter argument

![image alt text](image_48.png)

![image alt text](image_49.png)

### LandTrendr spectral indices

The following table lists the Landsat-based spectral indices and transformations that are available to run LandTrendr on.

|Code|Name|Disturbance delta|
|--- |--- |--- |
|NBR|Normalized Burn Ratio|-1|
|NDVI|Normalized Difference Vegetation Index|-1|
|NDSI|Normalized Difference Snow Index|-1|
|NDMI|Normalized Difference Moisture Index|???|
|TCB|Tasseled-Cap Brightness|1|
|TCG|Tasseled-Cap Greenness|-1|
|TCW|Tasseled-Cap Wetness|-1|
|TCA|Tasseled-Cap Angle|-1|
|B1|Thematic Mapper-equivalent Band 1|1|
|B2|Thematic Mapper-equivalent Band 2|1|
|B3|Thematic Mapper-equivalent Band 3|1|
|B4|Thematic Mapper-equivalent Band 4|-1|
|B5|Thematic Mapper-equivalent Band 5|1|
|B7|Thematic Mapper-equivalent Band 7|1|
|B5z|Thematic Mapper-equivalent Band 5 standardized to mean 0 and stdev 1|1|
|NBRz|Normalized Burn Ratio standardized to mean 0 and stdev 1|1|
|ENC|6 band composite - mean of z-score: [B5, B7, TCW, TCA, NDMI, NBR]|1|


## LandTrendr segmentation parameters

The following parameters control how LandTrendr performs spectral-temporal segmentation. Besides the following parameter 
definitions, more information and context can be found in the original paper describing LandTrendr 
([Kennedy et al, 2010](http://geotrendr.ceoas.oregonstate.edu/files/2015/05/Kennedy_etal2010.pdf))

|Parameter|Type|Default|Definition|
|--- |--- |--- |--- |
|maxSegments|Integer||Maximum number of segments to be fitted on the time series|
|spikeThreshold|Float|0.9|Threshold for dampening the spikes (1.0 means no dampening)|
|vertexCountOvershoot|Integer|3|The initial model can overshoot the maxSegments + 1 vertices by this amount. Later, it will be pruned down to maxSegments + 1|
|preventOneYearRecovery|Boolean|FALSE|Prevent segments that represent one year recoveries|
|recoveryThreshold|Float|0.25|If a segment has a recovery rate faster than 1/recoveryThreshold (in years), then the segment is disallowed|
|pvalThreshold|Float|0.1|If the p-value of the fitted model exceeds this threshold, then the current model is discarded and another one is fitted using the Levenberg-Marquardt optimizer|
|bestModelProportion|Float|1.25|Takes the model with most vertices that has a p-value that is at most this proportion away from the model with lowest p-value|
|minObservationsNeeded|Integer|6|Min observations needed to perform output fitting|


## Optional Parameters

|Parameter|Type|Definition|
|--- |--- |--- |
|outProj|String|The desired projection of the output GeoTIFFs defined as an EPSG code with the format ‘EPSG:####’. Master script defaults to Albers Equal Area Conic for North America|
|affine|List of floating point values|Option to define whether the pixel grid is tied to the center or corners of pixels. The third and sixth values determine the position. Use 15.0 to align center of pixels to the grid or 0.0 for pixel corners to be tied to the grid. The master script defaults to 15.0 (pixel center snaps to grid, which is what USGS NLCD products use).|
|options|Dictionary of options|An option to exclude images either by defining a list of image IDs and or excluding Landsat ETM+ scan line corrector off images(images with gaps in data). See the master script for an example of parameter structure. options.exclude.imgIds requires a list of image id strings (defaults to no image exclusion). options.exclude.slcOff requires a Boolean of either false or true for whether to exclude Landsat ETM+ SLC-off images (defualts to false). Image IDs can be obtained from the UI Image Screener app|


3. After all the parameters are set, hit the **Run** button at the top of the script panel of the GEE IDE. 
In a moment the **Tasks** tab in the right panel of the IDE will turn orange alerting you to jobs that need to 
be started (if it doesn’t appear to be working, be patience a couple minutes). Activate the **Tasks** tab and 
you should see six jobs that need to be started. The job names provide information about the LandTrendr run. 
The last file parts distinguish the type of data that will be generated from the GEE script and output to Google Drive.

![image alt text](image_50.png)

![image alt text](image_51.png)

The following sections describes what each job/file is.

## Output Description

### File name description key

Each file contains information about the LandTrendr run, both for your information and for the coming Python 
scripts to decide how to handle the various files. Therefore, you should not change files names. The files 
contain 8 pieces of information, each separated by a hyphen. The key below describes what each pieces represents.

File string part key: AA-BB-CC-DD-EE-FF-GG-HH

|File name part|Description|
|--- |--- |
|AA|featureKey (from the collection building parameters)|
|BB|featureValue (from the collection building parameters)|
|CC|index (from the collection building parameters)|
|DD|concatenation(startYear, endYear) format: yyyy|yyyy (from the collection building parameters)|
|EE|concatenation(startDay, endDay) format: mmdd|mmdd (from the collection building parameters)|
|FF|runName (from the collection building parameters)|
|GG|outProj (from the collection building parameters)|
|HH*|Data type, see next table (autogenerated)|


*The following table describes the six different data files that are generated 

|Data type|Description|
|--- |--- |
|ClearPixelCount|A multi-band GeoTIFF file that provides a count of the number of pixels that went into generating each annual composite.|
|TSdata|A multi-band GeoTIFF TimeSync-Legacy data stack.|
|LTdata|A multi-band GeoTIFF LandTrendr segmentation data stack.|
|TSaoi|A shapefile that defined the area run for TimeSync-Legacy data generation. It is buffed out a little from the original file and will be in the projection defined by the outProj parameter.|
|LTaoi|A shapefile that defined the area run for LandTrendr segmentation data generation. It is buffed out 300m (10 pixels) from the original file and will be in the projection defined by the outProj parameter.|
|runInfo|CSV file containing metadata about the LandTrendr run.|


1. Click the **Run **button following each job. After clicking **Run** on a job you’ll be prompted by a window 
asking you to confirm aspects of the job - click **Run**. Little gears will start to turn next to the jobs, 
indicating that the job is being processed. You can start all the jobs concurrently - no need to wait for one 
to finish before starting the next. 

![image alt text](image_52.png)

When the jobs finish, the job title box will turn blue and a check mark and time to completion will appear following. 
Wait until all jobs complete and then proceed to the next step of downloading the data. Each file type will be 
exported as either GeoTIFF, shapefile, or csv to the Google Drive folder you specified in the collection building parameters.

![image alt text](image_53.png)