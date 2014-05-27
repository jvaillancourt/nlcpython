from . import header
from . import vector
from . import text

def compass(x,y,angle,length,start=90,wcs='rd',**args):
   """Plot a compass of ra/dec or galactic l and b coordinates
   
      x,y    - coordinates for base of compass vectors
      angle  - Angle in degrees to rotate compass counter-clockwise
      length - length of compass vectors (probably pixels)
      start  - starting angle from +x that corresponds to zero.  The default
               of 90 means that zero degrees is the +y axis.  This is the
               normal convention in polarization maps.
      wcs    - can be 'rd' for RA/DEC compass or 'gl' for galactic compass
      Allowed optional **args:
         color     - string with color of the compass vectors
         size      - Size of vectors
         width     - Line width of vectors"""
   
   _allowed = ['color','size','width']
   fp = header._wipopen('compass',args.keys(),_allowed)
   fp.close()
   vector([x,x],[y,y],[angle,angle-90],[length,length],start,**args)
   a = 0.5*length*math.cos(math.pi*angle/180.)
   b = 0.65*length*math.sin(math.pi*angle/180.)
   if wcs == 'rd':
      text(x+a,y+1.5*b,r'\alpha',**args)
      text(x+a,y-b,r'\delta',**args)
   elif wcs == 'gl':
      text(x+a,y+1.5*b,r'\it{l}',**args)
      text(x+a,y-b,r'\it{b}',**args)
   else:
      header._error("compass(): wcs keyword must be 'rd' or 'gl'")   
