"""
This is condensed version of variability mode driver of PCMDI Metrics Package (PMP) in purpose of providing scientific examples for UV-CDAT. Full version will be available through the PMP (https://github.com/PCMDI/pcmdi_metrics). This script creates plots for Northern Atlantic Oscillation (NAO) and Pacific Decadal Oscillation (PDO) modes which are defined based on EOF analysis.

Ji-Woo Lee, LLNL, August 2016
"""

import os
import cdms2 as cdms
import cdutil
import cdtime
import genutil
from eofs.cdms import Eof
import vcs
import numpy as NP

libfiles = [ 'eof_analysis.py',
             'eof_plot_map.py']

for lib in libfiles:
  execfile(os.path.join('./',lib))

##################################################
# User defining options
#=================================================
# Mode of variability --
#mode = 'NAO' # Northern Atlantic Oscillation
mode = 'PDO' # Pacific Decadal Oscillation

season = 'DJF' # Available options for NAO: 'DJF','MAM','JJA','SON'
               # PDO is calculated from monthly, thus this option will be ignored.

##################################################
# Region selector ---
if mode == 'NAO':
  lat1 = 20
  lat2 = 80
  lon1 = -90
  lon2 = 40
  var = 'psl' # Variable name in NetCDF
elif mode == 'PDO':
  lat1 = 20
  lat2 = 70
  lon1 = 110
  lon2 = 260
  var = 'ts' # Variable name in NetCDF

# lon1g and lon2g is for global map plotting ---
lon1g = -180
lon2g = 180

if mode == 'PDO':
  lon1g = 0
  lon2g = 360

#=================================================
# Dataset 
#-------------------------------------------------
# Load variable ---
if var == 'psl':
  obs_path = '/clim_obs/obs/atm/mo/psl/ERAINT/psl_ERAINT_198901-200911.nc'
  obs_source = 'ERAINT'
  fo = cdms.open(obs_path)
  obs_timeseries = fo(var)/100. # Pa to hPa

elif var == 'ts':
  obs_path = '/clim_obs/obs/ocn/mo/tos/UKMETOFFICE-HadISST-v1-1/130122_HadISST_sst.nc'
  obs_source = 'HadISST'
  fo = cdms.open(obs_path)
  obs_timeseries = fo('sst')

  # Replace area where temperature below -1.8 C to -1.8 C ---
  obs_mask = obs_timeseries.mask
  obs_timeseries[obs_timeseries<-1.8] = -1.8
  obs_timeseries.mask = obs_mask

cdutil.setTimeBoundsMonthly(obs_timeseries)

# Check available time period ---
syear = obs_timeseries.getTime().asComponentTime()[0].year
eyear = obs_timeseries.getTime().asComponentTime()[-1].year

#-------------------------------------------------
# Adjust time series
#- - - - - - - - - - - - - - - - - - - - - - - - -
if mode == 'PDO':
  # Reomove annual cycle ---
  obs_timeseries = cdutil.ANNUALCYCLE.departures(obs_timeseries)

  # Subtract global mean ---
  obs_global_mean_timeseries = cdutil.averager(obs_timeseries(latitude=(-60,70)), axis='xy', weights='weighted')
  obs_timeseries, obs_global_mean_timeseries = \
                    genutil.grower(obs_timeseries, obs_global_mean_timeseries) # Match dimension
  obs_timeseries = obs_timeseries - obs_global_mean_timeseries     

else:
  # Get seasonal mean time series ---
  obs_timeseries = getattr(cdutil,season)(obs_timeseries)

#-------------------------------------------------
# EOF analysis and linear regression
#- - - - - - - - - - - - - - - - - - - - - - - - -
# Extract subdomain ---
obs_timeseries_subdomain = obs_timeseries(latitude=(lat1,lat2),longitude=(lon1,lon2))

# EOF analysis ---
eof1, pc1, frac1 = eof_analysis_get_first_variance_mode(mode, obs_timeseries_subdomain)

# Linear regression to have extended global map; teleconnection purpose ---
eof1_lr = linear_regression(pc1, obs_timeseries)

#-------------------------------------------------
# Record results 
#- - - - - - - - - - - - - - - - - - - - - - - - -
# Set output file name for plot ---
output_file_name = mode+'_'+var+'_eof1_'+season+'_'+obs_source+'_'+str(syear)+'-'+str(eyear)

# Plotting ---
plot_map(mode, obs_source, syear, eyear, season, eof1, frac1, output_file_name)
plot_map(mode+'_teleconnection', obs_source, syear, eyear, season, 
         eof1_lr(longitude=(lon1g,lon2g)), frac1, output_file_name+'_teleconnection')
