---
title: Functions
layout: default
has_children: false
nav_order: 3
---

# Functions
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}

* TOC
{:toc}


## Set properties

### setProps(colProps)

&#10551; `dictionary`

Updates the "props" global dictionary with desired collection properties. Will print the
resulting "props" dictionary to the console.

| Param  | Type | Description |
| :- | :- | :- |
| colProps | `dictionary` | A dictionary specifying desired collection properties |

Example. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var colProps = {
  startYear: 2013,
  endYear: 2018,
  startDate: '07-01',
  endDate: '09-01',
  sensors: ['LC08'],
  aoi: ee.Geometry.Point([-110.438, 44.609])
}
lcb.setProps(colProps)
```


--------------------------------------------------------------------------------------------

## Collection building functions

### sr.gather() 

&#10551; `ee.ImageCollection`

Gathers Landsat images into a collection. In the case where *LC08* images are included with either *LT05* or *LE07* images,
all images will be standardized to include only reflectance and CFmask *pixel_qa* bands 
and band names will match the *LC08* convention. In all other cases the original band arrangement and names 
will remain.

| Param  | Type | Description |
| :- | :- | :- |
| props.startYear | `int` | Minimum year in the desired range of the collection |
| props.endYear | `int` | Maximum year in the desired range of the collection |
| props.startDate | `string` | Minimum calendar date of the collection as 'mm-dd' (inclusive) |
| props.endDate | `string` | Maximum calendar date of the collection as 'mm-dd' (exclusive) |
| props.aoi | `ee.Geometry` | Area of interest used to filter image collection by bounds |
| props.sensors: | `list` | A list of the sensors to include images from. Options: 'LT05, 'LE07', 'LC08' |

Example. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
// load EE-LCB module
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 

// define collection properties
var colProps = {
  startYear: 2013,
  endYear: 2018,
  startDate: '07-01',
  endDate: '09-01',
  aoi: ee.Geometry.Point([-110.438, 44.609])
  sensors: ['LC08'],
}

// set collection properties
lcb.setProps(colProps)

// gather images following collection properties into an ee.ImageCollection
var col = lcb.sr.gather()
```

--------------------------------------------------------------------------------------------

### sr.harmonize(img)

&#10551; `ee.Image`

Spectrally harmonize Landsat 5 and 7 to 8 or vise versa.

| Param  | Type | Description |
| :- | :- | :- |
| props.harmonizeTo | `string` | Options: 'LE07', 'LC08' |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var img = lcb.sr.getLT05img();
var imgHarmonized = lcb.sr.harmonize(img);
print(img);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getL578col()
var colHarmonized = col.map(lcb.sr.harmonize);                     
print(colHarmonized);
```

--------------------------------------------------------------------------------------------

### sr.standardizeBands(img)

&#10551; `ee.Image`

Standardizes image to include only reflectance and CFmask *pixel_qa* bands with 
names following the *LC08* convention.

| Param  | Type | Description |
| :- | :- | :- |
| img | `ee.image` | A Landsat surface reflectance image |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var img = lcb.sr.getLT05img();
var imgStandardized = lcb.sr.standardizeBands(img);
print(imgStandardized);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLT05col();
var colStandardized = col.map(lcb.sr.standardizeBands);                     
print(colStandardized);
```

--------------------------------------------------------------------------------------------

### sr.removeBandCFmask(img)

&#10551; `ee.Image`

Removes the CFmask *pixel_qa* bands from a Landsat surface reflectance image.

| Param  | Type | Description |
| :- | :- | :- |
| img | `ee.image` | A Landsat surface reflectance image |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var img = lcb.sr.getLC08img();
var imgNoCFmask = lcb.sr.removeBandCFmask(img);
print(imgNoCFmask);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colNoCFmask = col.map(lcb.sr.removeBandCFmask);                     
print(colNoCFmask);
```

--------------------------------------------------------------------------------------------

### sr.removeImageSLCoff(col)

&#10551; `ee.ImageCollection`

Removes LE07 scan line corrector (SLC)-off images from a Landsat surface reflectance image.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.image` | A Landsat surface reflectance collection |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var colProps = {
  startYear: 1999,
  endYear: 2005,
  startDate: '07-01',
  endDate: '09-01',
  sensors: ['LE07'],
  aoi: ee.Geometry.Point([-110.438, 44.609])
};
lcb.setProps(colProps);
var col = lcb.sr.gather();
var colNoSLCoff = lcb.sr.removeSLCoff(col);
print(colNoSLCoff);
```

--------------------------------------------------------------------------------------------

### sr.removeImageList(col)

&#10551; `ee.ImageCollection`

Removes images included in 'exclude' property of the collection properties dictionary.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.image` | A Landsat collection |
| props.exclude | `list` | A list of Landsat `system:index` strings |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var colProps = {
  exclude: ['LT05_038029_20000707']
};
lcb.setProps(colProps);
var col = lcb.sr.getLT05col();
print(col);
var colExclude = lcb.sr.removeImageList(col);
print(colExclude);
```

--------------------------------------------------------------------------------------------

## Transformation functions

--------------------------------------------------------------------------------------------

### addBandTC(img)

&#10551; `ee.Image`

Applies the Tasseled Cap transformation to a Landsat surface reflectance image and adds bands:
'TCB', 'TCG', 'TCW', 'TCA'.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var img = lcb.sr.getLC08img();
var imgTrans = lcb.sr.addBandTC(img);
print(imgTrans);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.addBandTC);
print(colMasked);
```

