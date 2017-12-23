# Dave's python scripts

Scripts are mainly designed to work with EMEP files, especially the netcdf outputs, but will also accept other formats sometimes (e.g. ECHAM).

* Mainly python3
* Tested in modern (2016-2017) Xubuntu systems, 
* Mapping uses cartopy (which is not always in Ububtu repos, but available from github, or via conda, etc.)

Some comments
==============

I'm still a beginner with python. All scripts can be done better! Please let me know of any improvements (rather than changing files in my repository directly - I'd like to keep control of these so that I understand them at least).

The codes are listed below, roughly in order or importance/usage.

The code is organised in 'emx' directories (emx = emep/esx)

* emxcdf    - read and write cdf files
* emxdata   - related to observations
* emxemis   - emissions, mainly MACC processing so far
* emxmisc
* emxplot

emxcdf  code                  | Comment
:--------------------------   |:---------------------------------------
readcdf.py |  Main code to read EMEP files - checks projections, dimensions, etc. Gets values for givem lat/long point using bi-linear interpolation of nearby cells. Can also return the values of surrounding points - to make the shadowing used in Dave's time series scripts. Was EmepCdf.py
makecdf.py | Creates cdf files from a list of variable names and data. Works for lon/lat so far.

emxdata code                  | Comment
:--------------------------   |:---------------------------------------
ObservationsClass.py |

emxemis code                  | Comment
:--------------------------   |:---------------------------------------
macc2emep.py  |  Converts TNO/MACC format files to EMEP emission netcdf files

emxmisc code                  | Comment
:--------------------------   |:---------------------------------------
arealonlatcell.py  | Calculates area of cell with specified size in degrees
daily2meanvalues.py | Calculates mean between start and end-day from daily values. Copes with non-integer (e.g- from Ebas)
datestuff.py | avoiding datetime module, is_leap_year, doy,ymd
geometry.py | Returns distance to regresssion line. Used in EmepScatPlots
geocountries.py | Figures out country, continent, ISO2, ISO3 etc. from lon, lat coordinates (python2.67 only)
get_emepcoords.py | doc needed
get_emepcoords_projOnly.py | doc needed
emepstats.py      | Basic stats, mean, R, data-capture. Will expand in future (was EmepStats.py)
mkEUmask.py       | creates netcdf file with EU mask. (Hard-coded though, needs emis file)
numberfunctions.py | Small helper functions, eg for nint
printGenReactions.py | prints cleaned-up version of GenChem reactions files, minus comments
startdays.py | print out daynumbers at the start of each month.
stringfunctions.py | *stringClean* - Function to get rid of funny chars in names, e.g Bratt's Lake
"                  | *blankRemove* - obvious ...
"                  | *multiwrite*  - combines elements from an array with given format string
string2num.py      | not used? Returns string of formatted number


emxozone code                  | Comment
:--------------------------   |:---------------------------------------
dailymetrics.py | doc needed
seasonalmetrics.py | doc needed
weibullw126.py |

emxplots code                  | Comment
:--------------------------   |:---------------------------------------
dailyplots.py | Produces time-series plots of daily data, including optional fill range
"                  | (needed python pip3 install statsmodels on Xubuntu 17.04)
scatplots.py | Produces scatter plots, including optinional detection of outliers and addition of labels


Code                          | Comment
:--------------------------   |:---------------------------------------
emep_monthlyComp.py | Compares 2 or more annual or monthly files, for key patterns and given domain. Produces line plots for monthly files, and bar plots for annual. Still in development, but useful.

scanVerification.py | scans multiple Verification(scatterstations) results files and produces summary for annual statistics.
LICENSE.txt         |             GPL
README.md | This file.

