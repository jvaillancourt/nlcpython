from . import header

def stick(x,y,length,angle,filename=None,comment='#',scale=1,start=90,**args):
   """Plot sticks (vectors without arrowheads).

      matplotlib version 1.0.0 will give error messages when running this
      command, but the sticks will look fine.

      x,y      - integer, list, or tuple for x/y data points
      length   - integer, list, or tuple for length of sticks
      angle    - integer, list, or tuple for angles of sticks.  Values are
                 in degrees.  Note, the start keyword defines where zero
                 degrees is located.
      datafile - string name of input data file.  Leave as None if
                 x,y,length,angle are a sequence of numbers
      comment  - comment character used in datafile
      scale    - scale factor for length of sticks
      start    - starting angle from +x that corresponds to zero degrees.  The
                 default of 90 means that zero degrees is the +y axis.  This is
                 the normal convention in polarization maps.

      Supported optional arguments:
      color - Color of stick
      coord - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
              offset), mo (arcminutes offset), so (arcseconds offset).
              Pixels start at 1.
      fixed - Set to True if lengths of sticks should be held fixed and equal
              to scale factor
      wcs   - The wcs (defined by pywcs) used to convert from world coords
              to pixels.  If none, try to use a previously defined one
              (i.e., when halftone or contours were plotted).
      width - thickness of stick"""

   global _fig
   a   = header.translateArgs(**args)
   z   = header.updateZorder()

   a['linestyle'] = header.lineStyleToText(a['linestyle'])

   if filename is not None:
      data = header.loadtxt(filename,comments=comment,usecols=[x-1,y-1,length-1,
         angle-1])
      ndim = data.ndim
      if ndim == 1: # catch cases where only one line in file
         if data.shape[0] == 0: # catch cases of empty input file
            header.error("stick(): No data to plot")
         x = data[0]
         y = data[1]
         l = data[2]*scale
         angle = data[3]
      elif ndim == 2:
         x = data[:,0]
         y = data[:,1]
         l = data[:,2]*scale
         angle = data[:,3]
      else:
         header.error("stick(): ndim must be 1 or 2")
   else:
      x = x
      y = y
      l = length*scale
   if len(x) == 0 or len(y) == 0 or len(l) == 0 or len(angle) == 0:
      print("### Warning! zero-vectors to plot.")
      return
   
   if a['fixed'] is True:
      l = scale
   x2,y2 = header.translateCoords(x,y,a['coord'],a['wcs'])
   #x3,y3 = header.translateCoords(x+l,y,a['coord'],a['wcs'])# for length
   #l = x3-x2

   if a['linestyle'] != 'solid':
      print "### Warning!  non-solid vectors doesn't seem to work."
   t = (start + angle)*header.pi/180.
   Q = header.plt.quiver(x2,y2,l*header.cos(t),l*header.sin(t),headwidth=0,
      headlength=0,scale=1,headaxislength=0,pivot='middle',units='dots',
      width=a['linewidth'],facecolor=a['color'],edgecolor=a['color'],zorder=z,
      linestyles=a['linestyle'])
   header._fig['quiver'] = Q
   header._fig['scale'] = scale
