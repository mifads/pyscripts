Dave’s python scripts
=====================

Scripts are mainly designed to work with EMEP files, especially the
netcdf outputs, but will also accept other formats sometimes
(e.g. ECHAM).

-  Mainly python3
-  Tested in modern (2016-2018) Xubuntu systems,
-  Mapping uses cartopy (which is not always in Ububtu repos, but
   available from github, or via conda, etc.)

2019-01-12 - added to readthedocs for testing

Some comments
=============

I’m still a beginner with python. All scripts can be done better! Please
let me know of any improvements (rather than changing files in my
repository directly - I’d like to keep control of these so that I
understand them at least).

The codes are listed below, roughly in order or importance/usage.

The code is organised in ‘emx’ directories (emx = emep/esx)

-  emxcdf - read and write cdf files
-  emxdata - related to observations
-  emxemis - emissions, mainly MACC processing so far
-  emxmisc - bits n pieces
-  emxplot - daily, diurnal and scatter plots
-  emxverify - scripts to compare emep model and obs data.

+----------------------------+-----------------------------------------+
| emxcdf                     | Comment                                 |
+============================+=========================================+
| readcdf.py                 | Main code to read EMEP files - checks   |
|                            | projections, dimensions, etc. Gets      |
|                            | values for givem lat/long point using   |
|                            | bi-linear interpolation of nearby       |
|                            | cells. Can also return the values of    |
|                            | surrounding points - to make the        |
|                            | shadowing used in Dave’s time series    |
|                            | scripts. Was EmepCdf.py                 |
+----------------------------+-----------------------------------------+
| makecdf.py                 | Creates cdf files from a list of        |
|                            | variable names and data. Works for      |
|                            | lon/lat so far.                         |
+----------------------------+-----------------------------------------+

+----------------------------+-----------------------------------------+
| emxdata                    | Comment                                 |
+============================+=========================================+
| ObservationsClass.py       | Class with various info on              |
|                            | observations. May be overkill in        |
|                            | retrospect                              |
+----------------------------+-----------------------------------------+
| tabulate_nilu_ozone_statio | makes Tabulated_nilu_ozone_stations.txt |
| ns.py                      |                                         |
+----------------------------+-----------------------------------------+

+----------------------------+-----------------------------------------+
| emxemis                    | Comment                                 |
+============================+=========================================+
| macc2emep.py               | Converts TNO/MACC format files to EMEP  |
|                            | emission netcdf files                   |
+----------------------------+-----------------------------------------+

+----------------------------+-----------------------------------------+
| emxmisc code               | Comment                                 |
+============================+=========================================+
| arealonlatcell.py          | Calculates area of cell with specified  |
|                            | size in degrees                         |
+----------------------------+-----------------------------------------+
| daily2meanvalues.py        | Calculates mean between start and       |
|                            | end-day from daily values. Copes with   |
|                            | non-integer (e.g- from Ebas)            |
+----------------------------+-----------------------------------------+
| datestuff.py               | avoiding datetime module, is_leap_year, |
|                            | doy,ymd                                 |
+----------------------------+-----------------------------------------+
| geometry.py                | Returns distance to regresssion line.   |
|                            | Used in EmepScatPlots                   |
+----------------------------+-----------------------------------------+
| geocountries.py            | Figures out country, continent, ISO2,   |
|                            | ISO3 etc. from lon, lat coordinates     |
|                            | (python2.67 only)                       |
+----------------------------+-----------------------------------------+
| get_emepcoords.py          | doc needed                              |
+----------------------------+-----------------------------------------+
| get_emepcoords_projOnly.py | doc needed                              |
+----------------------------+-----------------------------------------+
| emepstats.py               | Basic stats, mean, R, data-capture.     |
|                            | Will expand in future (was              |
|                            | EmepStats.py)                           |
+----------------------------+-----------------------------------------+
| mkEUmask.py                | creates netcdf file with EU mask.       |
|                            | (Hard-coded though, needs emis file)    |
+----------------------------+-----------------------------------------+
| numberfunctions.py         | Small helper functions, eg for nint     |
+----------------------------+-----------------------------------------+
| printGenReactions.py       | prints cleaned-up version of GenChem    |
|                            | reactions files, minus comments         |
+----------------------------+-----------------------------------------+
| startdays.py               | print out daynumbers at the start of    |
|                            | each month.                             |
+----------------------------+-----------------------------------------+
| stringfunctions.py         | *stringClean* - Function to get rid of  |
|                            | funny chars in names, e.g Bratt’s Lake  |
+----------------------------+-----------------------------------------+
| "                          | *blankRemove* - obvious …               |
+----------------------------+-----------------------------------------+
| "                          | *multiwrite* - combines elements from   |
|                            | an array with given format string       |
+----------------------------+-----------------------------------------+
| string2num.py              | not used? Returns string of formatted   |
|                            | number                                  |
+----------------------------+-----------------------------------------+
| unitsconc.py               | converts ppb to ug/m3 and vice-versa    |
+----------------------------+-----------------------------------------+

