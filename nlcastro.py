#!/usr/bin/env python

import pyfits
import numpy
import nlclib

def coord(ra,dec,dist,angle=0):
   """Returns new ra,dec a given dist away from the input ra,dec in the given
      angle.
      
      ra,dec - As a sexagesimal string or degrees
      dist   - In arcseconds
      angle  - In degrees, east of north.  Note, this is astronomers east,
               which points to the left."""
               
   ra1  = sex2deg(ra,'ra')
   dec1 = sex2deg(dec,'dec')
   
   fac = numpy.pi/180.0
   shiftdec = dist/3600.0 * numpy.cos(angle*fac)
   shiftra  = dist/3600.0 * numpy.sin(angle*fac)
   dec2 = dec1 + shiftdec
   
   temp = numpy.cos(dist/3600.*fac) - numpy.sin(dec1*fac)*numpy.sin(dec2*fac)
   temp = temp/(numpy.cos(dec1*fac)*numpy.cos(dec2*fac))
   if temp > 1: # account for rounding errors
      temp = 0.0
   else:
      temp = numpy.arccos(temp)/fac
   if shiftra < 0:
      temp = -1*temp
   ra2 = ra1 + temp
   return ra2,dec2

def deg2sex(value,coord):
   '''Convert degrees to sexagesimal, unless it is already in sexagesimal
   
      Returns a tuple of HMS or DMS, depending on if coord is 'ra' or not.'''
   
   try:
      tmp = map(float,str(value).split(':'))
   except ValueError:
      nlclib.error('Invalid string given for conversion to sexagesimal: %s' %value)

   n = len(tmp)
   if n == 1: # assume it was in degrees
      junk = tmp[0]
      if coord == 'ra':
         junk = junk/15.0
      hours = int(junk)
      junk = 60*(numpy.abs(junk) - numpy.abs(hours))
      minutes = int(junk)
      junk = 60*(junk - minutes)
      seconds = float(junk)
      tmp[0] = hours
      tmp.append(minutes)
      tmp.append(seconds)
   elif n == 2: # assume it was already sexagesimal, but no seconds given
      tmp.append(0.0)
   return tmp

def distance(ra1,dec1,ra2,dec2):
   """Compute the angular distance between two points, in degrees"""
   
   tmp = numpy.pi/180.
   dist = numpy.cos(tmp*dec1)*numpy.cos(tmp*dec2)*numpy.cos(tmp*(ra1-ra2))
   dist = dist + numpy.sin(tmp*dec1)*numpy.sin(tmp*dec2)
   dist = numpy.arccos(dist)/tmp
   return dist

def findExt(fname,extname):
   """Try to match extname, which is a either an integer or string, with
      the extension in fname (the filename as a string)
      
      returns the extension number as an integer (starting from zero)"""
   
   if isinstance(fname,str): # string with filename, so open
      img = pyfits.open(fname)
   elif isinstance(fname,pyfits.HDUList):
      img = fname
   else:
      nlclib.error("findExt(): fname must be a string or pyfits.HDUList")
   n = len(img) # number of HDUs

   # first check if string of a integer, e.g. '1'
   try:
      ext = int(extname)
   except:
      ext = extname
   
   if isinstance(ext,int):
      if 1 <= ext <= n:
         tmp = ext - 1
      else:
         img.close()
         nlclib.error("Extension number must be in range %d-%d for %s!" %(1,n,img.filename()))
   elif isinstance(ext,str):
      ext = ext.lower()
      junk = [img[i].header['extname'].strip().lower() for i in xrange(1,n)]
      if 'EXTNAME' in img[0].header.keys():
         junk.insert(0,img[0].header['extname'].strip().lower())
      else:
         junk.insert(0,'primary')
      if ext in junk:
         tmp = junk.index(ext)
      else:
         img.close()
         nlclib.error("Extension name '%s' not found in %s!" %(ext,img.filename()))
   elif isinstance(ext,(list,tuple)):
      tmp = []
      for tmpext in ext:
         blah = findExt(img,tmpext)
         tmp.append(blah)
   else:
      img.close()
      nlclib.error("Extension must be an integer or string!")
   if isinstance(fname,str): # string with filename, so close
      img.close()
   return tmp

def meanangle(theta,dtheta):
   """This will compute the Equal Weight Stokes Mean (Li et al. 2006) of a 
      set of polarization vectors"""
      
   cost = numpy.cos(numpy.pi/90.*theta)
   sint = numpy.sin(numpy.pi/90.*theta)
   q  = cost
   u  = sint
   dq = numpy.pi/90.*numpy.abs(sint)*dtheta
   du = numpy.pi/90.*numpy.abs(cost)*dtheta

   dq = numpy.sqrt(numpy.sum(dq**2))/dq.shape[0]
   du = numpy.sqrt(numpy.sum(du**2))/du.shape[0]
   q  = q.mean()
   u  = u.mean()

   angle  = 90./numpy.pi*numpy.arctan2(u,q)
   dangle = 90./numpy.pi*numpy.sqrt(q**2*dq**2 + u**2*du**2)/(q**2 + u**2)
   order  = numpy.sqrt(q**2 + u**2)
   if angle < 0:
      angle = angle + 180
   return angle,dangle,order

def sex2deg(value,ctype):
   '''Convert sexagesimal to degrees, unless it is already in degrees'''

   if isinstance(value,str): # is a string
      tmp     = numpy.array(map(float,value.split(':')),dtype=numpy.float32)
      tmpsign = numpy.sign(tmp[0])
      fac     = 60**numpy.arange(tmp.shape[0],dtype=numpy.float32)
      degrees = tmpsign*numpy.sum(numpy.abs(tmp)/fac)
      if ctype == 'ra' and len(tmp) > 1: # first value is ra, multiply by 15
         degrees = 15*degrees # convert hours to degrees
   elif isinstance(value,(float,int)): # assume it is already in degrees
      degrees = value
   else: # assume it is a list,tuple, or array
      degrees = [sex2deg(a,ctype) for a in value]
   return degrees
