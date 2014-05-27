#!/usr/bin/env python
"""Script to generate proper WCS tickmarks for matplotlib."""

from . import header
import pywcs,pyfits
import numpy as np
from numpy import pi,sin,cos,arccos,where,isnan

def _angdist(ra1,dec1,ra2,dec2):
   """Compute the angular distance between two points, in degrees

      Note, ra1,dec1,ra2,dec2 can be numpy arrays or individual points"""

   tmp = pi/180.
   dist = cos(tmp*dec1)*cos(tmp*dec2)*cos(tmp*(ra1-ra2))
   dist = dist + sin(tmp*dec1)*sin(tmp*dec2)
   dist = arccos(dist)/tmp
   mask = where(isnan(dist))
   dist[mask] = 0
   return dist

def _convert(value,coord,precision=0):
   """Convert a single value in deg to sexagesimal.  Use in conjunction with
      _deg2sex() below.

      Returns sexagesimal value as a string

      value     = sexagesimal or degrees as a string
      coord     = either 'ra' or 'dec' to specify coordinate type
      precision = number of decimal places for rounding seconds"""

   negFlag = False # set to true if value is negative
   try:
      tmp = map(float,value.split(':'))
      if tmp[0] < 0:
         negFlag = True
         tmp[0] = abs(tmp[0])
   except ValueError:
      header.error('Invalid string given for conversion to sexagesimal: %s' %value)

   n = len(tmp)
   if n == 1: # assume it was in degrees
      junk = tmp[0]
      if coord == 'ra':
         junk = junk/15.0
      hours = int(junk)
      try:
         junk = 60*(junk%hours)
         minutes = int(junk)
      except ZeroDivisionError:
         minutes = int(60*junk)
      try:
         seconds = 60*(junk%minutes)
      except ZeroDivisionError:
         seconds = 60*junk
      while seconds >= 60:
         seconds = seconds - 60
         minutes += 1
      while minutes >= 60:
         minutes = minutes - 60
         hours += 1
      tmp = [hours,minutes,seconds]
   elif n == 2: # assume it was already sexagesimal, but no seconds given
      tmp.append(0.0)

   # now convert to a string
   seconds = round(tmp[2],precision)
   if precision == 0:
      seconds = int(seconds)
   while seconds >= 60:
      seconds -= 60
      tmp[1] += 1
   minutes = tmp[1]
   while minutes >= 60:
      minutes -= 60
      tmp[0] += 1
   if seconds < 10:
      tmp = "%d:%02d:0%s" %(tmp[0],minutes,str(seconds))
   else:
      tmp = "%d:%02d:%s" %(tmp[0],minutes,str(seconds))
   if negFlag: # catch cases where deg. is neg
      tmp = '-' + tmp

   return tmp

def _deg2sex(value,coord,precision=0):
   """Convert degrees to sexagesimal

      value     = str/float/int/tuple/list of sexagesimal or degree values
      coord     = either 'ra' or 'dec' to specify coordinate type
      precision = number of decimal places for rounding seconds"""

   if isinstance(value,float) or isinstance(value,int) or isinstance(value,str):
      tmp = _convert(str(value),coord,precision)
   else:
      tmp = []
      for c in value:
         tmp.append(_convert(str(c),coord,precision))
   return tmp

def _getstepdec_dms(dec):
   """Get stepdec and declabel in for the range of DEC plotted.  This is
      computed for degrees/minutes/seconds plotting.

      dec is two values in degrees

      returns stepdec and declabel in degrees"""

   # label steps in arcseconds
   tmplabel = [1  ,5,10,15,20,30,60,300,600,900,1200,1800,3600,18000,36000]
   tmpstep  = [0.5,1, 5, 5, 5,10,20, 60,300,300, 300, 600,1200, 3600,18000]

   declabel = map(lambda a: a/3600.,tmplabel) # convert to degrees
   stepdec  = map(lambda a: a/3600.,tmpstep)  # convert to degrees

   tmp = abs(dec[1] - dec[0])
   guess = tmp/6. # aim for about 6 labels
   diff  = [abs(guess-a) for a in declabel]
   idx   = diff.index(min(diff))

   return stepdec[idx],declabel[idx]

