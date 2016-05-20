# 
# This python script plots climatologyt of JJA temperature obtained from one single CMIP5 model
#

import cdms2 as cdms
import cdutil
import cdtime
import vcs

#
# open file from local -- DATA was downloaded from ESGF
#
odir = '/cmip5_css02/data/cmip5/output1/NIMR-KMA/HadGEM2-AO/historical/mon/atmos/Amon/r1i1p1/tas/1/' # Put your data directory here
nc = 'tas_Amon_HadGEM2-AO_historical_r1i1p1_186001-200512.nc'
f = cdms.open(odir+nc)

#Below is for Opendap usage
#opendap = 'http://aims3.llnl.gov/thredds/dodsC/cmip5_css02_data/cmip5/output1/NIMR-KMA/HadGEM2-AO/historical/mon/atmos/Amon/r1i1p1/tas/1/tas_Amon_HadGEM2-AO_historical_r1i1p1_186001-200512.nc'
#f = cdms.open(opendap)

#
# load variable
#
d = f('tas',latitude=(-60,80),longitude=(0,360))-273.15
d.units='degree C'

#
# climatology calculation
#
start_year = 1949
end_year = 2010

start_time = cdtime.comptime(start_year)
end_time =cdtime.comptime(end_year)

d_jja = cdutil.JJA.climatology(d(time=(start_time,end_time)))
d_jja.units = d.units
d_jja.long_name = 'JJA clim. TAS, '+str(start_year)+'-'+str(end_year)
d_jja.id = 'tas'
d_jja.model = 'HadGEM2-AO'

#
# Create canvas
#
canvas = vcs.init(geometry=(1200,800))
canvas.open()

#
# Set plot type
#
iso = canvas.createisofill()

#
# Color setup
#
levs = [-16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12 , 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
iso.levels = levs
canvas.setcolormap("rainbow")

# 
# Plot
#
canvas.plot(d_jja,iso)

#
# Set title
#
plot_title = vcs.createtext()
plot_title.x = .5
plot_title.y = .98
plot_title.height = 24
plot_title.halign = "center"
plot_title.valign = "top"
plot_title.color="black"
plot_title.string = d_jja.model+' '+'ex1_tas_jja_clim'
canvas.plot(plot_title)

#
# Drop output as image file
#
canvas.png("example_sfc_tas_jja_clim")
