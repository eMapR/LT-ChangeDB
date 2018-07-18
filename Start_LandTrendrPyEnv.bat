REM %PATH%;
SET PATH=%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv;%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\Library\bin;%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\Scripts;%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\site-packages
SET GDAL_DATA=%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\Library\share\gdal
SET PYTHONPATH=%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\site-packages;PYTHONPATH=%HOMEDRIVE%%HOMEPATH%\LandTrendrPyEnv\site-packages\click; REM click is in a weird place - need to define its path explicitly
start cmd.exe /k