--------------------------------------------------------------------------------------------

### addBandNBR(img)

&#10551; `ee.Image`

Applies the Normalized Burn Ratio transformation to a Landsat surface reflectance image and adds bands:
'NBR'.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var img = lcb.sr.getLC08img();
var imgTrans = lcb.sr.addBandNBR(img);
print(imgTrans);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.addBandNBR);
print(colMasked);
```

--------------------------------------------------------------------------------------------

### addBandNDVI(img)

&#10551; `ee.Image`

Applies the Normalized Difference Vegetation Index transformation to a Landsat surface reflectance image and adds bands:
'NDVI'.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var img = lcb.sr.getLC08img();
var imgTrans = lcb.sr.addBandNDVI(img);
print(imgTrans);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.addBandNDVI);
print(colMasked);
```

--------------------------------------------------------------------------------------------

### addBandNDSI(img)

&#10551; `ee.Image`

Applies the Normalized Difference Snow Index transformation to a Landsat surface reflectance image and adds bands:
'NDSI'.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var img = lcb.sr.getLC08img();
var imgTrans = lcb.sr.addBandNDSI(img);
print(imgTrans);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.addBandNDSI);
print(colMasked);
```

--------------------------------------------------------------------------------------------

### addBandNDMI(img)

&#10551; `ee.Image`

Applies the Normalized Difference Moisture Index transformation to a Landsat surface reflectance image and adds bands:
'NDMI'.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var img = lcb.sr.getLC08img();
var imgTrans = lcb.sr.addBandNDMI(img);
print(imgTrans);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.addBandNDMI);
print(colMasked);
```



## Correction functions

### ??.correctTopoMinearat

### xx.correctSLCoff

--------------------------------------------------------------------------------------------

## Masking functions

### sr.maskCFmask(img)

&#10551; `ee.Image`

Applies CFmask cloud and shadow mask to a Landsat surface reflectance image.

| Param  | Type                | Description  |
| ------ | ------------------- | ------------ |
| img  | `ee.Image`| An ee.Image object  |
| props.mask | `list` | A list of elements to be masked out. Options:<br> 'cloud', 'shadow', 'water', 'snow' |

Example: apply to ee.Image. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var colProps = {
	mask: ['cloud', 'shadow', 'water', 'snow']
};
lcb.setProps(colProps);
var img = lcb.sr.getLC08img();
var imgMasked = lcb.sr.maskCFmask(img);
print(imgMasked);
```

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var colProps = {
	mask: ['cloud', 'shadow', 'water', 'snow']
};
lcb.setProps(colProps);
var col = lcb.sr.getLC08col();
var colMasked = col.map(lcb.sr.maskCFmask);
print(colMasked);
```




### sr.maskOutliers*

### sr.maskDiff

--------------------------------------------------------------------------------------------

## Collection assessment functions

--------------------------------------------------------------------------------------------

### sr.countValid

## Composite functions

### sr.mosaicMean(col)

&#10551; `ee.ImageCollection`

Reduce an image collection to annual mosaics by mean.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat surface reflectance image collection |
| props.compositeDate | `string` | Date to assign to annual mosaic images. Format: 'mm-dd' |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var mosCol = lcb.sr.mosaicMean(col);
print(mosCol);
```

--------------------------------------------------------------------------------------------

### sr.mosaicMedian(col)

&#10551; `ee.ImageCollection`

Reduce an image collection to annual mosaics by median.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat surface reflectance image collection |
| props.compositeDate | `string` | Date to assign to annual mosaic images. Format: 'mm-dd' |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var mosCol = lcb.sr.mosaicMedian(col);
print(mosCol);
```

--------------------------------------------------------------------------------------------

### sr.mosaicMin(col)

&#10551; `ee.ImageCollection`

