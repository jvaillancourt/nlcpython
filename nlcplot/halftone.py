from . import header
import pywcs

def halftone(image,cmap='gray_r',ext=1,plane=1,vmin=None,vmax=None,**args):
   """Plot a halftone image with specified colormap.
   
      returns: numpy array of the halftone data.

      keywords:
      image = string with FITS image or the data as a numpy array
      ext   = FITS extension as a number or string name
      plane = Plane to plot from a data cube
      cmap  = Colormap to use for plotting
      vmin  = Minimum halftone value.  None is minimum of image
      vmax  = Maximum halftone value.  None is maximum of image
      
      optional keywords:
      wcs    - The wcs (as defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
               TODO: better description that is applicable to halftone()
               needed."""

   global _fig
   z = header.updateZorder()

   if isinstance(image,str):
      data = header.getdata(image,ext=ext)
      head = header.getheader(image,ext=ext)
      header._fig['wcs'] = pywcs.WCS(head)
   else:
      data = image
   a = header.translateArgs(**args)

   naxis = len(data.shape)
   if naxis == 1:
      header.error("halftone(): Image must be 2-D or 3-D to plot!")
   elif naxis == 2:
      pass
   elif naxis == 3:
      data = data[plane,:,:] # select a single plane from cube
   else:
      header.error("halftone(): Image must be 2-D or 3-D to plot!")

   header.plt.imshow(data,origin='lower',cmap=cmap,interpolation='nearest',
      aspect='equal',vmin=vmin,vmax=vmax,zorder=z)
   #header.plt.axis('off') # turn off axis plot
   return data
