from . import header
from numpy import flipud

def rgb(image,wcs=None):
   """Plot a color image (PNG, JPG, etc)

      image = string with image as png, jpg, etc.
      wcs    - World Coordinate System for image (default is to read from input
              file."""

   global _fig
   z = header.updateZorder()
   if wcs is not None:
      header._fig['wcs'] = wcs

   d = header.plt.imread(image)
   d2 = flipud(d)
   
   header.plt.imshow(d2,interpolation='nearest',origin='lower',zorder=z)
