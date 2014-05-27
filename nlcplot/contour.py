from . import header
import pyfits,pywcs
from numpy import nanmin,nanmax,linspace
from scipy import ndimage

def contour(image,levels=None,ext=0,align='pix',wcs=None,sigma=None,**args):
   """image  - string with FITS image or the data as a numpy array
      levels - either an integer number of levels, or a list or numpy array of
               levels
      ext    - FITS extension as a number or string name
      align  - How to align contours with halftone.  Options are either pix
               or wcs.
      wcs    - World Coordinate System for image (default is to read from input
              file.
      sigma  - Smooth the input data by a gaussian filter with a standard
               deviation equal to this value, in pixels.  Default is no
               smoothing.

      Supported optional arguments:
      color  - Color of contour lines"""

   global _fig
   a = header.translateArgs(**args)
   z = header.updateZorder()

   if isinstance(image,str):
      data = pyfits.getdata(image,ext=ext)
      head = pyfits.getheader(image,ext=ext)
      wcs2 = pywcs.WCS(head)
   else:
      data = image
      wcs2 = wcs

   if sigma is not None: # smooth data for cleaner contours
      data = ndimage.gaussian_filter(data,sigma)

   if isinstance(levels,int):
      immin  = nanmin(data)
      immax  = nanmax(data)
      levels = linspace(immin,immax,levels)

   lw = 0.5*a['linewidth']
   if align == 'pix': # align by pixel number (ignore wcs)
      header.plt.contour(data,colors=a['color'],levels=levels,linewidths=lw,zorder=z)
   elif align == 'wcs':
      wcs1 = header.updateWcs(None) # current wcs of image
      if wcs1 is None or wcs2 is None:
         header.error("contour(): no wcs in image to align with!")
      ctype1 = header.translateCtype(wcs1) # get ctype, i.e. ra, glon
      ctype2 = header.translateCtype(wcs2)

      contourset = header.plt.contour(data,alpha=0.0,levels=levels) # get contours
      nlevels = len(contourset.collections)
      for n in range(nlevels): # loop over each contour
         paths = contourset.collections[n].get_paths()
         for path in paths: # loop over each partial contour (path)
            if path.codes is not None:
               header.error("contour(): Can't handle codes right now!")
            vert = path.vertices # get pixel paths, convert to sky coords
            vert2 = wcs2.wcs_pix2sky(vert,0) # 0-based pixels b/c internal

            # now convert sky coords back to underlying pixel coords
            if ctype1 == ctype2:
               vert3 = wcs1.wcs_sky2pix(vert2,0) # 0-based pixels b/c internal
            header.plt.plot(vert3[:,0],vert3[:,1],ls='-', lw=lw, color=a['color'],zorder=z)
   else:
      header.error("contour(): Other alignments not supported yet")

   # update wcs with new one for this image
   if wcs2 is not None:
      header._fig['wcs'] = wcs2
