from . import header
from . import polygon

def rect(xmin,xmax,ymin,ymax,**args):
   """Draw a rectangle specified by coordinates xmin,xmax,ymin,ymax.

      This function calls polygon()

      Supported optional arguments:
      color  - Color of both inside and border of rectangle
      ecolor - Color of border of rectangle
      fcolor - Color of inside of rectangle
      fill   - Set to None for unfilled rectangle      
      style  - line style for border
      hatch  - Hatch style for interior
      coord - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
              offset), mo (arcminutes offset), so (arcseconds offset).
              Pixels start at 1.
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
      width  - thickness of rectangle border"""

   polygon([xmin,xmax,xmax,xmin],[ymin,ymin,ymax,ymax],**args)
