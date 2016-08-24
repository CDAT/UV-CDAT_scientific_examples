def plot_map(mode, model, syear, eyear, season, eof1, frac1, output_file_name):

  import vcs
  import string

  # Create canvas ---
  canvas = vcs.init(geometry=(900,800)) # Show canvas

  canvas.open()
  #canvas.drawlogooff()
  template = canvas.createtemplate()

  # Turn off no-needed information -- prevent overlap
  template.blank(['title','mean','min','max','dataname','crdate','crtime',
        'units','zvalue','tvalue','xunits','yunits','xname','yname'])

  # Color setup ---
  canvas.setcolormap('bl_to_darkred')
  iso = canvas.createisofill()
  if string.split(mode,'_')[0] == 'PDO':
    iso.levels = [-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5]
  else:
    iso.levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
  iso.ext_1 = 'y' # control colorbar edge (arrow extention on/off)
  iso.ext_2 = 'y' # control colorbar edge (arrow extention on/off)

  cols = vcs.getcolors(iso.levels)
  cols[6] = 139 # Adjsut color to light red for 0-1 (or 0-0.1) range
  iso.fillareacolors = cols
  iso.missing = 0 # Set missing value color as same as background

  # Map projection ---
  p = vcs.createprojection()
  if mode == 'NAO' or mode == 'PDO':
    p.type = 'lambert'
  elif mode == 'PDO_teleconnection':
    p.type = 'robinson' 
  else:
    p.type = int('-3')
  iso.projection = p
  xtra = {}
  if mode == 'PDO_teleconnection': 
    xtra = {}
  else: 
    xtra['latitude'] = (90.0,0.0) # For Northern Hemisphere
  eof1 = eof1(**xtra)

  canvas.plot(eof1,iso,template)

  # Title ---
  plot_title = vcs.createtext()
  plot_title.x = .5
  plot_title.y = .97
  plot_title.height = 23
  plot_title.halign = 'center'
  plot_title.valign = 'top'
  plot_title.color='black'
  percentage = str(round(float(frac1*100.),1)) + '%' # % with one floating number
  plot_title.string = mode+': '+model+'\n'+str(syear)+'-'+str(eyear)+' '+season+' '+percentage
  canvas.plot(plot_title)

  # Drop output as image file --- 
  canvas.png(output_file_name+'.png')
