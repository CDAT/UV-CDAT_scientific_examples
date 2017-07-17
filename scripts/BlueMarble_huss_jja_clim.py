################################################################################################# 
# This Python script plots JJA climatology at surface level, which given from one of CMIP5 models
# It uses NASA's BlueMarble image as background map image
# 
# Ji-Woo Lee, LLNL, July 2017
################################################################################################# 

import vcs
import cdms2 as cdms
import cdtime, cdutil
import numpy as np
import urllib

# Option for getting background image
Blue_marble_download = True
#Blue_marble_download = False

#Nighttimeimage = True
Nighttimeimage = False

def overlay_png(canvas, png_path, data, data2=None, gm=None, scale=.75, template=None, continents=1):
	canvas.open()
	canvas.put_png_on_canvas(png_path, zoom=scale)
	canvas.clear()
	canvas.put_png_on_canvas(png_path, zoom=scale)

	is_portrait = canvas.size < 1

	if template:
		t = vcs.createtemplate(template)
	else:
		t = vcs.createtemplate()

	padding = (1 - scale) / 2.

	# Plot & outline
	t.data.priority = 10
	t.data.x1 = padding
	t.data.x2 = 1 - padding
	t.data.y1 = padding
	t.data.y2 = 1 - padding
	t.box1.x1 = padding
	t.box1.x2 = 1 - padding
	t.box1.y1 = padding
	t.box1.y2 = 1 - padding

	# Ticks
	ticlen = abs(t.xtic1.y2 - t.xtic1.y1)
	t.xtic1.y1 = padding
	t.xtic1.y2 = padding - ticlen
	t.ytic1.x1 = padding
	t.ytic1.x2 = padding - ticlen / 2.
	t.xtic2.y1 = 1 - padding
	t.xtic2.y2 = 1 - (padding - ticlen / 2.)
	t.ytic2.x1 = 1 - padding
	t.ytic2.x2 = 1 - (padding - ticlen / 2.)

	# Tick Labels
	t.xlabel1.y = t.xtic1.y2 - ticlen
	t.xlabel2.y = t.xtic2.y2 + ticlen
	t.ylabel1.x = t.ytic1.x2 - ticlen / 2.
	t.ylabel2.x = t.ytic2.x2 + ticlen / 2.

	# Axis labels
	t.xname.y = t.xlabel1.y - ticlen * 2
	t.yname.x = t.ylabel1.x - ticlen * 2

	# Legend
	if is_portrait:
		t.legend.x1 = t.data.x1
		t.legend.x2 = t.data.x2
		t.legend.y1 = t.data.y1 / 4.
		t.legend.y2 = t.legend.y1 + padding / 3.
	else:
		t.legend.x1 = t.data.x2 + padding / 4.
		t.legend.x2 = t.legend.x1 + padding / 4.
		t.legend.y1 = t.data.y1
		t.legend.y2 = t.data.y2

	plot_args = [data, data2, t, gm]
	kwargs = {"continents": continents}
	return canvas.plot(*[p for p in plot_args if p is not None], **kwargs)


if __name__ == "__main__":

	# DATA ---

	# Open file
	odir = '/cmip5_css02/data/cmip5/output1/NIMR-KMA/HadGEM2-AO/historical/mon/atmos/Amon/r1i1p1/huss/1/' # Put your local directory here
	nc = 'huss_Amon_HadGEM2-AO_historical_r1i1p1_186001-200512.nc'
	f = cdms.open(odir+nc)

	# Load variable
	d = f('huss',longitude=(-180,180)) # Set longitude range to Blue Marble image
	d.units='%'

	# Climatology calculation
	start_year = 1949
	end_year = 2010
	start_time = cdtime.comptime(start_year)
	end_time =cdtime.comptime(end_year)
	d_jja = cdutil.JJA.climatology(d(time=(start_time,end_time)))
	d_jja.units = '%'
	d_jja.long_name = 'JJA clim. huss., '+str(start_year)+'-'+str(end_year)
	d_jja.id = 'huss'
	d_jja.model = 'HadGEM2-AO'

	# PLOT ---

        # The blue marble file I found has an aspect ratio of 2x1, so we'll use that aspect for the canvas
        canvas = vcs.init(size=2)

        cmap = vcs.createcolormap("my_colormap", "rainbow_no_grn") #you can specify which colormap you want to copy from in the second argument
        for i in range(16, 240):
                r, g, b, _ = cmap.getcolorcell(i)
                cmap.setcolorcell(i, r, g, b, 50) # You can pick an alpha value that looks nice; 0-100
        canvas.setcolormap(cmap)

	# Set isofill level
	isofill = vcs.createisofill()

	# Adding -1.e20 / 1.e20 at ends of levels turns extensions on
        tmp = np.round(np.ndarray.tolist(np.arange(0., 0.026, 0.002)), decimals=3)
        levels = np.ndarray.tolist(np.round(tmp,decimals=3))
	isofill.levels = levels
	colors = vcs.getcolors(levels,colors=range(16,240))
	isofill.fillareacolors = colors

        if Blue_marble_download:
                # Download background image for map; http://visibleearth.nasa.gov/
                bg_image_link = 'http://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74393/world.topo.200407.3x5400x2700.png'
                if Nighttimeimage:
                        bg_image_link = 'http://eoimages.gsfc.nasa.gov/images/imagerecords/79000/79765/dnb_land_ocean_ice.2012.3600x1800.jpg'
                bg_image = 'bg_image_blue_marble.png'
                bg_image_frame = open(bg_image,'wb')
                bg_image_frame.write(urllib.urlopen(bg_image_link).read())
                bg_image_frame.close()

        else:
                # Substitute your path to blue_marble.png
                bg_image = './bg_image_blue_marble.png'

	overlay_png(canvas, bg_image, d_jja, gm=isofill)
	canvas.png("BlueMarble_huss_jja_clim")