Reduce an image collection to annual mosaics by minimum.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat surface reflectance image collection |
| props.compositeDate | `string` | Date to assign to annual mosaic images. Format: 'mm-dd' |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var mosCol = lcb.sr.mosaicMin(col);
print(mosCol);
```

--------------------------------------------------------------------------------------------

### sr.mosaicMax(col)

&#10551; `ee.ImageCollection`

Reduce an image collection to annual mosaics by minimum.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat surface reflectance image collection |
| props.compositeDate | `string` | Date to assign to annual mosaic images. Format: 'mm-dd' |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var col = lcb.sr.getLC08col();
var mosCol = lcb.sr.mosaicMax(col);
print(mosCol);
```

--------------------------------------------------------------------------------------------

### ls.mosaicPath(col)

&#10551; `ee.ImageCollection`

Mosaics images from the same WRS-2 path and date.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat image collection |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
var colProps = {
	startYear: 2018,
	endYear: 2018,
	startDate: '07-01',
	endDate: '09-01',
	sensors: ['LC08'],
	aoi: ee.Geometry.Polygon(
        [[[-115.73283108195818, 47.0864041328592],
          [-115.73283108195818, 40.76536820958065],
          [-106.37247951945818, 40.76536820958065],
          [-106.37247951945818, 47.0864041328592]]])
};
lcb.setProps(colProps);
var col = lcb.sr.gather();
var colMos = lcb.ls.mosaicPath(col);
print(colMos);
Map.addLayer(colMos.filter(ee.Filter.eq('distinct_path', '038_20180709')));
```

--------------------------------------------------------------------------------------------

### xx.mosaicMedoid(col)

&#10551; `ee.ImageCollection`

Reduce an image collection to annual mosaics by minimum.

| Param  | Type | Description |
| :- | :- | :- |
| col | `ee.ImageCollection` | A Landsat surface reflectance image collection |
| props.compositeDate | `string` | Date to assign to annual mosaic images. Format: 'mm-dd' |

Example: apply to ee.ImageCollection. [Try Live](http://example.com/)
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js');
lcb.setProps({compositeDate: '07-15'});
var col = lcb.sr.getLC08col()
  .map(lcb.sr.standardizeBands)
  .map(lcb.sr.removeBandCFmask)
  .map(lcb.sr.addBandNDVI);
var colMos = lcb.sr.mosaicMedoid(col);
print(colMos);
```

--------------------------------------------------------------------------------------------

### xx.mosaicTargetDOY

## Visualization

### sr.visualize654

&#10551; `ee.Image`

Creates a 8-bit RGB visualization image from Landsat 8 equivlent bands 6, 5, and 4 mapped to 
red, green, and blue, respectively.

Example: apply to ee.Image
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var rgbImg = lcb.sr.visualize654(lcb.sr.getLC08img();)
Map.addLayer(rgbImg);
```

Example: apply to ee.ImageCollection
{: .lh-tight .fs-2 }
```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var rgbCol = lcb.sr.getLC08col()
                   .map(lcb.sr.visualize654)
Map.addLayer(rgbCol.first());
```


### sr.visualize543

### sr.visualize432

### sr.visualizeTC

## Example datasets

### sr.getLT05img()

&#10551; `ee.Image`

Returns an example *LANDSAT/LT05/C01/T1_SR* image.

```js
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 
var img = lcb.sr.getLT05img()
print(img)
```

--------------------------------------------------------------------------------------------

### sr.getLE07img()

&#10551; `ee.Image`

Returns an example *LANDSAT/LE07/C01/T1_SR* image. Note that the images is SLC-off.

```js
lcb.sr.getLE07img()
```

--------------------------------------------------------------------------------------------

### sr.getLC08img()

&#10551; `ee.Image`

Returns an example *LANDSAT/LC08/C01/T1_SR* image.

```js
lcb.sr.getLC08img()
```

--------------------------------------------------------------------------------------------

### sr.getLT05col()

&#10551; `ee.ImageCollection`

Returns an example *LANDSAT/LT05/C01/T1_SR* image collection.

```js
lcb.sr.getLT05col()
```

--------------------------------------------------------------------------------------------

### sr.getLE07col()

&#10551; `ee.ImageCollection`

Returns an example *LANDSAT/LE07/C01/T1_SR* image collection. Note that the images are SLC-off.

```js
lcb.sr.getLE07col()
```

--------------------------------------------------------------------------------------------

### sr.getLC08col()

&#10551; `ee.ImageCollection`

Returns an example *LANDSAT/LC08/C01/T1_SR* image collection.

```js
lcb.sr.getLC08col()
```

--------------------------------------------------------------------------------------------

### sr.getL578col()

&#10551; `ee.ImageCollection`

Returns an example image collection with one entry from:
- *LANDSAT/LT05/C01/T1_SR*
- *LANDSAT/LE07/C01/T1_SR*
- *LANDSAT/LC08/C01/T1_SR*

```js
lcb.sr.getL578col()
```

--------------------------------------------------------------------------------------------
