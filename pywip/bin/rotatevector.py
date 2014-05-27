#!/usr/bin/env python

from readcmd import ReadCmd

spec = """# Rotate vectors to account for WCS curvature
          in   = ???     # Input file
          cols = 1,2,3,5 # Columns for ra,dec,polarization percent,angle
          out  = ???     # Output file of x,y,polarization percent, new angle
          fits = ???     # FITS image
          ext  = 0       # Extension number for fits file"""

arg = ReadCmd(spec)
image  = arg.getstr('fits',exist=True)
infile = arg.getstr('in',exist=True)
cols   = arg.getlistint('cols',length=4)
outfile= arg.getstr('out',exist=False)
ext    = arg.getint('ext')

cols = map(lambda a: a-1,cols) # convert cols to a zero-based column numbers

import worldpos

from numpy import loadtxt,savetxt,sin,cos,pi,arctan,column_stack
import pyfits

# read CDELT from FITS header to pick an appropriate distance for scaling
fp = pyfits.open(image,mode='readonly')
cdelt = abs(float(fp[ext].header['cdelt2'])) # cdelt in degrees
scale = 5*cdelt
fp.close()

data0 = loadtxt(infile,usecols=cols,comments='#')
if len(data0.shape) == 1: # only 1 line in file, so upgrade to 2-d array b/c
   data0.shape = (1,data0.size) # numpy doesn't seem to do this by default
data0[:,3] = pi/180.*data0[:,3] # convert angles to radians

wcs = worldpos.getwcs(image,ext=ext)
data1 = worldpos.sky2xy(data0[:,0],data0[:,1],wcs)
data0[:,1] = data0[:,1] + scale # move dec's north by length amounts
data2 = worldpos.sky2xy(data0[:,0],data0[:,1],wcs)

# convert to numpy array with x,y in different columns
data1 = column_stack(data1)
data2 = column_stack(data2)

# make positions relative to initial position, so we can rotate around those 
# points.
data2 = data2 - data1

# rotate x,y
sintmp = sin(data0[:,3])
costmp = cos(data0[:,3])
tmp = data2[:,0]*costmp - data2[:,1]*sintmp
data2[:,1] = data2[:,0]*sintmp + data2[:,1]*costmp
data2[:,0] = tmp

# compute new angle
# angles are measured east of north, so -x should have +angle
theta = 180./pi*arctan(-1*data2[:,0]/data2[:,1])

data0[:,:2] = data1[:,:2] # put initial x,y positions instead of ra,dec
data0[:,3] = theta # update angle

# write out file
savetxt(outfile,data0,fmt='%f')
