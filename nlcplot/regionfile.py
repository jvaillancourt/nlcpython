from . import header
from . import rect
import pyregion

def regionfile(filename):
   """Plot ds9 region files using pyregion
      
      filename - DS9 region file"""

   wcs = header.updateWcs(None) # get wcs for image
   head = wcs.to_header() # convert to pyfits header for pyregion
   z = header.updateZorder()
   
   r = pyregion.open(filename).as_imagecoord(head)
   patch_list, artist_list = r.get_mpl_patches_texts()
   
   fig = header.plt.gcf()
   ax  = fig.gca()
   
   for t in artist_list:
      t.set_zorder(z)
      ax.add_artist(t)
   for p in patch_list:
      p.set_zorder(p)
      ax.add_patch(p)
