1. LT Annual Change Guide

   Contents

   1. [About](#About)
   2. [Directory Setup](#LandTrendr)
   3. [LandTrendrPyEnv]()
   4. [Scripts]()
   5. [Project Setup]()
   6. [Dependency Check]()
   7. [Vector Setup]()
   8. [Google Earth Engine Setup]()
   9. [Vector Upload to Google Earth Engine]()
   10. [LandTrendr Parameter Testing]()
   11. [Generate LandTrendr Data]()
   12. [Download LandTrendr Data from Google Drive]()
   13. [Generate Annual Change Polygons]()
   14. [SQL Queries]()
   15. [Appendix]()

   ## <a name="About">About</a>

   This document describes a method to generate geospatial polygons of annual landscape change for a given region of Earth. Change is identified from an annual series of Landsat images whose spectral history is segmented and queried for durable change. Spectral-temporal segmentation is performed by the LandTrendr () algorithm. Raster-based change information is generated in Google Earth Engine, which is then downloaded to a local computer for further processing in Python to filter change of interest and convert raster data to polygon data. Polygons representing discrete patches of change occurring at an annual time step are aggregated into a large database and attributed with characteristics describing the start and end years of the change as well as spectral properties that can aid in automatically identifying change agents and for generating descriptive statistics that describe patterns and trends of change.

   ## <a name="LandTrendr">LandTrendr</a>

   Each pixel in an image time series has a story to tell, LandTrendr aims to tell them succinctly. Let’s look at an example; here we have a pixel intersecting Lon: -123.845, Lat: 45.889 from a conifer-dominated, industrial forest region of the Pacific Northwest, USA. At the beginning of its record, it was a mature, second-growth conifer stand, and for 17 years, little changed. Then, between the summers of 2000 and 2001 a service road was built through it, removing some of its vegetation. Over the next year it experienced a clearcut harvest, removing all of its remaining vegetation. For the last 14 years it has been regenerating. Most recently it was a closed canopy, maturing, conifer stand.
   ![img](https://lh5.googleusercontent.com/ROxY4bzDSvypd2K1__GxAj3xQIqMnSINVizk_OZrw4U4yX50rElt9o0-YX9T-19ZHYta5nE802hf6S6N2R1H-9VbC1TU-WS0AB4SxIOYjStQKMScUnOODtdGK-UAwNlKqgRkveUyQsNCeLtu-CMH-G9Kv5fGLW-G_xecko5neJCAUI1ptiUqdix71FtR)

   *Every pixel tells a story. Landsat provides a historical record of the character of landscapes. By extracting a single pixel from a time series of Landsat imagery, it is possible to recount the state and change of the features composing the 1-hectare area of a pixel through time. In this example, we analyze the history of a conifer forest pixel from an industrial forest region of the Pacific Northwest (USA) that experiences a period of relative stability, a dramatic, rapid loss of vegetation, and subsequent regeneration.* 

   The description of this example pixel’s history is of course abridged, and only conveys a moderate resolution perspective of state and change in forest character. The unabridged version of this pixel’s story includes many other small changes in the forest stand it represents, but given the precision of the satellite sensor and methods in processing, the provided description is the type of pixel history interpretation we are confident are represented well in the image time series. LandTrendr is a brevity algorithm that listens to the annual, verbose, noisy detail of a pixel’s story and writes an abridged version.

   In practice, LandTrendr takes a single point-of-view from a pixel’s spectral history, like a band or an index, and goes through a process to identify breakpoints separating periods of durable change or stability in spectral trajectory, and records the year that changes occurred. These breakpoints, defined by year and spectral index value, allow us to represent the spectral history of a pixel as a series of vertices bounding line segments.

   ![img](https://lh4.googleusercontent.com/5Qs9dkbWwoOZRaWCER52WRVydifinbnzbNhSdJbMnWxTFtDwZRHBJ_VNkUCmfHK-MvksaLfB8me4gi3B53QcwlBgwo3ZylfTx7miU1yBiYAJWqi7SymJabqTAzoZldXYpXNZKZKl4COtn1OcRA8p-g1xVYxNA8aSJ8LO0yTrj_oMomJrPUNkYM67FYxV)

   *LandTrendr pixel time series segmentation. Image data is reduced to a single band or spectral index and then divided into a series of straight line segments by breakpoint (vertex) identification.*

   There are two neat features that result from this segmented view of spectral history.

   1. The ability to interpolate new values for years between vertices.
   2. Simple geometry calculations on line segments provide information about distinct spectral epochs

   The ability to interpolate new values for years between vertices is very useful. It ensures that each observation is aligned to a trajectory consistent with where the pixel has been and where it is going. We can think of this as hindsight-enhanced image time series data. It has two practical utilities. It can fill in data from missing observations in the time series (masked because of cloud or shadow) and it maintains consistency in predictive mapping through time; e.g. an annual forest classification is not likely to bounce between mature and old-growth conifer because of minor differences in spectral reflectance from atmosphere or shadow difference.

   ![img](https://lh3.googleusercontent.com/-a_paiae4lqG-JnQi4brmjmXnFae8ksTrtR00lVSBW-h5EPb6m5czZFBObqoCcI4a9Y0mB7Qm3Pnj3WQ2uyOcqY-09MCkdGXqBG5kU1PCXeA4-2furFlcwOIc_H4nbH2OgD21nL948C_TYFe8g0ddFVgnO8IFw3js0KpSkwMWR1sSfNOuJF0hjk78aku)

   *Hindsight-enhanced image time series data. Identification of time series breakpoints or vertices, allows the observations between vertices to be interpolated, removing extraneous information and placing each observation in the context of the trajectory it is part of. This is useful in filling missing observations because of cloud and shadow, and makes for more consistent annual map prediction.* 

   Since breakpoints or vertices are defined by a year we also have the ability to impose breakpoints identified in one spectral band or index on any other. For instance, we can segment a pixel time series cast as Normalized Burn Ratio (NBR: [NIR-SWIR]/[NIR+SWIR]) to identify vertices, and then segment a short-wave infrared (SWIR) band based on the NBR-identified vertices.

   ![img](https://lh5.googleusercontent.com/yQGuJiTwcQlHqKyMHj1b9Goz8wExDg9HPzBXkptHDFTu5C9wlTqJpiivJN5HQGlQ8mJk9gLq-SwvjGx0nke6tE_ldBWFyGqAyYVN-85Rv1_nPQN6h9ZvYlteBUCUiIdDpg74xLbXdF-P6RVwLb1V1SV_08TU0k-9yawK_Jew7ZZAHQZ91dLrWYj480OV)

   *Impose the segmentation structure of one spectral representation on another. Here we have identified four breakpoints or vertices for a pixel time series using NBR, and then used the year of those vertices to segment and interpolate the values of a SWIR band time series for the same pixel.* 

   This is useful because we can make the whole data space for a pixel’s time series consistent relative to a single perspective and summarize starting, ending, and delta values for all spectral representations for the same temporal segments, which can be powerful predictors of land cover, agent of change, and state transitions.

   ![img](https://lh4.googleusercontent.com/OMlq2Je3VsjTEFEgnKMCzKfD7BC22P2vBjrppaXOWas-tiEOKS5LvGqy5uxVkkBnsbbhn2u8eecWZNLW68Ll1CtokQ2Rhdp76mgm9NUg3XLcj0lQvWE0LcHlqP3conONScdA1RB-My6fvlv4yhr04q9FgIoxOHmlYF1AV58vl8_9r6zhd4HAYnVe255X)

   *A stack of spectral representations can be standardized to the segmentation structure of a single spectral band or index. Here we are demonstrating the standardization of tasseled cap brightness, greenness, and wetness to the segmentation structure of NBR. This allows us to take advantage of multi-dimensional spectral space to describe the properties of spectral epochs and breakpoints to predict land cover, change process, and transitions from a consistent perspective (NBR).* 

   The second neat feature of a segmented world view of spectral history is that simple geometry calculations can summarize attributes of spectral epochs. Temporal duration and spectral magnitude can be calculated for each segment based on the vertex time and spectral dimensions. These attributes allow us to easily query the data about when changes occur, how frequently they occur, on average how long do they last, what is the average magnitude of disturbance (or recovery) segments, etc. We can also query information about adjacent segments to focal segments. For instance, we can ask, what it the average rate of recovery following a disturbance segment, or what was the trajectory of a pixel time series prior to disturbance segments that we’ve attributed to fire.

   ![img](https://lh3.googleusercontent.com/vspaEVNAwjxNMQf8aCcwUIYng-5IFS9ulgpccJCHO8eBgvmi65jj0f6kgvdMPUuA95YlcGZjn3tWn8w7fbhdOIO70EDqkaUoiTlKQwDyuB9vK6Dy1HhfMkyszEDYJ30QGaZE2H4PyCLGtpf1sL7CQi8uKlXMepv6foDvOl--kwHU_B1kHF90wdq1gRLJ)

   *Diagram of segment attributes. From these attributes we can summarize and query change per pixel over the landscape.* 

   ## <a name="LandTrendrPreprocessing">LandTrendr Preprocessing</a>

   LandTrendr segmentation and fitted spectral time series data are produced using the Google Earth Engine implementation of the LandTrendr spectral-temporal segmentation algorithm. For a given region, a collection of USGS surface reflectance images for user-defined annual date range is assembled. The collection includes images from TM, ETM+, and OLI sensors. Each image in the collection is optionally masked to exclude clouds, cloud shadows, snow, and water using the CFMASK algorithm, which is provided with the surface reflectance product. Additionally, OLI image bands 2, 3, 4, 5, 6 and 7 are transformed to the spectral properties of ETM+ bands 1, 2, 3, 4, 5 and 7, respectively, using slopes and intercepts from reduced major axis regressions reported in Table 2 of Roy et al, (year).

   Transforming OLI data to match ETM+ data permits inter-sensor compositing to reduce multiple observations per year to a single annual spectral value, which is a requirement of the LandTrendr algorithm. To calculate composites, a medoid approach is used: for a given image pixel, the medoid is the value for a given band that is numerically closest to the median of all corresponding pixels among images considered.

   Medoid compositing is performed for each year in the collection and includes images from any sensor contributing to the annual set of seasonal observations for the year being processed. The result is a single multi-band image, per year, free of clouds and cloud shadows, and represents median user-defined season surface reflectance. From these annual medoid composites, a selected spectral index or band is calculated and provided as the time series input to the LandTrendr algorithm.

   ## <a name="DirectorySetup">Directory Setup</a>

   There are three major directories that are required for the process of generating annual change polygons. 

   1. A programming environment directory
   2. A script directory
   3. A project directory

   All three directories could be created in a single parent folder or spread out among paths that make sense for your system (more on this in the following steps). For the purpose of this guide we’ll put all three directories in the same parent folder called **LandTrendrGEE**. We’ll put it directly under the C drive.
   If you have write privilege to the C drive, create a folder at this location: **C:\LandTrendrGEE**, if you don’t have write permission to this directory, choose a different location.You now should have a **LandTrendrGEE** folder somewhere on your computer. In the next few steps we’ll add the three major directories to it, making it look something like this:

   ```
   C:\LandTrendrGEE
         ├───**LandTrendrPyEnv**
         ├───**LT-ChangeDB**
         └───**projects**
                 ├───<*project head folder 1*>
                 ├───<*project head folder 2*>
                 └───<*etc*>Throughout 
   ```

   this demo I’ll be referring to this directory structure frequently. Blah blah blah

   ## <a name="pyenv">LandTrendrPyEnv</a>

   ### About

   After data is generated in Earth Engine, it is downloaded and processed further with a series of Python scripts. To ensure that you have the dependent libraries and that your current installation of Python for ArcGIS or other uses, is not altered, we’ve developed an independent Python environment for LandTrendr processing called **LandTrendrPyEnv**

   LandTrendrPyEnv is an isolated, independent Python programming environment that does not disrupt any other Python installation on your system or set any environmental variables. It contains only the Python libraries and dependencies that are required for running scripts for working with LandTrendr outputs from Google Earth Engine.

   LandTrendrPyEnv is distributed and installed as a windows 64-bit.exe. It basically unzips a bunch of folders and files into the a directory of your choice.

   It is accessed via a special command prompt that is started by opening a Windows batchfile - *Start_LandTrendrPyEnv.bat* This batchfile is included in the zipped directory that you’ll download in the following step.  

   ## Install LandTrendrPyEnv

   ### Downloading

   The *LandTrendrPyEnv* installer can be downloaded using this [FTP](https://github.com/eMapR/LT-ChangeDB/releases/download/v1.0/LandTrendrPyEnv-0.4-Windows-x86_64.exe)

   Visiting the link will prompt a download of the file - it will download to your Downloads directory or wherever you have set your browser to store downloaded files. 

   ### Installation walkthrough

   Find the file that you just downloaded (**LandTrendrPyEnv-0.4-Winddouble**) and double click on it to start the installation process. If you are concerned about the reversibility of this installation, don’t worry, there is an uninstaller included with the installation and the program it will not change anything about your system’s registry or environmental variables. The uninstaller can be found by going to the install/uninstall application on your system and searching for the Python installation of LandTrendrPyEnv.

   1. **Run the executable**
      You might be presented with a security warning. Allow the program to **Run**

   ![img](https://lh6.googleusercontent.com/AmD2jcvj05Po7zLsY9LGQ7nTg-NwDxhHSvJHjz4mMPKaw2crGP0KEvjaGar_YcpyHiU3NK45appYAC3sJEFO6RKSzyDcBnKu6FXxAf7UyepuiYJG_wQHL3QW-jjTW75GCjKgJOfNKnRhGx5NuMZmDgeX5SfQxN-GHj133BgyoLX8FoTyvbdrOrerHaWx)

   

   ![img](https://lh6.googleusercontent.com/v_y6RzJii7CDyLVHd8mql1r_Ows64etlqIqXcFo4iy-jcrNOeGwCBZGcYbm5ZZdXftUPLLKvXXWSUZdpPKsNW9L9f86NpdfN8fubtr6B_zoRpELbcucC0BQqg_ACKb6MPPYUpWTL4pv5f1pnhWhXcOucblyHXzEG6VZhaR2iGiYTJTKUEtGM5ggHIynq)

   ​								Click “More info” to reveal a “Run anyway” button. 

   2. **Start installation and agree to Conda terms**

   **![img](https://lh4.googleusercontent.com/JEEXMst1oSyyWotIpZK4jOfAK5xJ03Ta_d4UkskwSfLPnjkpXI_wRNFNj7_u3DySKWCP8w99767JLlWNJ8uz7TOeqqpDxe_-JelSoRHUk6mv8UozUJ_kHs6eI8ouRmRLcG2xhUxazKUCvOwFwAWW0TFpAwzzFnV32PYI76I0_bJ6gx52JYo5s1RfzMEa)**

   **![img](https://lh5.googleusercontent.com/ZQ1iFW19Z-NVt9q8rjGhAoB3uwFj91bACAmO9IinoPbSlDpiiS5twkQsgi6-JN-_Bxuzjz6noTEwcPVixMFu0mOKMUsb58oDdJ-38qAMhCKN7d0BX9bmLPHw8PfC8sDJdcBUxVFZNogaHB4f5utwKGJ8j4aoC33g9M6dcCQrcjEpfLA6Dy1rpcwwmtNO)**

   3. **Who to install for**
      1. Select: **“Just Me”**

   ![img](https://lh4.googleusercontent.com/KSSAsbDs3cTJVlUFedu4yhbIsbeinYUGOpdYp8VBmD9zuUL8OLTvE1fGq6K5UTQp9kGtMwIBV_ICUxptgLekdCKZm6p2piKc5Nuo-OAar3cuGHqeTSJe4rvcNg0T1ArM2_-LOFi-ponWiS9dpA_uwUQu3s2BZDTjyrCecjvMP0BcxJRyQ8XK5aEMJD7E)

   

   4.  **Where to install**

      

   As mentioned in the Directory Setup section, you can install this wherever you wish, but for the purpose of the guide, we’ll install it in the C:\*LandTrendrGEE* folder we created in the previous step. We want the program’s folder to be called *LandTrendrPyEnv.* So, putting putting the paths together we end up with an destination folder:

   C:\*LandTrendrGEE\LandTrendrPyEnv*

   Note that you should have write privilege to this path and that there should be no spaces in the path (don’t put it in “My Documents”, for instance). Enter the desired path as the destination folder in the setup prompt. Additionally, note or save the path to a text file or in a open Notepad window, because we need to set it as a variable in .bat file in a following step. Hit the **Next** button 

   ![img](https://lh5.googleusercontent.com/w26hcFu_VjwfvHovWI0UO72iO1WD_WI7AaW9vGPU309LCzgh65K3RMqF3f4G2HAWTzOhKJkQVZXTyUwwZVsIZP8x742AM0reIyy990erIi_lQplNUZJLt5rI7akIIkLMJod_HJUcltsqufg2ltVWTuDk4PFCzRaZs363vEil8RYTO1_5JJQOg3RTJazT)

   

   5. **Advanced options**
      Do not check either option

      ![img](https://lh3.googleusercontent.com/GaaCNyiehgihdnQ96qSFy1WKJjkzfjHZ1hnvaRSaQLfMQQWkTIkl7ICLJD3XelCtLZN3P_WML8dnqtm1npGqVkZTDxPJ_wSBKqT2msttMs9CuDuA0sOc2eB83ShkQxUL8yEduuwqhaHtx-DDWGD5ptYVZBzEFJq_1YreMDlKPnxXibVdXQuruGkGL7ep)

      Install starts

      ![img](https://lh6.googleusercontent.com/dNGTuSfGUXxsTBHmRLg3wnaqlLN1XdcAO-iztRtTT3bJPS4lSaYjIDAfylA8kgYed1f3rjsjHg4WMW7-vAtBqFACAVoQtRk3Vahl5CC0K0rXt3SUIH36oE8eQjEgwRm5K6rGMrgJAArrdcOMTCsfD1uUT1cjoSvzEiuJ4Ga1ZFAZGIc6BNp6PkXmkynx)

      Install completes

      ![img](https://lh3.googleusercontent.com/ugagw-9puyB8uW5dvgb7h4LcF56HaBlmJ_wiP9N5cVFHVC4NF-nnDFgVgXdYfzEGsccdC3_g5H6yKqN0fXCB3a5t-WrmAYbt27OX3voQsaBAP8SVfdF22Tnc2MDfjuPEhfn4fR59ywwIO7hyjFdiPalGywXRD_ZKwekVfFi2A63Ta4JxXLtfEZmL-w30)

You should now have a “LandTrendrPyEnv*”* folder where ever you set the destination folder. Look for the folder to verify its location. If you can’t find it, hit the Windows key and do a search for “LandTrendrPyEnv*”.* If it is not at the location, then you’ll need to uninstall and reinstall the program and make sure to set the Destination Folder correctly.

**DON’T PUT ANY FILES IN THIS** **LandTrendrPyEnv** **FOLDER, IF YOU EVER NEED TO UNINSTALL IT, IT MIGHT THINK THAT THERE IS A VIRUS ASSOCIATED WITH THE PROGRAM BECAUSE THERE ARE FILES NOT RECOGNIZED AS BEING INSTALLED BY THE INSTALLER OR CONDA. IF THIS HAPPENS IT MAY QUARANTINE THE PROGRAM AND YOU’LL NEED TO FIND THE FILES THAT WERE ADDED AND DELETE THEM BEFORE TRYING TO UNINSTALL AGAIN.
      
#### ** Uninstall LandTrendrPyEnv **

If you ever need to uninstall LandTrendrPyEnv you can use its uninstaller .exe within the LandTrendrPyEnv folder, or by going to the install/uninstall application on your system and searching for the Python installation of LandTrendrPyEnv. It will remove the LandTrendrPyEnv folder and all its contents from your system and remove it from the list of installed programs (it is recognized as a Python version)

#### Mac or Linux system (Anaconda)

If you are on a Mac or Linux system you won’t be able to install LandTrendrPyEnv because it os for Window OS only. However, you can replicate the environment through Anaconda instead. It is best to do everything through Anaconda Prompt (search your applications for it). We’ll create a new virtual environment, so that we don’t mess up any versioning in your base environment. We have a .yml file that contains a list of all the libraries and versions that have been tested. Here is how to set up the conda environment (LandTrendrPyEnv) 

1. Skip ahead to the [Scripts]() section and download the LT-ChangeDB program files. In the directory is a file called: LandTrendrPyEnv.yml.

      a. Once you have the file, note its full path and return here to step 2

2. Open Anaconda Prompt and enter the following lines to add required channels to your conda configuration file.
```
conda config --append channels https://conda.anaconda.org/conda-forge/
conda config --append channels http://repo.anaconda.com/pkgs/main/
conda config --append channels https://conda.anaconda.org/IOOS/
conda config --append channels https://conda.anaconda.org/conda-forge/label/broken
```  
3. Enter the following command to create LandTrendrPyEnv. Following the -f flag in the command is where you’ll enter the full path to the LandTrendrPyEnv.yml file
```
conda env create -n LandTrendrPyEnv -f C:\path\to\file\LandTrendrPyEnv.yml
```      
Hopefully this will work for you, if it doesn’t it will tell you that solving the environment failed. I’ve only tested this on a Windows machine - it could be possible that some versions of libraries are not available for all OS.

4. Activate the LandTrendrPyEnv - run the following script. You can use the tab key to autocomplete ‘LandTrendrPyEnv’ after typing a few letters. Whenever you are going to be running scripts from the LT-ChangeDB program, you need to start Anaconda Prompt and activate ‘LandTrendrPyEnv’ 
```
conda activate LandTrendrPyEnv
```
5. To deactivate ‘LandTrendrPyEnv’, close Anaconda Prompt or type:
```
conda deactivate
```
6. You might need to add some environmental variables to your system - hopefully since you are running through Anaconda Prompt that won’t be necessary.

If setting up the environment using the LandTrendrPyEnv.yml file failed, then at minimum you should create your own environment starting with python 2.7 and making sure you have

- pandas
- rasteriorasterstats
- shapely
- fiona
- gdal

NOTES:  REK attempted this on his Mac, and the .yml file caused all sorts of problems because it was looking for specific versions of the libraries that were not available in the OSX. So, an alternative: 
      conda create -n LandTrendrPyEnv python=2.7 gdal=2.1 pandas rasterio rasterstats shapely=1.6.4 fiona=1.7.9 ScriptsAboutAll of the local data processing (post-processing the raster change data obtained from Earth Engine) is done using Python. There are a series of Python scripts that automate much of the workflow. You need to download the scripts to your system. They are stored in a GitHub repository from which you can download a zipped folder that contains all necessary files. Get ScriptsVisit the following URL:
      [https://github.com/eMapR/LT-ChangeDB  ](https://github.com/eMapR/LT-ChangeDB)Download the reposility as a zip file 
      ![save image](https://lh6.googleusercontent.com/fvRsk9ysROABhY64s7nphiCXfbLgKz_fiHc_lidKseCJivs8aggDPLO5XmWKLrzISiYFMt5DMw79M6OKk6IgKEzE6DQQ5YA_jl9wAQluyA-RYGXAYI30RC5dgSh0jg8ieQ5HwEkN7XsnY_mERKXR91uxW6piFiKMrV9kFjJ5CBzlRyuRRCYHvUEa79cU)

   A file titled **LT-ChangeDB-master.zip** will be downloaded to your computer. Find the file in your **Downloads** directory or wherever you have your browser set to stored downloaded files.
   The files in this zip archive can be thought of as program files - the program **LT-ChangeDB** stands for LandTrendr Change Database. Unzip the **LT-ChangeDB-master.zip** file to the **LandTrendrGEE** folder that was set up in the [**Directory Setup**](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.7k7uc2kddhr9) section and rename the folder to **LT-ChangeDB**. You now should have a directory that looks similar to this:
   C:\LandTrendrGEE├───LandTrendrPyEnv└───LT-ChangeDB
   The contents of the **LT-ChangeDB** should look like this:
   C:\LandTrendrGEE\LT-ChangeDB│  01_dependency_check.py│  02_project_setup.py│  03_vector_setup.py│  04_unpack_lt_ee_data.py│  05_extract_annual_change.py│  06_make_polygons.py│  07_append_zonal_stats.py│  08_make_tc_video.py│  ltcdb.py│  ltcdb.pyc│  README.md│  Start_LandTrendrPyEnv.bat│  tc_time_series.html│└───LandTrendrPyEnv_setup
   These files need to stay together. Nothing from this folder should be modified and nothing should be added to this folder. When we run python commands to post-process LandTrendr data from GEE the command prompt will look to this folder to find scripts to run. It should be noted that is directory can be placed anywhere and be called anything, but for the purpose of standardizing this guide, it is being placed in the **LandTrendrGEE** folder at the same level as the **LandTrendrPyEnv** folder.Setting Up the LandTrendrPyEnv PromptA special command prompt is included in the **LT-ChangeDB** folder. This special prompt is opened by double clicking on the **Start_LandTrendrPyEnv.bat** file in the **LT-ChangeDB** folder from the above step (don’t start it yet). It is how we will run all the scripts in the **LT-ChangeDB** folder. It is special because it will only know about files in the **LandTrendrPyEnv** folder and **LT-ChangeDB** folder, and it does not add anything to your system’s environmental variables or registry - it is totally isolated from from other installs of python. However, for it to know about files in the **LandTrendrPyEnv** folder, we have to tell it where the folder is located on your system.
   Open the **Start_LandTrendrPyEnv.bat** file from the **LT-ChangeDB** folder in Microsoft WordPad for editing. You can try right clicking on the file and select WordPad as an option under “open with”, if given the option, or open the WordPad application and then open the file from within WordPad (you may have to set the file search to “All Documents (*.*)” in order to see the .bat file). Note that Notepad should not be used as a text editor in this case because it does not read the new line returns correctly. Notepad++ is a good alternative general purpose text editor that could be used as well, though it needs to be downloaded and installed.Edit the text area highlighted in blue in the figure below so that it is the path of the **LandTrendrPyEnv** installation folder. If there are any spaces in the path to the **LandTrendrPyEnv** installation folder, you should be able to enclose the path with double quotes (there seems to be some inconsistencies in success with using quotes among systems - it is best if the path has no spaces). Leave no space between the “=” sign and the path.
   **Start_LandTrendrPyEnv.bat** before editing:![img](https://lh6.googleusercontent.com/TJT9AzKN-CdKEFg_Gzi6IPWxdlQwCjHRG5nYn3hyJ9BkcsuhpuZZ8x-mFEPvX4K0Adyhpqv9ufaCSRgzOe5FUDJoy-9iX2AcwRJNCjUzHnug3MxF4Lw9sVbCdmJriC916Sn0mhJQ1KXcqArTD0g025TYKus4JUMsUdAzA6aBz6xx0lhx3Z9OhKfkT0k0)
   Reminder of the directory that we want the path to bolded:
   C:\LandTrendrGEE├───**LandTrendrPyEnv**└───LT-ChangeDB
   **Start_LandTrendrPyEnv.bat** after editing:![img](https://lh4.googleusercontent.com/tzXVFVknRm7iC7IhLLRJdUiGepleD-6krqf6t5iS2bRL_OVyZb44BT1wO9uMuTi8uosV4wuBuJbTZZST8hVosQwB9Naljjx271PJP0eX9sbjJdVNbby4bzpVZn299OhseOZCwpCvst0qdllw2lZ1f4azz87itFFJIbZFZnEnNSEJWU1OGk8wVHrg10o6)
   \3) Save the file to it original location and name - overwrite the original.
   Double click on the **Start_LandTrendrPyEnv.bat** file to start the **LandTrendrPyEnv Prompt**. You should get a window like the one below showing the current working directory. We’ll interact with it by typing python followed by the path to a script we want to execute.
   Here is what the **LandTrendrPyEnv Prompt** should look like once opened.![img](https://lh4.googleusercontent.com/sEyDnksPAxEeG1QzYwU8oGZpmgQ7wiyWXsLeyOCjk4UVakBKDfVyJVHNGK30vLEv0k7QBu5V7-9PrvUy3-6xIFfD59QiKtfI6RKtLexzPmiYhhE4dZteJCWNWQD1gIeUnrmFQs3eHI8vmS8scjNwt13SPEA3mv6M6OuYaJ6gct4bOkXoXXVsvrC8Q5d4)
   \4) Type python into the **LandTrendrPyEnv Prompt** to see if it can find the **LandTrendrPyEnv** Python install. If it worked, you’ll get a python command line:
   ![img](https://lh6.googleusercontent.com/_QAvew3Vb8eGGJDScnVDtNzIlk1itxD4qF49OHgGqIecquuyFnmtSuBCY2d67lOpFrfhbzkpeW9uRf6ZHQenrHwVGKVUYcWaqviZVnoCBKSwl4-eNkcsmb5JNo5MQnh6WlNwMdLhyBs7hVA9jbX9slprkmzqCvWx5AtU3qyCt0R-riL4M2WTAOLBPNsY)
   If something failed you’ll get a window that looks like this:
   ![img](https://lh6.googleusercontent.com/OyALw0sYv611AGU0H8rltguWXEn_rIecIgkPweLIx9ZbOGPIO-H3m9wp8VKyiTyLnGDuc3_sBJ2bKz0pPFIqgRF3lfJtei_zPAbGRYTGtO2359_liHxnwyhmBDuGUNK80GNxXWLv-p2ezQQElhtGllvFENlkH88LlE9jbU2rkxdGjpUXkwyCjEF6bdLX)
   If it did fail check all your paths - relocate the **LandTrendrPyEnv** install older and make sure that it matches exactly what you set as the LT_PY_ENV variable when editing the **Start_LandTrendrPyEnv.bat** file.Dependency CheckAboutTo ensure that **LandTrendrPyEnv** was installed correctly and contains the Python libraries required by **LT-ChangeDB** scripts, we can run a test to check.Check for required librariesWe check for libraries by running a script from the **LandTrendrPyEnv Prompt***.* We’ll run a script to test for dependencies. If the python command line is still open from the previous step (designated as: >>>), then type: exit() into the prompt and hit enter to close the python interpreter. Alternatively, close the **LandTrendrPyEnv Prompt** and open a new one by double-clicking the **Start_LandTrendrPyEnv.bat** file in the **LT-ChangeDB** folder.
   The script to test dependencies is called **01_dependency_check.py**. It is found in the **LT-ChangeDB** program files folder. To run it type python followed by a space in the command line of the **LandTrendrPyEnv Prompt** and then type 01 and hit the tab key to autocomplete the filename. If the file was not found by autocomplete, then drag the **01_dependency_check.py** file into the command line, which will append the file’s path to the current command. The command line should look similar to this now:
   **![img](https://lh3.googleusercontent.com/1tYd_BzaS4tH9tDb81kFQ-CzHRk29iTxZFDgzyG6P7URlj_9JQFvuBWNNn5Yhpb2hygyGGum9zatLsG33pUv7FImTMIaMC8kJk91XoW2ZY-nWnaEojjZemoEeBfxuRXeL0UI_aL4dyaNQMfEpLHQJg9YSvlv42YRUysiXOC0C1RFz7L8cEqwesIFWCsT)**
   Example: python 01_dependency_check.py (if autocomplete worked)...orExample: python C:\LandTrendrGEE\LT-ChangeDB\01_dependency_check.py
   Note that if your path has any spaces in it, the path in the command line should be enclosed by quotations, so that it is interpreted as a single string of text - this is only relevant if you manually type the script file name. Using either autocomplete or drag and drop will automatically add quotes if needed. See the following example where one of the folders is called “misc programs”, in which case quotations are needed around the entire file path
   Example: python "C:\misc programs\LT-ChangeDB\01_dependency_check.py"
   Before you hit enter, make sure that the prompt is the active application, if you drag in a file to the prompt, generally Windows Explorer is the active application, so just click on the top bar of the **LandTrendrPyEnv Prompt**, then hit the enter key to start the program.
   If everything is okay with dependencies you should get a message like this:
   ![img](https://lh5.googleusercontent.com/N7lHq1FbFxVLVwslB6MkBMNHjeS7W1yie-nsli0y1WQPOu72yutNJQzBjpVSpm3EOCKKcLUH05WG6qn_CH14oMwRRdvb_WJhAkZJZJxboEbzK-iPVTE_SMAUofrEZVKYrq7gmt4iQ5yhZiI-maGYVUeOjckUFzgONlxdgXx2dExPTN7sMQXsXwiGc3RR)
   Where it says that each library checked **is** installed. If there were any missing libraries, the message would read **is not** installed. Since this **LandTrendrPyEnv** is pre-packaged, there should be no problems, but this is just a good test of the system.
   If it fails on any library, contact Justin Braaten ([jstnbraaten@gmail.com](mailto:jstnbraaten@gmail.com)) to find out what to do.Project SetupAboutFor each discrete geographic region you want to assemble change data for, you need to create a new project directory. This project region folder will hold a series of subfolders that are created by a python script where all of the data from Earth Engine will go, as well as all the data generated from post-processing scripts. You can create this project folder anywhere on your system. For consistency in this guide, I’m going to put it inside the **LandTrendrGEE** folder that was described in the [**Directory Setup**](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.7k7uc2kddhr9) section.Create Project DirectoryMake a new folder on your system to hold **LT-ChangeDB** post-processing files. In this example, I make a parent **projects** folder in the **LandTrendrGEE** folder that will hold a series of separate regions. I manually create a new folder called **projects** and a subfolder for a project called **mora** (Mount Rainier). The following diagram shows my current directory structure - the bolded folders were just created.
   C:\LandTrendrGEE
   ├───LandTrendrPyEnv
   ├───LT-ChangeDB
   └───**projects**
     └───**mora**
   Create the project directory structure. Open **LandTrendrPyEnv Prompt** by double clicking on the **Start_LandTrendrPyEnv.bat** file in the **LT-ChangeDB** folder.
   Type python in the prompt followed by a space and then type 02 and hit the tab key to autocomplete the filename. If the file was not found by autocomplete, then drag in the **02_project_setup.py** file from the **LT-ChangeDB** folder. The command should look like this:
   Example of autocomplete:C:\LandTrendrGEE\LT-ChangeDB>python 02_preoject_setup.py
   Example of script path drag and dropC:\LandTrendrGEE\LT-ChangeDB>python C:\LandTrendrGEE\LT-ChangeDB\02_preoject_setup.py
   After hitting the enter key, a Windows Explorer popup will appear prompting you to “Select or create and select a project head folder” that will hold all the raster and vector data for a specific study area. The prompt should default to the top of all open applications windows. If it doesn’t, minimize other open windows until you see it.
   Navigate to the project folder, select it and press the OK button.
   ![img](https://lh5.googleusercontent.com/6dcycTO1Qe5UeI0HrgMRhEm8om28MG2Yctec5Kj6884FqyVl7P4Vl73cYkoGAx0oDEkNduBjLDf5FLYef_5JIbnfoGLVL-MpQeBWvQXCcAHkaww3-L3wZg9fEQbckNHuRbLOMMq5daNqUQSiZJH7t5dhuEsfzxdHBSjcOd5sFx2PLqR2KvxFDIww5AtT)

   The program will then generate a directory structure in the head project folder you selected that looks like this:
   Project Head (mora)
   ├───raster
   │  ├───landtrendr
   │  │  ├───change
   │  │  └───segmentation
   │  └───prep
   │    └───gee_chunks
   ├───scripts
   ├───timesync
   │  ├───prep
   │  ├───raster
   │  └───vector
   ├───vector
   └───video
   In the following steps these folders will be filled with files manually and automatically from Python scripts. Vector SetupAboutIn this step you’ll run a script to standardize an existing vector file that defines the boundary of your study area. The script will automatically create a new ESRI Shapefile projected to EPSG:4326 (WGS84 Lat Long) and zips it up with all the .shp sidecar files (.dbf, .prj, .shx). This zipped shapefile will be uploaded to Google Earth Engine and define the region that LandTrendr is run on.
   The vector file that you use can have a single feature (like a single park boundary) or multiple features (all park boundaries for a given network). In any case, each study region needs to be identifiable by a unique ID for a given attribute (we’ll refer to this as a key-value pair). In the vector file that I’m using for the demo, I have a single boundary for Mount Rainier. The **Key** attribute is “PARK_CODE” and the **Value** for the feature of interest is “MORA” ![img](https://lh3.googleusercontent.com/2-T7LJt5iV-eN22bagOR295ce2yybQUUe7FtDN_l7jZY7uQAvtgGtT1U0I5XY1NW10nvK9uxHiKEzFpEPuLQkl0h6_8fa0S5onD7HOwOZopSr5qOcD7z6xSXfQ5H_u-atkUMJKoMsA4Ba1YfSySeR4OZT5s442ybQ7GKscWgjlXqzSWK6aX0fYNCqG6X)Google Earth Engine will want a “key-value” pair to know what feature in the vector should be analyzed by LandTrendr. It is important that both the Key and the Value not have hyphens (-), underscores are fine. Hyphens are a reserved character for use in filename parsing in LT-ChangeDB scripts. The key and value of the feature in this project will appear in file names, so if there is a hyphen in either the Key or the Value, then the system will break. Before moving on make sure that you have an area of interest file that meets the requirements described here. Once you have a shapefile with a unique ID defined by a Key (attribute field name) and Value (attribute value for a given feature) then move to creating a version for use in Google Earth Engine.Create a Google Earth Engine AOI FileMove the area of interest (AOI) shapefile (described previously) and all of its associated files to the “**vector**” folder within your project head folder created in the previous [Project Setup](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.qtiyguaspsr0) section. 
   Project Head (mora)
   ├───raster
   │  ├───landtrendr
   │  │  ├───change
   │  │  └───segmentation
   │  └───prep
   │    └───gee_chunks
   ├───scripts
   ├───timesync
   │  ├───prep
   │  ├───raster
   │  └───**vector**
   ├───vector
   └───video
   Open **LandtrendrPyEnv prompt** and type python then leave a space and then drag in the file **03_vector_setup.py** or autocomplete on 03 and hit enter to run the script
   Example of autocomplete:C:\LandTrendrGEE\LT-ChangeDB>python 03_vector_setup.py
   Example of script path drag and dropC:\LandTrendrGEE\LT-ChangeDB>python C:\LandTrendrGEE\LT-ChangeDB\03_vector_setup.py
   A Windows Explorer prompt will appear requesting that you select the project head folder![img](https://lh4.googleusercontent.com/X7HKK3iIf5ixgqzaU73CEc8nAcXm8I5j8wa0t-1yxEifpM3rNXj0D-65VlZXoivMc3rpKMczNtsGZBlHh6ybBPJTtJo2FmvrOLwQWCdp5rqaW48_4ppAxXQxwKD9KUs4_n1pLJNtS0OPwtZcT02_DD-BHtCmvmdeFjPZgUV5Wbi08qjFEm8iY_ttDS0J)
   Navigate to the head project directory, select it and hit the OK button
   A second prompt will appear listing available *.shp files in the vector directory and requests that you select a *.shp file to prepare for GEE. Select the *.shp file that you want to represent the area of interest for this project.
   ![img](https://lh6.googleusercontent.com/tWdhbjmgptTMzj1FTIF530HT5zYttwQQ1yN_4jMTChLl0QmHi2pBTARi_N8pONAVTuA9y-pNpurNpTEugiLx_nrEQJTalQNIwEEFQFkU0EuQpLDCOwH23_bhQASBWpBGow1geuihLqW78b6aR1KEk2QacYylGePm11TXF3jF7ILywATHrK1rwtFIzuOM)
   The program will create a new shapefile that appends some information to the end of the original file name and then zips a copy for upload to Google Earth Engine. See the bolded files below. The zipped file (*.zip) will be uploaded to Google Earth Engine in a following step.
   Project Head (mora)
   ├───raster
   ├───scripts
   ├───timesync
   ├───vector
   │    mora_aoi.dbf
   │    mora_aoi.prj
   │    mora_aoi.shp
   │    mora_aoi.shx
   │    mora_aoi_ltgee.zip
   │    **mora_aoi_ltgee_epsg4326.dbf**
   │    **mora_aoi_ltgee_epsg4326.prj**
   │    **mora_aoi_ltgee_epsg4326.shp**
   │    **mora_aoi_ltgee_epsg4326.shx**
   │
   └───videoGoogle Earth Engine SetupAccessWe’ll be using [Google Earth Engine](https://earthengine.google.com/) (GEE) to run LandTrendr ([LT-GEE](https://github.com/eMapR/LT-GEE)). GEE requires that a Google-associated email account be granted access. If you don’t have GEE access you can request it here: https://signup.earthengine.google.com/#!/
   If you need to sign up, you’ll be asked what you intend to do with Earth Engine. I’ve not heard of anyone being denied access, but make your response compelling.
   We’ll be using the GEE JavaScript API. Here is a link to the API User Guide for reference: https://developers.google.com/earth-engine/
   The JavaScript GEE code editor (IDE) can be accessed here:https://code.earthengine.google.com/
   The first time you access the code editor, you will probably be prompted to setup a default user code repository. The eMapR lab default code repository, for instance, is *users/***emaprlab***/default*. The default code repository might be suggested from your email, however, you may need to, or optionally define it. If you are required or choose to define it, make it short and reasonably representative/descriptive of you as a user or organization - it likely has to be unique.
   ![img](https://lh5.googleusercontent.com/CWo9ZCs-8T1yTH2nnAS01jaFO5syjxFEKyAimgJjuChKp03p3BMqRsJmV_cuP4RM8P44_-uu70fAUhawcXiYkpspqU9NrWHQEKo3rSRsCklRj3zNfdq_gMCNlEels23cgt_-AliMv0FyLyQG8CM0bW2BWoNxya9hjZzhOeyxzLvPixumptwpSYCd-NZ1)ExplorationGet comfortable with the JavaScript GEE IDE, move panel sliders, click on tabs, expand script libraries and documentation. Within the **Script Manager** tab, expand the **Examples** repository and run through some of the example for Images, Image Collection, and Feature Collection.When working on examples, zoom, pan, and click (view the Inspector tab), and watch for things printed to the consoleAdd required repositoriesWe have a series of scripts and applications that you need to add to your GEE account. Visit these URL links to add required scripts to your GEE account:
   The following link adds generic scripts and functions for using LandTrendr to your script library. It will show up under your **Reader** repository under the **Scripts** tab in the left panel of the GEE IDEhttps://code.earthengine.google.com/?accept_repo=users/emaprlab/public
   The following link adds scripts and applications specific to NPS annual change mapping to your GEE script library. It will show up under either your **Reader** repository under the **Scripts** tab in the left panel of the GEE IDE.https://code.earthengine.google.com/?accept_repo=users/emaprlab/NPS-LT-ChangeDBVector Upload to Google Earth EngineIn the previous [Vector Setup](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.7ncjbx4zupdj) step we generated a zipped directory of a shapefile that defines the region of this project. Now we’ll upload that file as an asset to your GEE account so it can be used to define the area that LandTrendr should be run on. 
   GEE User Guide reference for importing vectors:https://developers.google.com/earth-engine/importingInstructionsIf not already open, open the GEE IDE: https://code.earthengine.google.com/. If not already signed in, you’ll be prompted to log in to your GEE account. 
   Once the IDE opens click on the **Assets** tab in the left panel to open the **Assets Manager**. If you’ve not uploaded assets previously, then you’ll be prompted to **Create Home Folder**
   ![img](https://lh4.googleusercontent.com/CTLsUtr1hNb3has4FJ1fkJ2PBeL_EIBiETlprUXpQxRG_wGGy-Q7LymCybw6ZIQBde0LYJn5ntJfBQtXjkDZEwhvMQLWw92XuUNMK9RYF91rtW417di4-8qDC1vaGknUoDASA34CC-Y1D-RfIAqpQ3WMLQbBZpK2UYfa8NLF6qN2TrjdLXD7dHy35H34)Click the button and you’ll be presented with a new window where you are to define the name of the home folder. I would provide the same name as your user name in the **Scripts** library. For instance the eMapR user name is “emaprlab” (from: *users/***emaprlab***/default)* so I entered “emaprlab” as my asset home folder. This is just for consistency - it doesn’t matter that much. Here is an example from Al Kirschbaum: ![img](https://lh5.googleusercontent.com/8KY4c7mW7MKFqIkjbURj1rAi2UKENP4MVi47Vr7O-lflsBx3fSi-M4u4h9Ee8pcITeO0pykrEt4yiWkHxm48TRKkJRFvWGpvk-t5UhDvv3uG9el0Dyk6uD-jnR8X2qBuGtLNmB24SchGNB6mJ3O5s3piwhy_nqEstNv5xCYIH1_Z5CDhcun9Mh5sxqKh)
   If you’ve just set up your GEE **Assets** folder, or it already exists, you should be able to Click the **New** button to release a drop down menu and then select **Table upload**
   ![save image](https://lh5.googleusercontent.com/BnF4ZaxKGF-b1gJbyCoo2a9flMfVKv42WL2MrUsIpF5ijXr0Qd_1d3RS4kYbIBGWK5euWjHbyk_EUSPJ_ohuDA0p4VKaKMtEmhGICPmn_LHLS0uXMaopimDmUDbch_u_jJAo6QAjhn5SmAAudey4iiUHxFNN6b2mVSuP5pOD5MfybcB39f1uhkZnQMZL)![save image](https://lh5.googleusercontent.com/TOYaziKaoSNV1kCW3APYGi8OD_6dhaH5GJ99IHDcYx_k00fL43sKSefBx42nzWL9fVo7iSfHcfInZba4wtnMlK55Oi91puPMpM4KHFzCStEuk-IkfMYvJlvjhwNIozKO03_2SywG_rHTOkWg6FmBc2Y48yRMm_s4AvHlb07tiXsiPTPnjZ7iN6VJXqNT)Select the .zip file from vector subfolder of the head project directory
   ![img](https://lh6.googleusercontent.com/GABr08RKNMpWXVuwykA6q4E-F3glfPZt32YfaRtjixJi2Vyjx9rFHBzYnItqvBVsJv38GbqXiD9_Yfu6AN0AN6koaTicecCfjK1rjVeiIRVNQ0GRHE7L2IxfYk95KIr-qQqi3aL22Lhvf-NuiFGc2l_GJdxtb3OajmK2lX3dCbcMNfSarTQY1uTucyqP)
   Optionally rename the file and hit OK
   ![save image](https://lh6.googleusercontent.com/BglRHBcKCbu7S5UN5HxST5vAda3wveQsT6cblw38EyugsH8fXY5mKHeKg8dQGKHGglL8EuWW5-YMgfWl36qGSUqWG2-hCabBvQrpuemSNhPztDONuRcnqfqqsr6ZKLB6krBCsEBgVgoR3BmjshaQLsagsosTuUYDzgTJesiz0ny8WcR2JagYMUXESjIe)
   An **Asset Ingestion** job, which can be monitored in the **Task Manager** found under the **Tasks** tab in the right panel of the GEE IDE, will start. If you don’t see the job, you may have to refresh the browser. In a few minutes the process should complete and you will see your region in the **Asset Manager** panel - if you don’t see it after the job completes, then refresh the assets and/or the browser.
   Job starts:
   ![img](https://lh4.googleusercontent.com/bdGluFoojMsIZy461svz2JMdyNvIN19zLheaFWDksQt7WUl5hgzJdgw-m2k39W37srsXIl6U1ERYtQUCqk7Lc-nSDK6wpFIs_cTV7J6S9oJU463yTl-zd9IDp2uZ0UpnyW8ALAyMSIG-HIdM3b5F7H2_fUmTdmSxL9ODJAy4o9vC4SbOc08Km1ivHvVd)
   Asset upload and ingestion completes:
   ![img](https://lh3.googleusercontent.com/8b4HAneO7wBIhObpZPCZOv58Vh_l-mGwsq3eeCZUPUunbifxY0IW16ua-uHsRR7YM2OEsA7oOMfLW_yvsFzQxVR-jLwG2ISJ10dsvbHb3kDBP3xgv-iBP2Tfl9WEi9V3SSBgdT8poArO8SQboNDK56GjKmgE8RzrbXjpfY-dnpKrgq7JJTmYVMVEi07h)
   If you get an error, contact Justin Braaten at jstnbraaten@gmail.comCreate an LT-ChangeDB script folderIn a following step you’ll be making a copy of a master script to generate segmentation data. You’ll need a place to put this script copy that is writable by you.
   Within the GEE IDE under the **Scripts** tab click on the **NEW** button to release a dropdown menu - select the **Folder** option
   ![save image](https://lh4.googleusercontent.com/Whffy210CpTiYc3GEjOAh0Hg7Ub1H1wC0MPLF0VAmNLWtyDpAOOdhYrHW2wMhDrjdcamd3_DbPRJ9Q5QgBRWl0oFMaU0VW8fVBc6mMmpUhHZiXZJ3ONTT8y1cF-0qUcm-9uhzZpTjoXjINWv8279kGmdZdl7EDFoPpj_XTAOamu7webup_MN-t9UNaCr)A new window will appear asking you to define the repository and the new folder’s name. In this example, the repository is selected as the default and we’ve named the new folder **LT-ChangeDB**. Hit the **OK** button when you’re done.
   ![save image](https://lh5.googleusercontent.com/xFgqxj2L3yS_8xegvVbkka2zUHIzMQQrY-qv6fNPHg7UcLAVezBgcHOHBGKOA04iKb7aOJcbAqv2wvUsq5EjPvxrOwqAQ3SRa5l0SOHyBUIh2ES7iHKrv-FSVqykn_jyoPm_CUfpcPCzLRoswuWuDLla-RqtKsJfj7dTm7vnx46hD6Ua3DK0FlbLTMtL)
   You’ll now see the new folder in the repository that you selected. This folder is where you’ll copy and save your personal scripts to.
   ![save image](https://lh3.googleusercontent.com/dGg9yith8lzYyG8uiadXOmeXwnkL2ibErU8jVRLNPsSPPPnyK8jNtjab2uUqAY6s7dcOcfCqHEucUK2aeTwgNVH5WiAFjSbNrDtBt-TRR_6phAZKHcEbnAAt4l640Vj4T3IXLQ_FsvVoMKs7O29fpeg3c3SF3gF9og7zffnfp82EleF8UYGs-j9VkV6m)

   

   LandTrendr Parameter TestingGEE has made it possible to pretty quickly do visual assessments of the effect of various LandTrendr parameter settings. There are two interfaces for testing and exploring parameters. There is :
   A time series profile application that shows the results of segmentation for a given pixel time seriesA greatest disturbance mapping application that shows disturbances for a given set of parameters.
   To access these applications make sure that you’ve added the [required repositories](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.ynfzhje5e82d). Open the GEE [IDE](https://code.earthengine.google.com/) and expand the **user/emaprlab/nps_annual_change** repository (possible that this name will change). Note that the repo might be under either **Reader or Writer.** ![img](https://lh6.googleusercontent.com/CVHEdkOVhS0TgZwhz5rdlwjVlJTEkfNlMaln5pxhYtgtaqzIdmub9UXN_1XRZ7Mq2_o-HKp3iHAK6CBh--QdXBgrcPJoflZYlV7nkdSofcq0YV_TSGigTFKo4XXEZLmYZ4eu0NNUy8GUk-GYXozQcNqCIi2DbUzIwVML-igAY6M52ihtZrWFabB0WXX2)Expand the repo and you’ll find files: 
   Get LandTrendr ChangeDB Segmentation DataUI LandTrendr Disturbance Mapper TESTINGUI LandTrendr Pixel Time Series Plot TESTING
   Clicking on a file will open it in the GEE IDE editor.Time Series Segmentation AppThe *UI LandTrendr Pixel Time Series Plotter* will plot the Landsat surface reflectance source and LandTrendr-fitted index for a selected pixel. The script is useful for simply exploring and visualizing the spectral-temporal space of a location, for comparing the effectiveness of a series of indices for identifying landscape change, and for parameterizing LandTrendr to work best for your study region.
   Click on the **UI LandTrendr Pixel Time Series Plot TESTING** file. It will open in the GEE IDE editor, click the **Run** button
   ![img](https://lh5.googleusercontent.com/mQ55I82G0yR_J-a2KorL2MUB4RU1iD-AM-qIP-OujCNrO77txJF7CtFifiw2kqZToObXsIEt___t1nG7qJtkG39m7KRfSZYO-d8bVraUYJqCaoX2gxS6eO1fc8M5N57lRIesMy7lCeS3_pXFUL4uWBj7PRfTwXY1Enc8ba5S_IYEIvuylSyaoPdUp2sC)
   A GUI will populate the Map window of the GEE IDE, drag the top of the Map panel to the top of the IDE so that it is as large as possible. It should now look like this:
   ![img](https://lh3.googleusercontent.com/17YlV__8VVfafTR7Slq5710AWnKcO3jvnTAomgPK9kLzeUp8kPziwiTkKw_97mCEZ5OMTDt6naARXLlDEXcd-ARavuXMWAzPNB-r3Woy2O6Xv7fSmO3-bGi1ewYWHo94ic1bJ2to26CUjMc5pYneX7X3RUtWTHV-b76FoR2u9YDvyZzLZkJhONbP6_6p)

   Here are some instructions for running the application:
   Click on the script to load it and then click the Run button to initialize the application.Drag the map panel to the top of the page for better viewing.Define a year range over which to generate annual surface reflectance composites.Define the date range over which to generate annual composites. The format is (month-day) with two digits for both month and day. Note that if your study area is in the southern hemisphere and you want to include dates that cross the year boundary to capture the summer season, this is not possible yet - it is on our list!Select [spectral indices and bands](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.x5i65rpzi1jj) to view. You can select one or many.Optionally define a pixel coordinate set to view the time series of, alternatively you’ll simply click on the map. Note that the coordinates are in units of latitude and longitude formatted as decimal degrees (WGS 84 EPSG:4326). Also note that when you click a point on the map, the coordinates of the point will populate these entry boxes.Define the LandTrendr segmentation parameters. See the [LT Parameters](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.w7mtxeya9mfh) section for definitions.Either click a location on the map or hit the Submit button. If you want to change anything about the run, but keep the coordinate that you clicked on, just make the changes and then hit the Submit button - the coordinates for the clicked location are saved to the pixel coordinates input boxes.Wait a minute or two and plots of source and LandTrendr-fitted time series data will appear for all the indices you selected. The next time you click a point or submit the inputs, any current plots will be cleared and the new set will be displayed.
   Here we see forest decline near on Hurricane Ridge in Olympic National Park from three different indices![img](https://lh6.googleusercontent.com/0UhEuu2AZnFgJBrwDaEK1JlRlX5RXQQl4rByyBh6TGQnuD396SzXjsPVcQzD6nzkKG_c3sBsmqxPzILxdyoh9Xfv5iZ7NiB9kgyfmdZrtjOUpnEiRsdznOi9UubgeOI-SUd5UdVHIpm2AwdK_1uoXdcvD3Y_Gu5XnoDhSbN8aGdb8aVS0utQsdIrsh_P)Try different combinations of parameters on points of interest, save screenshots showing parameters and LT fits and compare them to find the best parameters and index for your project.
   Greatest Disturbance Mapping App


   The *UI LandTrendr Disturbance Mapper* will display map layers of disturbance attributes including: year of disturbance detection, magnitude of disturbance, duration of disturbance, and pre-disturbance spectral value.
   Click on the **UI LandTrendr Disturbance Mapper TESTING** file. It will open in the GEE IDE editor, click the **Run** button
   **![img](https://lh3.googleusercontent.com/bBTsFlagw4VFWEMYWbkAJmsxWdty2WYUQXS0UlcVC1NxUzZzTUT-48dXU77Sa_X56IU_wXPUM3OkF2ue8LkaBC0Hm5s19TW1ZBHX1NcDCs_bEXhKspWwexTDPKVuIAjjU0gWV5p-w6D38tNQoQsqftoUgyaQQQ55eMFEPXlBzZPNHOLvE-6rlQLh-17Y)**
   A GUI will populate the Map window of the GEE IDE, drag the top of the Map panel to the top of the IDE so that it is as large as possible. It should now look like this:
   **![img](https://lh4.googleusercontent.com/uV0WKBqyhpQD5e3lf7KPE8ccCA-4sEXtTs3sBdDmsL3ZK54jD7-nCmeAD0hgS_UlFp-7IANUkt0E4MXDU7PrztovMawqhX8u5Uls3mz4LcLu6tiVklNX09NLrtPrupURsz0QcIV6sFZm_teQDPwlybohxL2ClRwrK81WzKRWjFEcaGNNKWCkKYrovIWK)**
   Here are some instructions for running the application:
   Click on the script to load it and then click the Run button to initialize the application.Drag the map panel to the top of the page for better viewing.Define a year range over which to identify disturbances - best to set this close to the maximum range, you can filter disturbances by year in a different setting below.Define the date range over which to generate annual composites. The format is (month-day) with two digits for both month and day Note that if your study area is in the southern hemisphere and you want to include dates that cross the year boundary to capture the summer season, this is not possible yet - it is on our list!Select [spectral index or band](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.x5i65rpzi1jj) to use for disturbance detection.Optionally define a pixel coordinate set to define the center of the disturbance map, alternatively you’ll simply click on the map. Note that the coordinates are in units of latitude and longitude formatted as decimal degrees (WGS 84 EPSG:4326). Also note that when you click a point on the map, the coordinates of the point will populate these entry boxes.Define a buffer around the center point defined by a map click or provided in the latitude and longitude coordinate boxes from step 6. The units are in kilometers. It will draw and clip the map to the bounds of the square region created by the buffer around the point of interest.

   

   Define the disturbance type you are interested in - this applies only if there are multiple disturbances in a pixel time series. It is a relative qualifier among a series of disturbances for a pixel time series.Optionally filter disturbances by the year of detection. Adjust the sliders to constrain the results to a given range of years. The filter is only applied if the Filter by Year box is checked.Optionally filter disturbances by magnitude. Magnitude filtering is achieved by interpolation of a magnitude threshold from 1 year to 20 years. Define the magnitude threshold considered a disturbance for disturbances that are one year in duration and also 20 years in duration. If you want to apply the same threshold value across all durations, enter the same value in each box. The values should be the minimum spectral delta value that is considered a disturbance. They should be the absolute value and multiplied by 1000 for decimal-based surface reflectance bands and spectral indices (we multiply all the decimal-based data by 1000 so that we can convert the data type to signed 16-bit and retain some precision). The filter is only applied if the Filter by Magnitude box is checked.Optionally filter by pre-disturbance spectral value. This filter will limit the resulting disturbances by those that have a spectral value prior to the disturbance either greater/less than (depending on index) or equal to the defined value. The units are a of the spectral index selected for segmentation and should be scaled by 1000 (if you are you only want disturbances that had an NBR value of 0.4 prior to disturbance, you would set this parameter to 400). The filter is only applied if the Filter by Pre-Dist Value box is checked.Optionally filter by a minimum disturbance patch size, as defined by 8-neighbor connectivity of pixels having the same disturbance year of detection. The value is the minimum number of pixel in a patch. The filter is only applied if the Filter by MMU box is checked.Define the LandTrendr segmentation parameters. See the [LT Parameters](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.w7mtxeya9mfh) section for definitions.Inspector mode selector. In the center top of the map there is a check box for whether to interact with the map in Inspector mode or not. When inspector mode is activated, map clicks engage the GEE Inspector functionality so that you can explore map layer values for a point (see the Inspector tab). When deactivated, a map click will start mapping disturbances for the region surrounding the clicked point.Generate LandTrendr DataWe’ll run LT-GEE (LandTrendr on Google Earth Engine) to segment a selected Landsat spectral time series band or index and then fit to the vertices that are identified, tasseled cap brightness, greenness, and wetness (Crist, 1985). All of the data necessary for populating an annual change database will be assembled in a single image with >100 bands that will be exported to the Google Drive account associated with your EE account and then downloaded locally.
   Open the GEE [IDE](https://code.earthengine.google.com/) and expand the **user/emaprlab/NPS-LT-ChangeDB** repository in the **Scripts** tab found on the left panel. Note that the repository will be under your **Reader** directory.
   ![save image](https://lh6.googleusercontent.com/aQ8dnHoDKeEg1McuVXwgIUthz9tRpphIOfPz2ej7aJYo-iHZEsZW-um0dlLT-IbfFXMq6qNr_oXlfi4qcfscRk5dAzUDWbRQAVZCQElRyxtJVrWY0VyuKxvJ6Q8vyYN8B7G-Ovx5QqrqxjHRsE76Sx30UWlwvDBC7KjwdDQLkFStW84KZL5Wfdz7gy3Q)

   Copy the master **Get LT-ChangeDB Segmentation Data** script file found in the **Scripts** subfolder to the **LT-ChangeDB** folder you created in a previous step, so you can edit and save it (the master copy is read only and used as a template by everyone using this system). To copy the file: click, hold, and drag the file from **user/emaprlab/NPS-LT-ChangeDB:Scripts/** repository to your **LT-ChangeDB** folder.
   ![save image](https://lh4.googleusercontent.com/nwvx6o4dgsM6Tv-obSwbK-dvETuxKX1cAQjJYr51-6vIsmzwx-Uz1jCxCk95__oii-Q34bZLz0pSSF8J1if0dwhKIrorMxwb-4BBQOpqhtkd0vkbqAu8al8BVXo91L-jMM6Mxt_DhNdxfDIRf9InHZfTFzhX6EbVo1daYWQMIf7FuZBqJ-bpmWwhnPqz)

   Click on the **Get LT-ChangeDB Segmentation Data** script file you just copied to your **LT-ChangeDB** folder. When it loads in the editor it will look like this:
   ![save image](https://lh4.googleusercontent.com/Lf3v46xcGcI2tJsEv3DOl_FIBp590spAFU3XT9ZTG_UFWR3od3wvWk5eK_lNtF4PqaFq8BohOlTMZcy5i8xQhla28aCBoIk_ZItPefrJAkwHDa78Tgtf-VrKUNpMj70hyR4CPyhMk1Z2Vv9Yg3fPjQMkwyl5V0N8MdarfK8TEgt2LGOjfsJglZ4OCzO3)

   There are two sections to this script file: an **inputs** section and a **processing** section. You’ll edit the parameters in the **inputs** section to define the area to run LandTrendr on, over what period of years, over what season, what to mask, how to perform segmentation, and optionally set output coordinate reference information, as well as excluding images.Edit the inputs as desired. Use the following tables of definitions to help you set the parameters.Collection building parametersThe following parameters control the building of annual image collections that are composited and provided as input to LandTrendr for spectral-temporal segmentation.
   **Parameter****Type****Definition**featureCol*StringThe path to the area of interest file that was [uploaded in a previous step](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.v7dbl7hanw9i). See the instructions* below for identifying the path. featureKeyStringThe feature attribute that will define the study area over which to run LandTrendr. A field name from the attribute table of the uploaded shapefile. See [Vector Setup](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.7ncjbx4zupdj) section.featureValueStringThe value from the attribute field set as *featureKey* that defines the study area over which to run LandTrendr. See [Vector Setup](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.7ncjbx4zupdj) section. runNameStringA unique name for this LandTrendr/project run. Example 'v1' (you might want to try different parameters sets, in which case you might have several versions: v1, v2, v3, etc). It should not contain any hyphens (-) or special characters besides underscore (_).gDriveFoldergDriveFolderThe name of the Google Drive folder that the resulting data will be sent to. If the folder does not exist, it will be created on-the-fly. It will not write to subfolder of your Google Drive. The folder with either be created at the first level or must exist at the first level.startYear IntegerThe start year of the annual time series over which LandTrendr will operate.endYear IntegerThe end year of the annual time series over which LandTrendr will operate.startDay StringThe minimum date in the desired seasonal range over which to generate annual composite. Formatted as 'mm-dd'.endDay StringThe maximum date in the desired seasonal range over which to generate annual composite. Formatted as 'mm-dd'.index StringThe spectral index or band from the list of [index codes](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.x5i65rpzi1jj) to be segmented by LandTrendr.maskTheseListA list of strings that represent names of images features to mask. Features can include 'cloud', 'shadow', 'snow', 'water'.
   **FeatureCol* parameter: this is defined as the path to the shapefile asset you uploaded to GEE in a [previous step](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.qv236ea764hk). To get the path, open the **Assets** tab found in the left panel of the GEE IDE, click on the AOI file name you’d like to use, which will open up a metadata window, copy the **Table ID** and paste it as the **FeatureCol** parameter argument
   ![save image](https://lh3.googleusercontent.com/ZEqjR3lLQkQt3r6wYSEkJ9Z5LQVw39zfwMWNqcjxsBIu2WV8E8q89e-R4TNbM284a-tWoRqPeoM13lzdORqTiW6AsQQoQzvUr9MBBi56E6Rava8VOpdKgWhMeZCNMa-FJifGg8T-RD55HQ2AEAbSmblfTmkblIn2ScyGOTa7Nqq5R20bwKd4I-BnZiLZ)
   ![save image](https://lh6.googleusercontent.com/ZlhNj8vIaEVKl4ot9vXH2b5TTxjDemGDTyPQZYq02Ubu3DNV_87d5zkZE2mP9QpS7KE4K7dteQYLCaV4Be-ikZHrfCRx6J1BX3bbsorxjkU8CQBM4fIokE60zjCa1I0qhe3150RXyeTrSwqCoPwH6spcyHAXehv11kcvwo70Lt1tGf-6G-Mp6xGc_igB)LandTrendr spectral indicesThe following table lists the Landsat-based spectral indices and transformations that are available to run LandTrendr on.
   **Code****Name****Disturbance delta** NBRNormalized Burn Ratio-1NDVINormalized Difference Vegetation Index-1NDSINormalized Difference Snow Index-1NDMINormalized Difference Moisture Index???TCBTasseled-Cap Brightness1TCGTasseled-Cap Greenness-1TCWTasseled-Cap Wetness-1TCATasseled-Cap Angle-1B1Thematic Mapper-equivalent Band 11B2Thematic Mapper-equivalent Band 21B3Thematic Mapper-equivalent Band 31B4Thematic Mapper-equivalent Band 4-1B5Thematic Mapper-equivalent Band 51B7Thematic Mapper-equivalent Band 71B5zThematic Mapper-equivalent Band 5 standardized to mean 0 and stdev 11NBRzNormalized Burn Ratio standardized to mean 0 and stdev 11ENC6 band composite - mean of z-score: [B5, B7, TCW, TCA, NDMI, NBR]1LandTrendr segmentation parametersThe following parameters control how LandTrendr performs spectral-temporal segmentation. Besides the following parameter definitions, more information and context can be found in the original paper describing LandTrendr ([Kennedy et al, 2010](http://geotrendr.ceoas.oregonstate.edu/files/2015/05/Kennedy_etal2010.pdf))
   **Parameter****Type****Default****Definition**maxSegmentsInteger Maximum number of segments to be fitted on the time seriesspikeThresholdFloat0.9Threshold for dampening the spikes (1.0 means no dampening)vertexCountOvershootInteger3The initial model can overshoot the maxSegments + 1 vertices by this amount. Later, it will be pruned down to maxSegments + 1preventOneYearRecoveryBooleanFALSEPrevent segments that represent one year recoveriesrecoveryThresholdFloat0.25If a segment has a recovery rate faster than 1/recoveryThreshold (in years), then the segment is disallowedpvalThresholdFloat0.1If the p-value of the fitted model exceeds this threshold, then the current model is discarded and another one is fitted using the Levenberg-Marquardt optimizerbestModelProportionFloat1.25Takes the model with most vertices that has a p-value that is at most this proportion away from the model with lowest p-valueminObservationsNeededInteger6Min observations needed to perform output fitting
   Optional Parameters

   **Parameter****Type****Definition**outProjStringThe desired projection of the output GeoTIFFs defined as an EPSG code with the format ‘EPSG:####’. Master script defaults to Albers Equal Area Conic for North America affineList of floating point valuesOption to define whether the pixel grid is tied to the center or corners of pixels. The third and sixth values determine the position. Use 15.0 to align center of pixels to the grid or 0.0 for pixel corners to be tied to the grid. The master script defaults to 15.0 (pixel center snaps to grid, which is what USGS NLCD products use). optionsDictionary of options An option to exclude images either by defining a list of image IDs and or excluding Landsat ETM+ scan line corrector off images(images with gaps in data). See the master script for an example of parameter structure. options.exclude.imgIds requires a list of image id strings (defaults to no image exclusion). options.exclude.slcOff requires a Boolean of either false or true for whether to exclude Landsat ETM+ SLC-off images (defualts to false). Image IDs can be obtained from the **UI Image Screener** app 
   After all the parameters are set, hit the **Run** button at the top of the script panel of the GEE IDE. In a moment the **Tasks** tab in the right panel of the IDE will turn orange alerting you to jobs that need to be started (if it doesn’t appear to be working, be patience a couple minutes). Activate the **Tasks** tab and you should see six jobs that need to be started. The job names provide information about the LandTrendr run. The last file parts distinguish the type of data that will be generated from the GEE script and output to Google Drive.![save image](https://lh5.googleusercontent.com/FN4NKdswh5Zbe8U0NmChnPQqcDJkSrIGmZ9k5iXhe9T4NtpuNiFj3fLPuCf6_dVyae7CfVzsnA1kU0cMTsdLJjuAJ-MX1MGxBOrwJ8XL907VT2Lw4lmAE5pOiDEshzNducE0nQPDGfY6TL_d4XeewN4HG-VJtzDjc9Aq_sokpID5QfRkabohEfuRFAY2)
   ![save image](https://lh4.googleusercontent.com/c5YV15Q_UizQkS3boaElEVfI3MQfedK9ZvGNBtMKh0NvfEO6bsNPrLFezJGg7Sqb2ec_LAD-VDbkIRanOhXj7fo1yoRoNRMVGOBtXrlsR5wWvMO3TFzZnIt21PJZ6T6_VEQDi2wmQLKiEDwhADwMlxFDBfcoKgLNYV-iVcne5bswbPi505xDVoT5SiJ2)
   The following sections describes what each job/file is.Output DescriptionFile name description keyEach file contains information about the LandTrendr run, both for your information and for the coming Python scripts to decide how to handle the various files. Therefore, you should not change files names. The files contain 8 pieces of information, each separated by a hyphen. The key below describes what each pieces represents.
   File string part key: AA-BB-CC-DD-EE-FF-GG-HH
   **File name part****Description**AA*featureKey* (from the collection building parameters)BB*featureValue* (from the collection building parameters)CC*index* (from the collection building parameters)DDconcatenation(*startYear*, *endYear*) format: yyyy|yyyy (from the collection building parameters)EEconcatenation(*startDay*, *endDay*) format: mmdd|mmdd (from the collection building parameters)FF*runName* (from the collection building parameters)GG*outProj* (from the collection building parameters)HH*Data type, see next table (autogenerated)
   *The following table describes the six different data files that are generated Data type**Description**ClearPixelCountA multi-band GeoTIFF file that provides a count of the number of pixels that went into generating each annual composite.TSdataA multi-band GeoTIFF TimeSync-Legacy data stack.LTdataA multi-band GeoTIFF LandTrendr segmentation data stack.TSaoiA shapefile that defined the area run for TimeSync-Legacy data generation. It is buffed out a little from the original file and will be in the projection defined by the *outProj* parameter.LTaoiA shapefile that defined the area run for LandTrendr segmentation data generation. It is buffed out 300m (10 pixels) from the original file and will be in the projection defined by the *outProj* parameter.runInfoCSV file containing metadata about the LandTrendr run.
   Click the **Run** button following each job. After clicking **Run** on a job you’ll be prompted by a window asking you to confirm aspects of the job - click **Run**. Little gears will start to turn next to the jobs, indicating that the job is being processed. You can start all the jobs concurrently - no need to wait for one to finish before starting the next. 
   ![img](https://lh4.googleusercontent.com/ryQUdRtKjyILo4Bb-p3yorvUba7TlLRFKZ6eG5mva_1Sfb9lLkl1AiG-cgX_gNdzMJVPdLRjthe-QSVNPO8EmhDH3Ip-sVOEXZgpSo1Y4WmC050XfYR-Eg_sJHFNkxiaznVM9vHeK-NJ6MGo56CzqAgT91NWM1oQfh8lhZqclsV_YNnbTKlKrv6FnhUG)
   When the jobs finish, the job title box will turn blue and a check mark and time to completion will appear following. Wait until all jobs complete and then proceed to the next step of downloading the data. Each file type will be exported as either GeoTIFF, shapefile, or csv to the Google Drive folder you specified in the collection building parameters.
   ![save image](https://lh6.googleusercontent.com/nWu0ePFd2NeKNu6nLAwC_iYIEuGou4eNmj_k4k2kiwLzMzJpTHYZjqzb0AyvEUNoLS4BqbVRjbqCPKWBVuRQ3Mqafq7P9fLjObwUkRoR1HDjXECSuTvuijyJzQXeBFVtgytjk-VjQr-Y6h-q7ao6BTGekgsKOdvMbUeUI0me39grFBjofoHy5wnkyjNt)Download LandTrendr Data from Google DriveGo to the Google Drive account associated with your Earth Engine account and find the folder that you specified for the *gDriveFolder* parameter when running LT-GEE. If the folder did not exist prior to running the script, the folder will be at the first level of the Google Drive directory. Open the folder and you should find .tif files, files associated with ESRI Shapefiles, and a .csv file. If your area of interest was large, there might be several .tif files for both *TSdata and *LTdata. If output files are large, GEE will divide them into a series of image chunks.
   Download each file. Right click and select download. It’s recommended to highlight all the files that are not .tif and right click and select download, which will zip all the selected files and prompt a download. The .tif files should be downloaded individually, as it takes an incredibly long time to zip them all and download and usually it ends up missing some files. Once each file has finished downloading, find them on your computer and move them to the *\raster\prep\gee_chunks folder of your project directory. The files and folder structure should look like this:
   Project Head (mora)
   ├───raster
   │  ├───landtrendr
   │  │  ├───change
   │  │  └───segmentation
   │  └───prep
   │    └───gee_chunks
   ├───scripts
   ├───timesync
   │  ├───prep
   │  ├───raster
   │  └───vector
   ├───vector
   └───video
   Note that you might have to allow popups in your browser to allow files to download. Go to browser settings and search for popup settings.
   If any of the files from the Google Drive download were zipped for downloading make sure they are unzipped directly into the *\raster\prep\gee_chunks folder and the original .zip file deleted. The files in the *\raster\prep\gee_chunks folder should look like the following directory tree. If you have a large study area, then *LTdata* might have a series of files with number appended signifying various spatial subsets (chunks) of the raster. 
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
           PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-EPSG5070-TSaoi.shxGenerate Annual Change PolygonsUnpack Data from GEEOpen **LandTrendrPyEnv Prompt** by double clicking on the **Start_LandTrendrPyEnv.bat file** in the **LT-ChangeDB** **folder**.
   C:\LandTrendrGEE\LT-ChangeDB
     01_dependency_check.py
     02_project_setup.py
     03_vector_setup.py
     04_unpack_lt_ee_data.py
     05_extract_annual_change.py
     06_make_polygons.py
     07_append_zonal_stats.py
     08_make_tc_video.py
     ltcdb.py
     ltcdb.pyc
     README.md
     **Start_LandTrendrPyEnv.bat**
     tc_time_series.html
   Type python in the prompt followed by a space and then drag in the **04_unpack_lt_ee_data.py**  file from the **LT-ChangeDB folder** or type: 04 followed by the tab key to autocomplete find the file. The command should look like this:
   Example of autocomplete:C:\LandTrendrGEE\LT-ChangeDB>python 04_unpack_lt_ee_data.py

   Example of script path drag and dropC:\LandTrendrGEE\LT-ChangeDB>python C:\LandTrendrGEE\LT-ChangeDB\04_unpack_lt_ee_data.py


   Hit enter and you’ll be asked to navigate to the project head folder select the folder **bolded**:
   C:\LandTrendrGEE\LT-ChangeDB\projects\**mora**
   **Project Head (mora)**
   ├───raster
   │  ├───landtrendr
   │  │  ├───change
   │  │  └───segmentation
   │  └───prep
   │    └───gee_chunks
   ├───scripts
   ├───timesync
   │  ├───prep
   │  ├───raster
   │  └───vector
   ├───vector
   └───video
   ![img](https://lh5.googleusercontent.com/zR8CsHrTo5ziRhQ2BShbVSikCKsreMdg_OBQrF-ZWgQ8q2TqM8ybI7xaJkZ4M6frMU0T90MKWjgAVDeo5A9obD2OHWCVOa5_ivNCVVm4GQ0e31pn8CDEM52DtxD9fnExxuO3ZNXUAQBvj1XrEsShZhSxNc7p-nwBAdbIsBIRki0PknOmZR7HFNSe6lpz)

   After selecting a folder, the program will work to unpack all data downloaded from Google Drive. The command prompt will look like this:
   C:\LandTrendrGEE\LT-ChangeDB>python 04_unpack_lt_ee_data.py

   Working on LT run: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01
     Unpacking file:
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-vert_yrs.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-vert_fit_idx.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-seg_rmse.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcb.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcg.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcw.tif
     Unpacking file:
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-clear_pixel_count.tif
     Creating TC ftv delta data
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcb_delta.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcg_delta.tif
      PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-ftv_tcw_delta.tif
     Creating TC vert_fit data
      100% **done**
   Done!
   LT-GEE data unpacking took 4.8 minutes

   C:\LandTrendrGEE\LT-ChangeDB>

   The unpacked files will be placed in several subfolders of the project head folder. Files and some subfolders are named according to the file name given to the GEE output files ([File name description key](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.cikfk8fyn4aq)), excluding the projection. The major file types unpacked in the is step include: 
   **Run info file**: this is a .txt file that is placed directly inside the project head folder. It describes the LandTrendr run and includes all of the parameters used, as well as a list of all the images used to build the annual surface reflectance composites.**Segmentation files**: this set of files is unpacked into a subfolder of the *<project head>\raster\landtrendr\segmentation folder. They are output files from LandTrendr. Please see the [Segmentation Raster File Names and Definitions](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.no6fp058un2h) section for detail about the files. **Vector file**: A shapefile that defines the boundary of the area run by LandTrendr is placed inside of the *<project head>\vector folder. If the shapefile you uploaded to GEE contained more than one feature, this shapefile will only include the feature defined by the key-value pair given in the LandTrendr parameters and will be buffered by 300m to account for changes that occur at the boundary. **TimeSync files**: If you chose to export TimeSync files from GEE, then the unpacking script will move the TimeSync image files to the *<project head>\timesync\prep folder. It does not process them in this step, it simply moves them. It also places a shapefile in the *<project head>\timesync\vector folder. If the shapefile you uploaded to GEE contained more than one feature, this shapefile will only include the feature defined by the key-value pair given in the LandTrendr parameters. It represents the extent of the feature with a buffer 6300m to account the size of TimeSync image chip.
   What to do with the packaged LT-GEE files in the prep folder - the plan was to delete them after unpacking - do park folks want to archive them to an “~ltgeearchive” folder? Extract Annual Change as RastersType python in the prompt followed by a space and then drag in the **05_extract_annual_change.py file** from the **LT-ChangeDB folder** or type: 05 followed by the tab key to autocomplete find the file. The command should look like this:
   Example of autocomplete:C:\LandTrendrGEE\LT-ChangeDB>python 05_extract_annual_change.py

   Example of script path drag and dropC:\LandTrendrGEE\LT-ChangeDB>python C:\LandTrendrGEE\LT-ChangeDB\05_extract_annual_change.py

   After hitting the enter key, a Windows Explorer popup will appear prompting you to “Select the project head folder”. The prompt should default to the top of all open application windows. If it doesn’t, minimize other open windows until you see it.
   Generic example directory path to “project head folder”C:\LandTrendrGEE
   ├───LandTrendrPyEnv
   ├───LT-ChangeDB
   └───projects
     └───<**project head folder**>
   Example path following the “mora” demoC:\LandTrendrGEE\LT-ChangeDB\projects\**mora**
   After Selecting the project head folder the program will identify the LandTrendr run associated with the project, display its name and ask whether you would like to vegetation disturbance or growth. Type either **disturbance** or **growth** and hit enter.
   Here is what is shown in the command promptRegarding LT run: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01
   What change do you want to map (disturbance or growth)?:

   Next you’ll be asked to provide a minimum disturbance threshold. The value will be standard deviation times 1000. I’ve found that with the z-score indices (NBRz, Band5z, ENC) that 1.25 standard deviations seems like a pretty good threshold for minimum disturbance to consider. *Band5z* could maybe be a little greater like: 1.35-1.45. So go with a value of 1250 and see what happens.
   Regarding LT run: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01
   What is the desired minimum change magnitude:

   The progress will print to the consoleWorking on LT run: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01
     38% done

   The annual change rasters will be placed within a subfolder of the *<project_head>\raster\landtrendr\segmentation folder with the name equal to the LT-GEE job name plus the change type and the minimum magnitude threshold value, for example: PARK_CODE-MORA-NBRz-7-19842017-06010930-v01-disturbance_1250 
   These files are all related to the LandTrendr segmentation and fitting to vertex processes.
   Project Head├───raster  ├───landtrendr    ├───change\<job>\PARK_CODE-MORA-NBRz-7-19842017-06010930-change_attributes.csvPARK_CODE-MORA-NBRz-7-19842017-06010930-change_dur.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_idx_mag.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcb_mag.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcb_post.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcb_pre.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcg_mag.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcg_post.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcg_pre.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcw_mag.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcw_post.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_tcw_pre.tifPARK_CODE-MORA-NBRz-7-19842017-06010930-change_yrs.tif
   See the [Appendix](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.1vdzlzn7ka5p) for definitions of the filesMake Polygons from Annual RastersType python in the prompt followed by a space and then drag in the **06_make_polygons.py file** from the **LT-ChangeDB folder** or type: 06 followed by the tab key to autocomplete find the file. The command should look like this:
   Example of autocomplete:C:\LandTrendrGEE\LT-ChangeDB>python 06_make_polygons.py

   Example of script path drag and dropC:\LandTrendrGEE\LT-ChangeDB>python C:\LandTrendrGEE\LT-ChangeDB\python 06_make_polygons.py

   After hitting the enter key, a Windows Explorer popup will appear prompting you to “Select the project head folder”. The prompt should default to the top of all open application windows. If it doesn’t, minimize other open windows until you see it.
   Generic example directory path to “project head folder”C:\LandTrendrGEE
   ├───LandTrendrPyEnv
   ├───LT-ChangeDB
   └───projects
     └───<**project head folder**>
   Example path following the “mora” demoC:\LandTrendrGEE\LT-ChangeDB\projects\**mora**
   After you select the project head folder you’ll be presented with a list of raster change definitions that were generated in the previous step. You be asked to select which one to convert to polygons. Enter the number to the left of the change definition you want to convert.
   Here is the list of raster change definitions:
   1: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-disturbance_1250
   2: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-growth_1250

   Which one would you like to convert to polygons (enter the number):

   Next you’ll be asked to provide a minimum mapping unit. The value is the minimum number of connected pixels that define a patch (neighbor rule defined in next step). If you select 10, then patches with < 10 pixels will be ignored in conversion from raster to vector. We recommend using a MMU between 5-10 (9 is one hectare). You’ll likely want to try a few sizes to see what represents your landscape better and is a compromise between commission and omission error. 
   Regarding raster change definition: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-disturbance_1250
   What is the desired minimum mapping unit in pixels per patch:

   Next you’ll be asked to define the connectivity rule - 8 neighbor or 4 neighbor. If you want 8 neighbor type yes - if not type no
   Regarding raster change definition: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-disturbance_1250
   Should diagonal adjacency warrant pixel inclusion in patches? - yes or no:

   Progress will be printed
   Working on raster change definition: PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-disturbance_1250
     sieving to minimum mapping unit...
     making polygons from disturbance pixel patches...
       working on year: 1/32 (1986)
       working on year: 2/32 (1987)
       working on year: 3/32 (1988)
       working on year: 4/32 (1989)
       working on year: 5/32 (1990)
       working on year: 6/32 (1991)
       working on year: 7/32 (1992)
       working on year: 8/32 (1993)
       working on year: 9/32 (1994)
   The annual disturbance polygons will be placed within a sub-folder of the project_head\vector\change folder with the name equal to the LT-GEE job name. 
   C:\LandTrendrGEE\LandTrendrPyEnv\projects\<project head folder>
   └───vector
     └───change
       └───PARK_CODE-MORA-NBRz-7-19852017-06010930-v01-disturbance_1250-11mmu_8con
           _change_merged.dbf
           _change_merged.prj
           _change_merged.shp
           _change_merged.shx
           attributes.csv
           change_1986.dbf
           change_1986.prj
           change_1986.shp
           change_1986.shx
           change_1987.dbf
           change_1987.prj
           change_1987.shp
           change_1987.shx
           ...remaining years
           patches.tifPolygon AttributesIn step 5 (script 05_extract_annual_change.py) an *attributes.csv file was created and populated with a standard set of variables to summarize per polygon. This file was copied to the <head folder>\vector\<run name> dir. We can edit this file (either the source one or the one that was just copied) to either turn variable to be summarized off and on or add more variables to be summarized, like elevation, slope, ave precip, soil type, etc. More information about this file can be found in the [appendix](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.g06pygirthjs).Adding Attributes from other rastersYou can add other raster data (DEM, Slope, etc.) to the attributes of your polygons by following the steps laid out below.
   First, Download and add your TIF file to <directory header>/raster/prep/gee_chucks” You can download as dem from Google Earth Engine under reader as get DEM.
   Then go to <Project header>\raster\landtrendr\change\<job> where there is an Excel file. Open the excel file and it will look something like this.	![img](https://lh3.googleusercontent.com/rAAjFa_MguGxzr6qKhVkPlE_RfGQBL-x9xeLQgKUnj5WM5bq79Myk4ZVLhJqt4GWdwOSYBUoEqkvaZTeo5YYqBgYJG4-aOpFtdLoaWwR46YF9UT51ut1DQ-HjhoTdq2NAwN1eJs80NLL1utUpv8BjMiHCq0zfMcbZ4Zpw6V39DzJv1vM8hN21NydbZvn) In column A add the file path to the TIF file you added in step 1In column B add the name that you want to represent that field. (for a DEM use Elev for elevation or IR for infrared reflectance.)In column C add “con”. In column D add “static”.In column E add “int”In column F add the band number for the raster being used. If the raster has more than one band and you would like to add the attributes from the other bands to the polygons repeat steps 1 through 9 for each band. (example below)![img](https://lh3.googleusercontent.com/glB1HUoom0xm-mWOEFlPifDBoBi_UPtCLWWpmMsWNgQEyvVxuSg5mrOxs1Gs3bYhAMZimXXb-SHLOhWH7M8s27rwpW48pHQGRcNwJGw7MUp4QjszauiCPpdFTaZ3QC2W0IqjwUuueqTgppuH_e6wFALw3EkffOMuztm5M0Wnvo5QBWD0zu9GmkoRtCfn)In column G and a “1” or “0” to turn the attribute on or off. If it is off it will not be added.Once your done adding information to the table **SAVE** your changes and close the excel file and continue on.

   !!! Important !!!!!! Important !!!!!! Important !!!   For the meeting:Open the file that is similar to this on you system/project:
   <headFolder>\vector\change\PARK_CODE-MORA-NBRz-7-19842017-06010930-dist_info_11mmu_8con\PARK_CODE-MORA-NBRz-7-19842017-06010930-change_attributes.csv
   You can open it in Excel or a programming-friendly text editor (Justin uses notepad++)
   ![img](https://lh6.googleusercontent.com/ztvVjh-yfJpKepWrwXA2GDzvK2jGXKnWHE3CP20LrJhqZ70TfuwEHrEaECGwYWcyxBUOXsQTtWgyzhw7OrIBs9OP3DHT78X0_JsrCe_sML9EdW7yTbfyAV-XU_n3i12GhabB8d-jL7t4Yhu-CVAqthstnorNHpfixl2NnfRX2EEcRblTt2nWkplmLXrQ)
   Change the red circled 1’s to 0s and save the file (keep format as csv). This file controls how what is summarized for polygons. This 7th column is an on/off switch, we’re going to turn off summarizing these three attributes because they take hours to complete.Append Zonal Statistics to PolygonsType python in the prompt followed by a space and then drag in the *07_append_zonal_stats.py* file from the *LT-ChangeDB* folder or type: 07 followed by the tab key to autocomplete find the file. The command should look like this:
   ![img](https://lh4.googleusercontent.com/KsdHwLmENTmQn4i7CGPLn4_H77Wt-13wkw8T20HZqPaYUgStJi8v7HWdKJcJDQy8FZd1QzfQB3yZcmovrLf3IanfG2nJlB9gjvjdIJ7KqP2-Fq0QXBrPwUXfN9J8yY2uFkKiogNB99jjJAO4OJMpMpCE_tdVwslww_2hNdp_K9p5QSP-1KFMiRkhw2gu)
   Example: >python 07_append_zonal_stats.py (if autocomplete worked)...orExample: >python D:\work\programs\LT-ChangeDB\07_append_zonal_stats.py
   Hit enter and you’ll be asked to navigate to the project head folder.
   You will get an error that can be ignored - does not affect the outputs:
   *rasterstats\main.py:161: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated.
   The polygon files created in the previous step will be updated to include zonal summary stats for various attributes and two new files that are will be created, which are all of the individual year polygons merged into a single shapefile and a single spatialite geodatabase file 
   Project Head└───vector\change\<job>distall.dbfdistall.prjdistall.shpdistall.shx
   Project Head└───vector\change\<job>distall.sqlite
   TimeSync prep? Make TC video?SQL QueriesCreate a centroid shapefile for use in TimeSync
   SELECT ST_Centroid(geometry), uniqid, ST_x(ST_Centroid(geometry)) as x, ST_y(ST_Centroid(geometry)) as y FROM dist
   Add centroid xy to databaseSave the selection as a shapefile

   

   Find intersecting polygonsselect a.ogc_fid as a_ogc_fid, b.ogc_fid as b_ogc_fid
   From nbrz a, nbrz b
   where a.ogc_fid < b.ogc_fid and st_intersects(a.geometry, b.geometry)
   Select all polygons with a year of detection equal to 2000select * from nbrz where yod = 2000
   TODO: add a bunch more examples of queries
   Troubleshooting
   From command prompt, print environmental variables: set

   AppendixSegmentation Raster File Names and Definitions
   **Filename****Description***clear_pixel_count.tifA raster that describes the number of pixels that were included in the calculation of the composite for a given pixel per year. There are as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. *ftv_tcb.tifAnnual time series of Tasseled Cap Brightness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order.*ftv_tcg.tifAnnual time series of Tasseled Cap Greenness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. *ftv_tcw.tifAnnual time series of Tasseled Cap Wetness that has been fit to the vertices (ftv) of a given project’s LandTrendr segmentation per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. *ftv_tcb_delta.tifA multi-band raster dataset that describes the Tasseled Cap Brightness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.*ftv_tcg_delta.tifA multi-band raster dataset that describes the Tasseled Cap Greenness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.*ftv_tcw_delta.tifA multi-band raster dataset that describes the Tasseled Cap Wetness difference from the prior year to the current year per pixel. It has as many bands as there are years in the time series defined by the range inclusive of the startYear and endYear parameters. Band order from 1 to n corresponds to ascending year order. Note that the first year of the time series has no delta since we don’t know what the prior year’s values are.*seg_rmse.tifA single band raster that describes the overall LandTrendr segmentation fit in terms of root mean square error to the original time series per pixel.*vert_fit_idx.tifA multi-band raster that describes the fitted vertex values for the LandTrendr segmentation index for each segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.*vert_fit_tcb.tifA multi-band raster that describes the fitted vertex values for Tasseled Cap Brightness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.*vert_fit_tcg.tifA multi-band raster that describes the fitted vertex values for Tasseled Cap Greenness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.*vert_fit_tcw.tifA multi-band raster that describes the fitted vertex values for Tasseled Cap Wetness for each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0.*vert_yrs.tifA multi-band raster that describes the year of each LandTrendr segmentation vertex per pixel. There are as many bands as there are maximum vertices as defined by the maxSegments LandTrendr parameter plus 1. Null vertex slots are filled by 0. 

   Annual Change Raster File Names and Definitions
   These files are not really useful on their own. They are containers that make attributing change polygons with segment information efficient. They are multi-band GeoTIFF raster files with a band for each year that a change onset can be detected (changes cannot be detected until the second year of the time series). Each file describes some aspect of a change segment and correspond to each other. If for a given year and pixel, no change onset is detected, then the pixel value for the year/band across all files will be null. If, however, a change onset is detected for a given year/band the pixel across all files will be filled with attributes about the change, like, the year of change onset detection, the magnitude of change, the duration of change, the pre-change segment spectral value, and the post-change segment value. The spectral values include the index that LandTrendr segmented the time series on and tasseled cap brightness, greenness, and wetness (fit to the vertices of the the LandTrendr-segmented index). There is also a comma delimited file that describes this file that is used in the script 07_append_zonal_stats.py as a list of parameter arguments. It is described further in the [Attribute Controller](https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.g06pygirthjs) section below.

   **Filename****Description***change_attributes.csvA change polygon attribute control file. It contains a list of raster files that represent attributes to be summarized per polygon. It contains file paths and arguments that instruct the program on how to handle the file. You can find more information about this file HERE*change_dur.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the temporal duration (years) of a change segment identified as starting on a given year/band. *change_idx_mag.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of the index that was used to segment the time series) of a change segment identified as starting on a given year/band.*change_tcb_mag.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap brightness) of a change segment identified as starting on a given year/band.*change_tcb_post.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap brightness) for the vertex defining the end of a change segment identified as starting on a given year/band.*change_tcb_pre.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap brightness) for the vertex defining the start of a change segment identified as starting on a given year/band.*change_tcg_mag.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap greenness) of a change segment identified as starting on a given year/band.*change_tcg_post.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap greenness) for the vertex defining the end of a change segment identified as starting on a given year/band.*change_tcg_pre.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap greenness) for the vertex defining the start of a change segment identified as starting on a given year/band.*change_tcw_mag.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral delta (spectral change in units of tasseled cap wetness) of a change segment identified as starting on a given year/band.*change_tcw_post.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap wetness) for the vertex defining the end of a change segment identified as starting on a given year/band.*change_tcw_pre.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the spectral value (units of tasseled cap wetness) for the vertex defining the start of a change segment identified as starting on a given year/band.*change_yrs.tifThe values in each band are either null (if there was no change onset detected for a given pixel for a given year/band) or the year that change onset was detected value for a change segment identified as starting on a given year/band.
   Polygon Field Names and DefinitionsPolygon attributes are defined in the *attributes.csv file found in the <project head>\vector\change\<run name> directory. During step 5 (script 05_extract_annual_change.py) it is copied to this location from the <project head>\raster\landTrendr\change\<run name> directory. It controls what get summarized for each polygon. By default, it is initially populated with information from segmentation, but you can add you own variables to the list, like elevation, slope, etc. 
   Attributes controller attributes.csv file column descriptions (no field names or header on the file)**Column Number** **Description**1Raster attribute data source2Attribute field name (max 10 characters)3Code for whether variable is continuous (con) or categorical (cat)4A switch for how the variable should be handled. Generally, if you add your own variables, you’ll use static which means that the raster band does not change depending on what the change polygon year of detection is5A code what what the datatype is - integer (int) or float (float)6Which band to use. O mean that the band should be tied to yod, a barred series indicates bands past yod’s band, and a single value > 0 mean use that band number from the source 7A boolean switch to turn the summary attribute on (1) or off (0). If off (0), then the attribute will not be included in the shapefile 

   *attributes.csv attribute field name description **Attribute Code****Attribution description****Diagram Code**yodThe year of disturbance detection1annualIDSequential patch identification number per year. Values range from 1 to the total number of patches in a given year. NAindexThe spectral index code from which LandTrendr spectral-temporal segmentation was based onNAuniqIDUnique polygon ID - Concatenation of index, yod, and annualIDNAdurMnChange segment duration mean3durSdChange segment duration standard deviation3idxMagMnSpectral segmentation index change magnitude mean2idxMagSdSpectral segmentation index change magnitude standard deviation2tcbMagMnTasseled cap brightness change magnitude mean2tcbidxMagSdTasseled cap brightness change magnitude standard deviation2tcgMagMnTasseled cap greenness change magnitude mean2tcgMagSdTasseled cap greenness change magnitude standard deviation2tcwMagMnTasseled cap greenness change magnitude mean2tcwMagSdTasseled cap greenness change magnitude standard deviation2idxPreMnSpectral segmentation index pre-change mean4idxPreSdSpectral segmentation index pre-change standard deviation4tcbPreMnTasseled cap brightness pre-change mean4tcbPreSdTasseled cap brightness pre-change standard deviation4tcgPreMnTasseled cap greenness pre-change mean4tcgPreSdTasseled cap greenness pre-change standard deviation4tcwPreMnTasseled cap wetness pre-change mean4tcwPreSdTasseled cap wetness pre-change standard deviation4tcbPstMnTasseled cap brightness post-change mean5tcbPstSdTasseled cap brightness post-change standard deviation5tcgPstMnTasseled cap greenness post-change mean5tcgPstSdTasseled cap greenness post-change standard deviation5tcwPstMnTasseled cap wetness post-change mean5tcwPstSdTasseled cap wetness post-change standard deviation5areaPatch area (meters square)NAperimPatch perimeter (m)NAShapeA measure of patch shape complexity (perimeter of patch divided by the perimeter of a circle with the same area as the patch)NAtcbPst--MnTasseled cap brightness post-change xx years mean 6, 7, 8, 9tcbPst--SdTasseled cap brightness post-change xx years standard deviation6, 7, 8, 9tcgPst--MnTasseled cap greenness post-change xx years mean 6, 7, 8, 9tcgPst--SdTasseled cap greenness post-change xx years standard deviation6, 7, 8, 9tcwPst--MnTasseled cap greenness post-change xx years mean 6, 7, 8, 9tcwPst--SdTasseled cap greenness post-change xx years standard deviation6, 7, 8, 9

   ![img](https://lh3.googleusercontent.com/Dj7cL1gA1MjpAfaXfRlKjRHzhrJ-VQzuGswkOVfYVi-GhSDvJvim63bRNAzVWQg_FnshvGhNQQNMGBwxJkDgJ_qW7RniXy-DBttFfGdc7Gi1GWzaSl30Yo2-jO4Ct0cpqoVRVtIdiwV3HOBl29UflbBhfQr4G_OyVLJDFliKIrskIU63EbSEA3dgWCfn)Diagram of a segmented pixel time series showing the attributes regarding a segment of interest. Attributed codes are referenced in the above table: *attributes.csv attribute field name description 

   

   http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/http://www.gaia-gis.it/gaia-sins/windows-bin-amd64/spatialite_gui-4.3.0a-win-amd64.7z


   SELECT *, ST_IsValidReason(geometry)FROM dist1992WHERE NOT ST_IsValid(geometry)

   ReferencesCrist, E. P. (1985). A tm tasseled cap equivalent transformation for reflectance factor data. Remote Sensing of Environment, 17(3):301–306.
   Kennedy, R. E., Yang, Z., & Cohen, W. B. (2010). Detecting trends in forest disturbance and recovery using yearly Landsat time series: 1. LandTrendr—Temporal segmentation algorithms. Remote Sensing of Environment, 114(12), 2897-2910.

2. https://docs.google.com/document/d/1MuYjttWOZvqWPAz2BQvr6IPE7N4r9dxW2PuKJoSpxe4/edit#heading=h.lgt2q590e10r)
