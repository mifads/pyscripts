# Dave's python scripts

Scripts are mainly designed to work with EMEP files, especially the netcdf outputs, but will also accept other formats sometimes (e.g. EHCAM).

* Mainly python3
* Tested in modern (2016-2017) Xubuntu systems, 
* Mapping uses cartopy (which is not always in Ububtu repos, but available from github, or via conda, etc.)

Some comments
==============

I'm still a beginner with python. All scripts can be done better!

The codes are listed below, roughly in order or importance/usage.

Code                          | Comment
:--------------------------   |:---------------------------------------
EmepCdf.py |  Main code to read EMEP files - checks projections, dimensions, etc. Gets values for givem lat/long point using bi-linear interpolation of nearby cells. Can also return the values of surrounding points - to make the shadowing used in Dave's time series scripts.
mkCdf.py | Creates cdf files from a list of variable names and data. Works for lon/lat so far.
mkCdfComp.py | IN DEVELOPMENT ... compares 2 or more monthly files, for key patterns and given domain.
  | 
get_emepcoords.py |
get_emepcoords_projOnly.py |
StringFunctions.py | *stringClean* - Function to get rid of funny chars in names, e.g Bratt's Lake
"                  | *blankRemove* - obvious ...
"                  | *multiwrite*  - combines elements from an array with given format string
EmepScatPlots.py | Produces scatter plots, including optinional detection of outliers and addition of labels
"                  | (needed python pip3 install statsmodels on Xubuntu 17.04)
scanVerification.py | scans multiple Verification(scatterstations) results files and produces summary for annual statistics.
AreaLonLatCell.py  |
CountryStuff.py | Figures out country, continent, ISO2, ISO3 etc. from lon, lat coordinates (python2.67 only)
DailyOzoneMetrics.py |
SeasonalOzoneMetrics.py |
DateStuff.py |
macc2emep.py  |  Converts TNO/MACC format files to EMEP emission netcdf files
mkEUmask.py  |
ObservationsClass.py |
to_precision.py      |           not used? Returns string of formatted number
Geometry.py | Returns distance to regresssion line. Used in EmepScatPlots
WeibullW126.py |
printGenReactions.py | prints cleaned-up version of GenChem reactions files, minus comments
LICENSE.txt         |             GPL
README.md | This file.

