---
title: Get Started
layout: default
has_children: false
nav_order: 2
---

# Get Started
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}


## Philosophy


## Function arguments 

EE-LCB is a function mapping focused module. Each in the module is function is named and can only accept
a single collection object as an argument. This is very limiting if there are other parameters that a
given function requires. A single global dictionary is used to define the properties of the collection 
being built. 


## About Landsat


## Banding naming convention


## Create a Landsat surface reflectance collection

```js
var props = {
  startYear: 1986,
  endYear: 2018,
  startDate: '06-15',
  endDate: '09-15',
  aoi: ee.Geometry.Point([-110.438,44.609]),
  cfmask: ['cloud', 'shadow', 'snow', 'water'],
  sensors: ['LT05', 'LE07', 'LC08'],
  includeSLCoff: 'true',
  exclude: [],
  harmonizeTo: 'LE07', // 'LC08' 
  resample: 'nearest-neighbor',
  compositeDate: '08-01'
};
```

```js
// load the EE-LCB module
var lcb = require('users/jstnbraaten/modules:ee-lcb.js'); 

// define some desired collection properties
var userProps = {
	startYear: 1984,
	endYear: 2018,
	startDate: '07-01',
	endDate: '09-01'
	cfmask: ['cloud', 'shadow']
}

// set module properties
lcb.setProps(userProps)

// gather desired images into a collection
var srCol = lcb.sr.gather()

print(srCol)
```



The most important thing about this module is the `props` dictionary.
The `props` dictionary is...



Most functions operate on a single ee.Image so that they can be easily mapped over an ee.ImageCollection.
They focus on a single task for maximum flexibility

They use a global dictionary with many properties, this allows for simply function mapping - all of the global properties
are exposed to a given function being mapped.

Function names generally follow a verb-noun pattern where camel case is used to concatenate words, 
where the first is always a verb is typically a noun or in some cases an adjective.
In some cases a third word is included.

Function are divided into several sub-modules based on Landsat data type. 

| Sub-module  | Applies to |
| :- | :- |
| ls   | All Landsat data |
| sr   | Landsat surface reflectance data |
| toa  | Landsat top of atmosphere |
| refl | SR and TOA reflectance |
| dn   | Landsat digital number |




The mosaic functions are intended to create annual mosaics - they will create a mosaic per year of all images included for each distinct year
in the collection - note that the program can handle inter-year collection requests - helpful in the southern hemisphere. 
If you want to "reduce" an entire collection, use the base
API collection reduction functions like `col.reduce(ee.Reducer.Mean())`







