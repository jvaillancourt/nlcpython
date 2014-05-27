from . import header

def arrow(x,y,length,angle,start=90,**args):
   """Plot a single arrow
      
      Supported optional arguments:
      color  - color of arrow (controls both fcolor and ecolor)
      fcolor - color of face (inside) of arrow
      ecolor - color of edge of arrow
      coord  - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
               offset), mo (arcminutes offset), so (arcseconds offset).
               Pixels start at 1.
      width  - Thickness of arrow
      size   - Size of arrow head
      overhang - fraction of arrow head cut out in back (defaults to 0.0)
      wcs   - The wcs (defined by pywcs) used to convert from world coords
              to pixels.  If none, try to use a previously defined one
              (i.e., when halftone or contours were plotted).
   """

   a = header.translateArgs(**args)
   z = header.updateZorder()
   
   x1,y1 = header.translateCoords(x,y,a['coord'],a['wcs'])

   t = (start + angle)*header.pi/180.
   header.plt.arrow(x1,y1,length*header.cos(t),length*header.sin(t),
      length_includes_head=True,head_width=a['markersize']*a['linewidth'],
      width=a['linewidth'],facecolor=a['facecolor'],edgecolor=a['edgecolor'],
      overhang=a['overhang'],zorder=z)
