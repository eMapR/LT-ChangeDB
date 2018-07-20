REM %PATH%;
SET LT_PY_ENV="C:\users\braatenj\LandTrendrPyEnv"
SET PATH=%LT_PY_ENV%;%LT_PY_ENV%\Library\bin;%LT_PY_ENV%\Scripts;%LT_PY_ENV%\site-packages
SET GDAL_DATA=%LT_PY_ENV%\Library\share\gdal
SET PYTHONPATH=%LT_PY_ENV%\site-packages
REM SET PYTHONPATH=%LT_PY_ENV%\site-packages;PYTHONPATH=%LT_PY_ENV%\site-packages\click; REM click is in a weird place - need to define its path explicitly -- this line works
start cmd.exe /k

