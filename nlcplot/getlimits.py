from . import header

def getlimits(coord='pix'):
   """Return current image limits as a list of [xmin,xmax,ymin,ymax,coord]

      coord - coordinates for returned limits.  Set to one of: pix, deg,
              do, mo, so (degrees/arcminutes/arcseconds offset).  Pixels start
              at 1."""

   l = list(header.plt.axis()) # this gets limits in pixel coordinates
   wcs = header.updateWcs(None)
   if coord == 'pix':
      if wcs is None:
         return l + [coord]
      else: # wcs defined, need to shift from zero-based to one-based
         l2 = [a + 1 for a in l]
         return l2 + [coord]
   elif coord in ('deg','do','mo', 'so'):
      if wcs is None:
         header.error("getlimits(): No wcs defined!")
      ra,dec = wcs.wcs_pix2sky([l[0],l[1],l[0],l[1]],[l[2],l[2],l[3],l[3]],0)
      # TODO: should we worry about RA increasing to the left, so that max(ra)
      # will be the smallest pixel value?
      if coord in ('do', 'mo', 'so'):
         crval = wcs.wcs.crval
      else:
         crval = (0,0)
      if coord == 'mo':
         fac = 60.
      elif coord == 'so':
         fac = 3600.
      else:
         fac = 1.
      xmin = fac*(min(ra)  - crval[0])
      xmax = fac*(max(ra)  - crval[0])
      ymin = fac*(min(dec) - crval[1])
      ymax = fac*(max(dec) - crval[1])
      return [xmin,xmax,ymin,ymax,coord]
   else:
      header.error("getlimits(): coord must be one of 'pix', 'deg', 'do', 'mo', or 'so'!")
