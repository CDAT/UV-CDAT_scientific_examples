################################################################################################# 
# This Python script plots EOF analysis of sea-surface temperature observation
# 
# Ji-Woo Lee, LLNL, July 2017
################################################################################################# 

import cdms2 as cdms
import cdutil
import cdtime
from eofs.cdms import Eof
import vcs

#===========================================================================================================
# DATA
#-----------------------------------------------------------------------------------------------------------
# Open file ---
data_path = '/clim_obs/obs/ocn/mo/tos/UKMETOFFICE-HadISST-v1-1/130122_HadISST_sst.nc' ## Put your file here
f = cdms.open(data_path)

# Set time period ---
start_year = 1980
end_year = 2000
start_time = cdtime.comptime(start_year)
end_time = cdtime.comptime(end_year)

# Load variable ---
d = f('sst',time=(start_time,end_time),longitude=(0,360),latitude=(-90,90)) # Provide proper variable name

# Reomove annual cycle ---
d_anom = cdutil.ANNUALCYCLE.departures(d)

# EOF (take only first variance mode...) ---
solver = Eof(d_anom, weights='area')
eof = solver.eofsAsCovariance(neofs=1)
pc = solver.pcs(npcs=1, pcscaling=1) # pcscaling=1: scaled to unit variance 
                                     # (divided by the square-root of their eigenvalue)
frac = solver.varianceFraction()

# Sign control if needed ---
eof = eof * -1
pc = pc * -1

#===========================================================================================================
# Plot
#-----------------------------------------------------------------------------------------------------------
# Create canvas ---
canvas = vcs.init(geometry=(900,800))
#canvas = vcs.init()

canvas.open()
template = canvas.createtemplate()

# Turn off no-needed information -- prevent overlap
template.blank(['title','mean','min','max','dataname','crdate','crtime',
      'units','zvalue','tvalue','xunits','yunits','xname','yname'])

# Color setup ---
canvas.setcolormap('bl_to_darkred')
iso = canvas.createisofill()
levels = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
levels.insert(0,-1.e20)
levels.append(1.e20)
iso.levels = levels
colors = vcs.getcolors(levels,colors=range(16,240))
iso.fillareacolors = colors
iso.missing = 0 # Set missing value color as same as background

# Map projection ---
p = vcs.createprojection()
p.type = 'robinson'
iso.projection = p

# Plot ---
canvas.plot(eof[0],iso,template)

# Title ---
plot_title = vcs.createtext()
plot_title.x = .5
plot_title.y = .97
plot_title.height = 23
plot_title.halign = 'center'
plot_title.valign = 'top'
plot_title.color='black'
percentage = str(round(float(frac[0]*100.),1)) + '%' # % with one floating number
plot_title.string = 'EOF first mode, HadISST('+str(start_year)+'-'+str(end_year)+'), '+percentage
canvas.plot(plot_title)

# Save output as image file --- 
canvas.png('eof_analysis.png')
