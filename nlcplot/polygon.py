from . import header

def polygon(x,y,**args):
   """Plot polygons

      Supported optional arguments:
      fcolor - Color of inside of polygon
      ecolor - Color of border of polygon
      color  - Color of both inside and border of polygon
      style  - line style for border
      fill   - Set to None for unfilled polygon
      hatch  - Hatch style for interior
      coord - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
              offset), mo (arcminutes offset), so (arcseconds offset).
              Pixels start at 1.
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
      width  - thickness of polygon border"""

   a = header.translateArgs(**args)
   z = header.updateZorder()
   
   if a['linestyle'] == '-':
      a['linestyle'] = 'solid'
   elif a['linestyle'] == '--':
      a['linestyle'] = 'dashed'
   elif a['linestyle'] == '-.':
      a['linestyle'] = 'dashdot'
   elif a['linestyle'] == ':':
      a['linestyle'] = 'dotted'

   x2,y2 = header.translateCoords(x,y,a['coord'],a['wcs'])

   header.plt.fill(x2,y2,fill=a['fillstyle'],ec=a['edgecolor'],fc=a['facecolor'],
      lw=a['linewidth'],ls=a['linestyle'],hatch=a['hatch'],zorder=z)