def _getstepra_hms(ra):
   """Get stepra and ralabel for the range of RA plotted.  This is computed
      for hours/minutes/seconds plotting.

      ra is two values in degrees

      return stepra and ralabel in degrees (I think)"""

   # label steps in hour-seconds
   tmplabel = [1  ,  2,5,10,15,20,30,60,120,300,600,900,1200,1800,3600,18000]
   tmpstep  = [0.5,0.5,1, 2, 5, 5, 5,20, 30, 60,300,300, 300, 600,1200, 3600]

   ralabel = map(lambda a: a/240.,tmplabel) # convert to degrees
   stepra  = map(lambda a: a/240.,tmpstep)  # convert to degrees

   tmp = abs(ra[1] - ra[0])
   guess = tmp/6. # aim for about 6 labels
   diff  = [abs(guess-a) for a in ralabel]
   idx   = diff.index(min(diff))

   return stepra[idx],ralabel[idx]

def _getstepdeg(deg):
   """Get step size and label size for a range of degrees plotted.  This is 
      computed when coordinates will be printed as decimal degrees.

      deg is a list of two values in degrees

      return stepsize and labelsize in degrees"""

   tmpstep  = [0.5,0.10,0.05,0.05,0.01]
   tmplabel = [1.0,0.50,0.25,0.10,0.05]
   
   diff = abs(deg[1] - deg[0])
   guess = [diff/a for a in tmplabel]
   #print deg
   #print diff
   #print guess
   
   for idx in xrange(len(tmpstep)):
      if guess[idx] >= 3:
         break
   return tmpstep[idx],tmplabel[idx]

def _getTickLocs(pixels,coords,stepsize,wcsrange=(0,360)):
   """Get tickmark locations in pixel coordinates."""

   if not np.all(np.diff(coords) > 0):
      header.error("coords passed to _getTickLocs() must be monotonically increasing!")
   minval = np.amin(coords)
   maxval = np.amax(coords)
   tickmark = np.arange(wcsrange[0],wcsrange[1]+stepsize,stepsize)
   mask = np.where((tickmark >= minval) & (tickmark <= maxval))
   tickmark = tickmark[mask]
   tickpix  = np.interp(tickmark,coords,pixels)
   return tickpix,tickmark

def _makelabel_hms(tickmark,step,coord):
   """Convert hms or dms labels to values put on a plot"""

   firstFlag = True # set to false after first wcs on an axis written
   mylabel = []
   for c in tickmark:
      t = c.split(":")
      arcmin = int(t[1])
      arcsec = float(t[2])
      if coord == 'ra':
         if step >= 15: # label every hour.  15 because
            mylabel.append(r"$%s^\mathrm{h}$" %t[0])
         elif step >= 0.25:
            if arcmin == 0: # full hours
               mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}$" %(t[0],t[1]))
            else: # only put arcminutes
               if firstFlag:
                  mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}$     " %(t[0],t[1]))
                  firstFlag = False
               else:
                  mylabel.append(r"$%s^\mathrm{m}$" %(t[1]))
         else:
            if firstFlag:
               mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}%s^\mathrm{s}$         " %tuple(t))
               firstFlag = False
            elif arcmin == 0 and arcsec == 0:
               mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}%s^\mathrm{s}$" %tuple(t))
            elif arcsec == 0: # full arcminutes
               mylabel.append(r"$\mathrm{%s^m%s^s}$" %(t[1],t[2]))
            else:
               mylabel.append(r"$\mathrm{%s^s}$" %(t[2]))
      elif coord == 'dec':
         if step >= 1:
            mylabel.append(r"$%s^\circ$" %t[0]) # full degrees
         elif step >= 1/60.:
            if arcmin == 0: # full degree mark
               mylabel.append(r"$%s^\circ%s'$" %(t[0],t[1]))
            else: # only put arcminutes
               if firstFlag:
                  mylabel.append(r"$%s^\circ%s'$" %(t[0],t[1]))
                  firstFlag = False
               else:
                  mylabel.append(r"$%s'$" %(t[1]))
         else:
            if arcmin == 0 and arcsec == 0:
               mylabel.append(r"$%s^\circ%s'%s''$" %tuple(t))
            elif firstFlag:
               mylabel.append(r"$%s^\circ%s'%s''$" %tuple(t))
               firstFlag = False
            elif arcsec == 0: # full arcminutes
               mylabel.append(r"$%s'%s''$" %(t[1],t[2]))
            else:
               mylabel.append(r"$%s''$" %(t[2]))
   return mylabel