================== ==========
emxozone code      Comment
================== ==========
dailymetrics.py    doc needed
seasonalmetrics.py doc needed
weibullw126.py    
================== ==========

+----------------------------+-----------------------------------------+
| emxplots code              | Comment                                 |
+============================+=========================================+
| plotdaily.py               | Produces time-series plots of daily     |
|                            | data, including optional fill range     |
+----------------------------+-----------------------------------------+
| "                          | (needed python pip3 install statsmodels |
|                            | on Xubuntu 17.04)                       |
+----------------------------+-----------------------------------------+
| plotscatt.py               | Produces scatter plots, including       |
|                            | optinional detection of outliers and    |
|                            | addition of labels                      |
+----------------------------+-----------------------------------------+
| plotdiurnal.py             | Diurnal (1-24h) plots                   |
+----------------------------+-----------------------------------------+

+----------------------------+-----------------------------------------+
| emxverify code             | Comment                                 |
+============================+=========================================+
| comp_ozone_metrics.py      | produces daily and diurnal plots and    |
|                            | tables for Dmax, AOT, W126,M/ etc. Uses |
|                            | hourly data (so far). Typically run     |
|                            | using run_comp_ozone_metrics.py         |
+----------------------------+-----------------------------------------+

ebas_flags.py

+----------------------------+-----------------------------------------+
| Misc code                  | Comment                                 |
+============================+=========================================+
| auto_dicts                 | Allows multi-dimensional dicts to be    |
|                            | created (autovivified) on the fly       |
+----------------------------+-----------------------------------------+
| emepmonthlycomp.py         | Compares 2 or more annual or monthly    |
|                            | files, for key patterns and given       |
|                            | domain. Produces line plots for monthly |
|                            | files, and bar plots for annual. Still  |
|                            | in development, but useful.             |
+----------------------------+-----------------------------------------+
| emepsitecomp.py            | Compares 2 or more annual or monthly    |
|                            | files, for key patterns and given       |
|                            | coords (or full domain). Still in       |
|                            | development (hacked from                |
|                            | emepmonthlycomp), but useful.           |
+----------------------------+-----------------------------------------+
| sum_regional_emissions.py  | sums values from input netcdf over      |
|                            | regions and globally. Used for          |
|                            | emissions so far                        |
+----------------------------+-----------------------------------------+
| scanVerification.py        | scans multiple                          |
|                            | Verification(scatterstations) results   |
|                            | files and produces summary for annual   |
|                            | statistics.                             |
+----------------------------+-----------------------------------------+
| pyRef.py                   | Reads bibtex file and allows search and |
|                            | pdf viewing. Hard-coded for Dave's      |
|                            | Refs.bib so far, since just started.    |
+----------------------------+-----------------------------------------+
| LICENSE.txt                | GPL                                     |
+----------------------------+-----------------------------------------+
| README.md                  | This file.                              |
+----------------------------+-----------------------------------------+
