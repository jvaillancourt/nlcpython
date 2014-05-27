#!/usr/bin/env python
"""Script to generate proper WCS tickmarks in WIP.  WIP assumes the sky is
flat, and so can be off for large fields.  This uses the worldpos module."""

import nlclib
import pywcs,pyfits
from numpy import arange,amin,amax,where,interp,all,diff,pi,sin,cos,arccos,sign

def _convert(value,coord,precision=0):
   """Convert a single value in deg to sexagesimal.  Use in conjunction with
      deg2sex() below.

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
      nlclib.error('Invalid string given for conversion to sexagesimal: %s' %value)

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

def deg2sex(value,coord,precision=0):
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

def angdist(ra1,dec1,ra2,dec2):
   """Compute the angular distance between two points, in degrees

      Note, ra1,dec1,ra2,dec2 can be numpy arrays or individual points"""

   tmp = pi/180.
   dist = cos(tmp*dec1)*cos(dec2)*cos(tmp*(ra1-ra2))
   dist = dist + sin(tmp*dec1)*sin(tmp*dec2)
   dist = arccos(dist)/tmp
   return dist

def getstepdec(dec):
   """Get stepdec and declabel given the range in declination plotted"""

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

def getstepra(ra):
   """Get stepra and ralabel for the range of RA plotted.
      Input ra is two values in degrees"""

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

def getstepoffset(offset,coord):
   """Get stepdec and declabel given the range in declination plotted"""

   # label steps in arcseconds
   offlabel = array([1  ,5,10,15,20,30,60,300,600,900,1200,1800,3600,18000,36000])
   offstep  = array([0.5,1, 5, 5, 5,10,20, 60,300,300, 300, 600,1200, 3600,18000])
   tmp = abs(offset[1] - offset[0])

   if coord == 'so': # arcsecond offset
      tmp = 3600*tmp
   elif coord == 'mo': # arcminute offset
      offlabel = offlabel/60.
      offstep  = offsetep/60.
      tmp = 60*tmp
   elif coord == 'do': # degree offset
      offlabel = offlabel/3600.
      offstep  = offstep/3600.
   else:
      nlclib.error("getstepoffset(): coord keyword must be one of: so, mo, do!")

   guess = tmp/6. # aim for about 6 labels
   diff  = [abs(guess-a) for a in offlabel]
   idx   = diff.index(min(diff))

   return offstep[idx],offlabel[idx]

def getTickLocs(pixels,coords,stepsize,wcsrange=(0,360)):
   """Get tickmark locations in pixel coordinates."""

   if not all(diff(coords) > 0):
      nlclib.error("coords passed to getTickLocs() must be monotonically increasing!")
   minval = amin(coords)
   maxval = amax(coords)
   tickmark = arange(wcsrange[0],wcsrange[1]+stepsize,stepsize)
   mask = where((tickmark >= minval) & (tickmark <= maxval))
   tickmark = tickmark[mask]
   tickpix  = interp(tickmark,coords,pixels)
   return tickpix,tickmark

def makelabel(tickmark,step,coord):
   """Convert hms or dms labels to values put on a plot"""

   firstFlag = True # set to false after first wcs on an axis written
   mylabel = []
   for c in tickmark:
      t = c.split(":")
      amin = int(t[1])
      asec = float(t[2])
      if coord == 'ra':
         if step >= 1: # label every hour
            mylabel.append(r"$%s^\mathrm{h}$" %t[0])
         elif step >= 1/60.:
            if amin == 0: # full hours
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
            elif amin == 0 and asec == 0:
               mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}%s^\mathrm{s}$" %tuple(t))
            elif asec == 0: # full arcminutes
               mylabel.append(r"$\mathrm{%s^m%s^s}$" %(t[1],t[2]))
            else:
               mylabel.append(r"$\mathrm{%s^s}$" %(t[2]))
      elif coord == 'dec':
         if step >= 1:
            mylabel.append(r"$%s^\circ$" %t[0]) # full degrees
         elif step >= 1/60.:
            if amin == 0: # full degree mark
               mylabel.append(r"$%s^\circ%s^'$" %(t[0],t[1]))
            else: # only put arcminutes
               if firstFlag:
                  mylabel.append(r"$%s^\circ%s^'$" %(t[0],t[1]))
                  firstFlag = False
               else:
                  mylabel.append(r"$%s^'$" %(t[1]))
         else:
            if amin == 0 and asec == 0:
               mylabel.append(r"$%s^\circ%s^'%s^{''}$" %tuple(t))
            elif firstFlag:
               mylabel.append(r"$%s^\circ%s^'%s^{''}$" %tuple(t))
               firstFlag = False
            elif asec == 0: # full arcminutes
               mylabel.append(r"$%s^'%s^{''}$" %(t[1],t[2]))
            else:
               mylabel.append(r"$%s^{''}$" %(t[2]))
   return mylabel

def getcoord(fitsfile,ext=0,limits=None,side='left'):
   """Return two lists of locations (in pixels) and axis labels for the
      given side.

      fitsfile = string name of FITS file
      ext      = FITS file extension to read for world coordinate header
      limits   = tuple/list of xmin,xmax,ymin,ymax as pixel coordinates
                 (defaults to entire image).  Limits must be zero-based
                 pixel coordinates
      side     = string.  Either left, right, top, or bottom"""

   head = pyfits.getheader(fitsfile,ext=ext)
   wcs = pywcs.WCS(head)
   if limits is None:
      xmin = 1
      xmax = head['naxis1']
      ymin = 1
      ymax = head['naxis2']
   else:
      xmin = limits[0]
      xmax = limits[1]
      ymin = limits[2]
      ymax = limits[3]

   if side in ('bottom','top'): # top or bottom edge
      pixels = arange(xmax,xmin-1,-1)
      nx = pixels.shape[0]
      if side == 'bottom':
         ra,dec = wcs.wcs_pix2sky(pixels,[ymin]*nx,0)
      elif side == 'top':
         ra,dec = wcs.wcs_pix2sky(pixels,[ymax]*nx,0)
      stepra,ralabel = getstepra((ra[0],ra[-1]))
      minorpix,minortick = getTickLocs(pixels,ra,stepra,(0,360))
      majorpix,majortick = getTickLocs(pixels,ra,ralabel,(0,360))
      if ralabel < 1/240.: # label steps less than 1 hour-second
         majorwcs = deg2sex(majortick,'ra',precision=1)
      else:
         majorwcs = deg2sex(majortick,'ra',precision=0)
      majorwcs.reverse() # reverse so largest RA first
      majorwcs = makelabel(majorwcs,ralabel,'ra')
      return majorpix[::-1],majorwcs # reverse pixel order too
   elif side in ('left','right'): # left or right edge
      pixels = arange(ymin,ymax+1)
      ny = pixels.shape[0]
      if side == 'left':
         ra,dec = wcs.wcs_pix2sky([xmin]*ny,pixels,0)
      elif side == 'right':
         ra,dec = wcs.wcs_pix2sky([xmax]*ny,pixels,0)
      stepdec,declabel = getstepdec((dec[0],dec[-1]))
      minorpix,minortick = getTickLocs(pixels,dec,stepdec,(-90,90))
      majorpix,majortick = getTickLocs(pixels,dec,declabel,(-90,90))
      if declabel < 1/3600.: # label steps less than 1 arcsecond
         majorwcs = deg2sex(majortick,'dec',precision=1)
      else:
         majorwcs = deg2sex(majortick,'dec',precision=1)
      majorwcs = makelabel(majorwcs,declabel,'dec')
      return majorpix,majorwcs

def getcoordoffset(fitsfile,ext=0,limits=None,side='left'):
   """Computes tickmarks as arcsecond offsets from crpix

      Return two lists: locations (in pixels) and axis labels for the
      given side.

      fitsfile = string name of FITS file
      ext      = FITS file extension to read for world coordinate header
      limits   = tuple/list of xmin,xmax,ymin,ymax as pixel coordinates
                 (defaults to entire image)
      side     = string.  Either left, right, top, or bottom"""

   head = pyfits.getheader(fitsfile,ext=ext)
   wcs = pywcs.WCS(head)
   if limits is None:
      xmin = 1
      xmax = head['naxis1']
      ymin = 1
      ymax = head['naxis2']
   else:
      xmin = limits[0]
      xmax = limits[1]
      ymin = limits[2]
      ymax = limits[3]

   nx = xmax - xmin + 1
   ny = ymax - ymin + 1

   if side in ('bottom','top'): # top or bottom edge
      pixels = arange(xmax,xmin-1,-1)
      if side == 'bottom':
         ra,dec = wcs.wcs_pix2sky(pixels,[ymin]*nx,0)
      elif side == 'top':
         ra,dec = wcs.wcs_pix2sky(pixels,[ymax]*nx,0)
      ra0,dec0 = wcs.wcs_pix2sky([head['crpix1']],[ymin],0)
      offset = sign(ra-ra0)*angdist(ra,dec,ra0,dec0)
      stepoff,offlabel = getstepoffset(offset,'so')

      stepra,ralabel = getstepra((ra[0],ra[-1]))
      minorpix,minortick = getTickLocs(pixels,ra,stepra,(0,360))
      majorpix,majortick = getTickLocs(pixels,ra,ralabel,(0,360))
      if ralabel < 1/240.: # label steps less than 1 hour-second
         majorwcs = deg2sex(majortick,'ra',precision=1)
      else:
         majorwcs = deg2sex(majortick,'ra',precision=0)
      majorwcs.reverse() # reverse so largest RA first
      majorwcs = makelabel(majorwcs,ralabel,'ra')
      return majorpix[::-1],majorwcs # reverse pixel order too
   elif side in ('left','right'): # left or right edge
      pixels = arange(ymin,ymax+1)
      if side == 'left':
         ra,dec = wcs.wcs_pix2sky([xmin]*ny,pixels,0)
      elif side == 'right':
         ra,dec = wcs.wcs_pix2sky([xmax]*ny,pixels,0)
      stepdec,declabel = getstepdec((dec[0],dec[-1]))
      minorpix,minortick = getTickLocs(pixels,dec,stepdec,(-90,90))
      majorpix,majortick = getTickLocs(pixels,dec,declabel,(-90,90))
      if declabel < 1/3600.: # label steps less than 1 arcsecond
         majorwcs = deg2sex(majortick,'dec',precision=1)
      else:
         majorwcs = deg2sex(majortick,'dec',precision=1)
      majorwcs = makelabel(majorwcs,declabel,'dec')
      return majorpix,majorwcs

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
