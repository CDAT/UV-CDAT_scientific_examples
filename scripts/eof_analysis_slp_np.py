import cdms2 as cdms
import cdutil
import cdtime
from eofs.cdms import Eof
import vcs
import string

#===========================================================================================================
# DATA
#-----------------------------------------------------------------------------------------------------------
# Open file ---
data_path = '/clim_obs/obs/atm/mo/psl/ERAINT/psl_ERAINT_198901-200911.nc' ## Put your file here
f = cdms.open(data_path)

# Set time period ---
start_year = 1980
end_year = 2000
start_time = cdtime.comptime(start_year)
end_time = cdtime.comptime(end_year)

# Load variable ---
d = f('psl',time=(start_time,end_time),longitude=(-180,180),latitude=(20,90)) # Provide proper variable name

# Get DJF seasonal mean time series ---
d_DJF = cdutil.DJF(d)

# Unit adjustment, Pa to hPa
d_DJF = d_DJF/100.

# EOF (take only first variance mode...) ---
solver = Eof(d_DJF, weights='area')
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

canvas.open()
template = canvas.createtemplate()

# Turn off no-needed information -- prevent overlap
template.blank(['title','mean','min','max','dataname','crdate','crtime',
      'units','zvalue','tvalue','xunits','yunits','xname','yname'])

# Color setup ---
canvas.setcolormap('bl_to_darkred')
iso = canvas.createisofill()
iso.levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
iso.ext_1 = 'y' # control colorbar edge (arrow extention on/off)
iso.ext_2 = 'y' # control colorbar edge (arrow extention on/off)
cols = vcs.getcolors(iso.levels)
iso.fillareacolors = cols
iso.missing = 0 # Set missing value color as same as background

# Map projection ---
p = vcs.createprojection()
p.type = int('-3') 
iso.projection = p
xtra = {}
xtra['latitude'] = (90.0,0.0) # For Northern Hemisphere

# Plot ---
canvas.plot(eof[0](**xtra),iso,template)

# Title ---
plot_title = vcs.createtext()
plot_title.x = .5
plot_title.y = .97
plot_title.height = 23
plot_title.halign = 'center'
plot_title.valign = 'top'
plot_title.color='black'
percentage = str(round(float(frac[0]*100.),1)) + '%' # % with one floating number
plot_title.string = 'Northern Atlantic Oscillation (NAO)\n EOF first mode, ERAINT('+str(start_year)+'-'+str(end_year)+'), psl, DJF, '+percentage
canvas.plot(plot_title)

# Save output as image file --- 
canvas.png('eof_analysis_slp_np.png')
