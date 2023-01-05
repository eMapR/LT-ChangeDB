// ###############################################################################
// #### INPUTS ###################################################################
// ###############################################################################

// define external parameters
var featureCol = 'users/emaprlab/NCCN/mora_aoi_ltgee'; // provide the path to aoi asset
var featureKey = 'PARK_CODE'; // provide the feature attribute that will define the study area
var featureValue = 'MORA'; // what unique value from the above attribute field defines the study area
var runName = 'v01'; // a version name to identify the run; it should NOT include a dash/hyphen (-) 
var gDriveFolder = 'reflectance_ftv_test'; // what is the name of the Google Drive folder that you want the outputs placed in
var startYear = 2000; // what year do you want to start the time series 
var endYear = 2010; // what year do you want to end the time series
var startDay = '06-01'; // what should the beginning date of annual composite be | month-day 06-01
var endDay =   '09-30'; // what should the ending date of annual composite be | month-day 09-30
var index = 'NBR'; // select the index to run, option are: 'NBRz', Band5z, 'ENC'
var maskThese = ['cloud', 'shadow', 'snow']; // select classes to masks as a list of strings: 'cloud', 'shadow', 'snow', 'water'
var clip = 'true'; // should the outputs be clipped to the AOI (pixels outside of the aoi +300m buffer will be set to -9999) - defined by string: 'true' or 'false'

// define internal parameters - see LandTrendr segmentation parameters section of LT-ChangeDB guide
var runParams = { 
  maxSegments: 6,
  spikeThreshold: 0.9,
  vertexCountOvershoot: 3,
  preventOneYearRecovery: true,
  recoveryThreshold: 0.25,
  pvalThreshold: 0.05,
  bestModelProportion: 0.75,
  minObservationsNeeded: 6
};

// optional inputs
var outProj = 'EPSG:5070'; // what should the output projection be? 'EPSG:5070' is North American Albers
var affine = [30.0, 0, 15.0, 0, -30.0, 15.0]; // should center of pixel be tied to grid or corner - 15.0 is center, change to 0.0 for corner (15.0 aligns to NLCD products)
var options = {                            // options to exclude images
  'exclude':{
    'imgIds':[],                            // ...provide a list of image ids as an array
    'slcOff':false                          // ...include Landsat 7 scan line corrector off images (true or false)
  }
};

// ###############################################################################
// ###############################################################################
// ###############################################################################

// buffer the aoi 10 pixels to give consideration to mmu filter
var aoiBuffer = 300;

// load the LandTrendr library
var ltgee = require('users/emaprlab/NPS-LT-ChangeDB:Modules/LandTrendr.js'); 

// get geometry stuff
var aoi = ee.FeatureCollection(featureCol)
  .filter(ee.Filter.stringContains(featureKey, featureValue))
  .geometry()
  .buffer(aoiBuffer);

// make annual composite collections
var srCollection = ltgee.buildSRcollection(startYear, endYear, startDay, endDay, aoi, maskThese, options);
var ltCollection = ltgee.buildLTcollection(srCollection, index, []);

// make a list of images use to build collection
var srCollectionList = ltgee.getCollectionIDlist(startYear, endYear, startDay, endDay, aoi, options).get('idList');

// run landtrendr
runParams.timeSeries = ltCollection;
var ltResult = ee.Algorithms.TemporalSegmentation.LandTrendr(runParams);

// get the year array out for use in fitting reflectance
var lt = ltResult.select('LandTrendr');
var vertMask = lt.arraySlice(0, 3, 4);
var vertYears = lt.arraySlice(0, 0, 1).arrayMask(vertMask);

// make a reflectance source stack
var refl = srCollection.select(['B1','B2','B3','B4','B5','B7']);

// fit reflectance stack
var fittedRefl = ee.Algorithms.TemporalSegmentation.LandTrendrFit(refl, vertYears, runParams.spikeThreshold, runParams.minObservationsNeeded);

// get TC as annual bands stacks 
var ftvB1 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B1', true).round().toShort().unmask(-9999);
var ftvB2 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B2', true).round().toShort().unmask(-9999);
var ftvB3 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B3', true).round().toShort().unmask(-9999);
var ftvB4 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B4', true).round().toShort().unmask(-9999);
var ftvB5 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B5', true).round().toShort().unmask(-9999);
var ftvB7 = ltgee.getFittedData(fittedRefl, startYear, endYear, 'B7', true).round().toShort().unmask(-9999);

// optionally clip the data
if(clip == 'true'){
  ftvB1 = ftvB1.clip(aoi).unmask(-9999);
  ftvB2 = ftvB2.clip(aoi).unmask(-9999);
  ftvB3 = ftvB3.clip(aoi).unmask(-9999);
  ftvB4 = ftvB4.clip(aoi).unmask(-9999);
  ftvB5 = ftvB5.clip(aoi).unmask(-9999);
  ftvB7 = ftvB7.clip(aoi).unmask(-9999);
}

// make a dictionary of the run info
var runInfo = ee.Dictionary({
  'featureCol': featureCol, 
  'featureKey': featureKey,
  'featureValue': featureValue,
  'runName': runName,
  'gDriveFolder': gDriveFolder,
  'startYear': startYear,
  'endYear': endYear,
  'startDay': startDay,
  'endDay': endDay,
  'maskThese': maskThese,
  'segIndex': index,
  'maxSegments': runParams.maxSegments,
  'spikeThreshold': runParams.spikeThreshold,
  'vertexCountOvershoot': runParams.vertexCountOvershoot,
  'preventOneYearRecovery': runParams.preventOneYearRecovery,
  'recoveryThreshold': runParams.recoveryThreshold,
  'pvalThreshold': runParams.pvalThreshold,
  'bestModelProportion': runParams.bestModelProportion,
  'minObservationsNeeded': runParams.minObservationsNeeded,
  'noData': -9999,
  'srCollectionList': srCollectionList,
  'options': options
});
var runInfo = ee.FeatureCollection(ee.Feature(null, runInfo));

// export the run info.
Export.table.toDrive({
  collection: runInfo,
  description: 'reflectance-ftv-info',
  folder: gDriveFolder,
  fileNamePrefix: 'reflectance-ftv-info',
  fileFormat: 'CSV'
});

// export the data
Export.image.toDrive({
  'image': ftvB1, 
  'region': aoi, 
  'description': 'reflectance-ftv-b1', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b1', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

Export.image.toDrive({
  'image': ftvB2, 
  'region': aoi, 
  'description': 'reflectance-ftv-b2', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b2', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

Export.image.toDrive({
  'image': ftvB3, 
  'region': aoi, 
  'description': 'reflectance-ftv-b3', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b3', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

Export.image.toDrive({
  'image': ftvB4, 
  'region': aoi, 
  'description': 'reflectance-ftv-b4', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b4', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

Export.image.toDrive({
  'image': ftvB5, 
  'region': aoi, 
  'description': 'reflectance-ftv-b5', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b5', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

Export.image.toDrive({
  'image': ftvB7, 
  'region': aoi, 
  'description': 'reflectance-ftv-b7', 
  'folder': gDriveFolder, 
  'fileNamePrefix': 'reflectance-ftv-b7', 
  'crs': outProj, 
  'crsTransform': affine, 
  'maxPixels': 1e13
});

// export the buffered LT shapefile
Export.table.toDrive({
  collection: ee.FeatureCollection(aoi),
  description: 'reflectance-ftv-aoi',
  folder: gDriveFolder,
  fileNamePrefix: 'reflectance-ftv-aoi',
  fileFormat: 'SHP'
});