def _makelabel_off(tickmark,tickstep,unit):
   """Make label for offsets"""

   mylabel = []
   if unit == 'do': # label by degrees
      fac = 1
      unit = r"^\circ"
   elif unit == 'mo': # label by arcminutes
      fac = 60
      unit = r"'"
   elif unit == 'so': # label by arcseconds
      fac = 3600
      unit = r"''"
   else:
      header.error("tickmarks._makelabel_off(): unknown unit %s!" %unit)

   # determine number of decimal places for rounding
   tmp = fac*tickstep
   if tmp > 1:
      digits=0
   elif tmp > 0.01:
      digits = 1
   else:
      digits = 2

   for c in tickmark:
      junk = np.around(fac*c,digits)
      #if roundFlag:
      #   junk = int(np.around(fac*c,0))
      #else:
      #   junk = "%g" %(fac*c)
      mylabel.append(r"$%g%s$" %(junk,unit))
   return mylabel

def getcoord(wcs,limits,side='left',unit='hms'):
   """Return two lists of locations (in pixels) and axis labels for the
      given side.

      wcs    - The wcs (as defined by pywcs) used to convert from world coords
               to pixels.
      limits   = tuple/list of xmin,xmax,ymin,ymax as pixel coordinates
                 (defaults to entire image).  Limits must be one-based
                 pixel coordinates
      side     = string.  Either left, right, top, or bottom
      unit     = string.  Controls units of tickmark labels Can be 'deg'
                 (decimal degrees), 'hms' (degrees/minutes/seconds and
                 hours/minutes/seconds, i.e. sexagesimal), 'do', 'mo', 'so'
                 (degrees/arcminutes/arcseconds offset) from crval1,crval2)"""

   xmin = limits[0] - 1
   xmax = limits[1] - 1
   ymin = limits[2] - 1
   ymax = limits[3] - 1

   if side in ('bottom','top'): # top or bottom edge
      pixels = np.arange(xmax,xmin-1,-1) # reverse b/c ra increase to the left
      nx = pixels.shape[0]
      if side == 'bottom': # get RA for every pixel along given side
         ra,dec = wcs.wcs_pix2sky(pixels,[ymin]*nx,0)
      elif side == 'top':
         ra,dec = wcs.wcs_pix2sky(pixels,[ymax]*nx,0)

      if unit == 'hms':
         # find step size given size of image plotted
         stepra,ralabel = _getstepra_hms((ra[0],ra[-1]))

         # find pixel and wcs locations for major and minor tickmarks
         minorpix,minortick = _getTickLocs(pixels,ra,stepra,(0,360))
         majorpix,majortick = _getTickLocs(pixels,ra,ralabel,(0,360))

         # convert degrees to sexagesimal with required precision (returns strings)
         if ralabel < 1/240.: # label steps less than 1 hour-second
            majorwcs = _deg2sex(majortick,'ra',precision=1)
         else:
            majorwcs = _deg2sex(majortick,'ra',precision=0)
         majorwcs.reverse() # reverse so largest RA first

         # format labels for plotting by matplotlib
         majorwcs = _makelabel_hms(majorwcs,ralabel,'ra')
      elif unit == 'deg':
         stepra,ralabel = _getstepdeg((ra[0],ra[-1]))

         # find pixel and wcs locations for major and minor tickmarks
         minorpix,minortick = _getTickLocs(pixels,ra,stepra,(0,360))
         majorpix,majortick = _getTickLocs(pixels,ra,ralabel,(0,360))

         majorwcs = _makelabel_off(majortick,ralabel,'do') # ralabel > 1 for deg labeling
         majorwcs.reverse() # reverse order so positive offset first
      elif unit in ('do','mo','so'):
         crval = wcs.wcs.crval
         ra = np.sign(ra-crval[0])*_angdist(ra,dec,crval[0],dec)
         stepra,ralabel = _getstepdec_dms((ra[0],ra[-1]))
         
         # find pixel and wcs locations for major and minor tickmarks
         minorpix,minortick = _getTickLocs(pixels,ra,stepra,(-180,180))
         majorpix,majortick = _getTickLocs(pixels,ra,ralabel,(-180,180))

         majorwcs = _makelabel_off(majortick,ralabel,unit)
         majorwcs.reverse() # reverse order so positive offset first
      else:
         header.error("tickmarks.getcoord(): unit must be hms, deg, or off!")

      return majorpix[::-1],majorwcs,minorpix # reverse pixel order too
   elif side in ('left','right'): # left or right edge
      # pixels for entire edge
      pixels = np.arange(ymin,ymax+1)
      ny = pixels.shape[0]

      # get declination for every pixel on edge
      if side == 'left':
         ra,dec = wcs.wcs_pix2sky([xmin]*ny,pixels,0)
      elif side == 'right':
         ra,dec = wcs.wcs_pix2sky([xmax]*ny,pixels,0)

      if unit in ('do', 'mo', 'so'):
         crval = wcs.wcs.crval
         dec = np.sign(dec-crval[1])*_angdist(ra,dec,ra,crval[1])

      # find step size given range of declination plotted
      if unit == 'hms':
         stepdec,declabel = _getstepdec_dms((dec[0],dec[-1]))
      elif unit == 'deg':
         stepdec,declabel = _getstepdeg((dec[0],dec[-1]))
      else:
         stepdec,declabel = _getstepdec_dms((dec[0],dec[-1]))
      
      # find pixel and wcs locations for major and minor tickmarks
      minorpix,minortick = _getTickLocs(pixels,dec,stepdec,(-90,90))
      majorpix,majortick = _getTickLocs(pixels,dec,declabel,(-90,90))

      if unit == 'hms':
         # convert degrees to sexagesimal with required precision
         if declabel < 1/3600.: # label steps less than 1 arcsecond
            majorwcs = _deg2sex(majortick,'dec',precision=1)
         else:
            majorwcs = _deg2sex(majortick,'dec',precision=0)

         # format labels for plotting by matplotlib
         majorwcs = _makelabel_hms(majorwcs,declabel,'dec')
      elif unit == 'deg':
         majorwcs = _makelabel_off(majortick,declabel,'do') # declabel > 1 for deg labeling
      elif unit in ('do', 'mo', 'so'):
         majorwcs = _makelabel_off(majortick,declabel,unit)
      else:
         header.error("tickmarks.getcoord(): unit must be hms, deg, or off!")
      return majorpix,majorwcs,minorpix

if __name__ == "__main__":

   xmin = 20
   xmax = 125
   ymin = 25
   ymax = 120

   locs,labels = getcoord("stokesI.fits",limits=[20,125,25,120],side='bottom')
   print locs,labels
   locs,labels = getcoord("stokesI.fits",limits=[20,125,25,120],side='top')
   print locs,labels
   locs,labels = getcoord("stokesI.fits",limits=[20,125,25,120],side='left')
   print locs,labels
   locs,labels = getcoord("stokesI.fits",limits=[20,125,25,120],side='right')
   print locs,labels
