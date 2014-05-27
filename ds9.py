#!/usr/bin/env python
'''Library functions to control ds9 from within python.  This just uses the
xpa access framework for its magic.'''

import os,commands

_zoomlevel = 6
_numframes = 6

def center(window,frame,ra,dec):
   """Centers to a specified RA/DEC region.

      Will also delete all regions in that frame if delete=1.
      window - string with name of ds9 window
      frame  - integer which is the ds9 frame number
      ra     - Right Ascension
      dec    - Declination"""

   os.system("xpaset -p %s frame %s" %(window,frame))
   os.system("xpaset -p %s pan to %s %s wcs" %(window,ra,dec))

def getFrame(window):
   """Return index of current active frame"""
   return commands.getoutput('xpaget %s frame' %window)

def getRegion(window):
   """Return the regions in the window and active frame"""
   return commands.getoutput('xpaget %s regions' %window)

def init(window):
   """Set the zoom level, tile option and match wcs ONCE.  Hopefully, this will
      minimize the memory leaks."""
   for i in range(_numframes):
      os.system("xpaset -p %s frame %s" %(window,i+1))
      os.system("xpaset -p %s zoom to %g" %(window,_zoomlevel))
   os.system("xpaset -p %s tile" %window)
   if _numframes > 1:
      os.system("xpaset -p %s match frames wcs" %window)
      os.system('xpaset -p %s frame 1' %window)

def load(window,frame,fitsfile,scaletype='zscale',cmap='cool',invert=True):
   """Load a fits file into a specific frame

      window   - string with name of ds9 window
      frame    - integer specifying ds9 frame number
      fitsfile - string with name of fits file to load"""

   print "Loading %s in frame %d" % (fitsfile, frame)
   os.system("xpaset -p %s frame %d" %(window,frame))
   cmd='cat "%s" | xpaset %s fits %s' % (fitsfile,window,fitsfile)
   os.system(cmd)
   scale(window,frame,scaletype)
   os.system("xpaset -p %s cmap %s" %(window,cmap))
   if invert is True:
      os.system("xpaset -p %s cmap invert yes" %window)
   else:
      os.system("xpaset -p %s cmap invert no" %window)

def loadAll(window,fitslist):
   """Load all fits files into proper DS9 frames

      window   - a string with the name of the ds9 window.
      fitslist - list of names of fits files to load"""

   setNumFrames(len(fitslist))
   for i in range(_numframes):
      load(window,i+1,fitslist[i])
   os.system('xpaset -p %s wcs format degrees' %window)
   view(window)

def makeRegion(fp,ra,dec,color='green',size=4.0,numbers=False):
   """Takes a c2d data table and writes a region file that
      can be opened with ds9.
      
      fp        - file pointer
      ra,dec    - sequences of ra,dec values
      color     - color of circles
      size      - size of circles in arcseconds
      numbers   - display numbers with circles?"""

   fp.write("# Region file format: DS9 version 3.0\n")
   fp.write('global color=%s font="helvetica 12 normal"' %color)
   fp.write(' select=1 edit=1 move=1 delete=1 include=1')
   fp.write(' fixed=0 source\n')
   for i,p in enumerate(zip(ra,dec)):
      if numbers:
         fp.write('fk5;circle(%lf,%lf,%f") # text={%d}\n' %(p[0],p[1],size,i+1))
      else:
         fp.write('fk5;circle(%lf,%lf,%f")\n' %(p[0],p[1],size))

def region(window,frame,filename,delete=False):
   """Load a ds9 region file in the given frame"""

   os.system("xpaset -p %s frame %d" %(window,frame))
   if delete:
      os.system("xpaset -p %s regions deleteall" %window)
   os.system('xpaset -p %s regions file %s' %(window,filename))

def scale(window,frame,scaletype):
   """Change the scaling in one frame to the specified type
   
      window    - string with name of ds9 window
      frame     - ds9 frame number
      scaletype - string with ds9 scale type"""

   os.system("xpaset -p %s frame %d" %(window,frame))
   if scaletype == 'histeq':
      os.system("xpaset -p %s scale histequ" %window)
      os.system("xpaset -p %s scale mode minmax"%window)
   else:
      os.system("xpaset -p %s scale linear" %window)
      os.system("xpaset -p %s scale mode %s"%(window,scaletype))

def scaleAll(window,scaletype):
   """Change the scaling in all frames to the specified type
   
      window    - string with name of ds9 window
      scaletype - string with ds9 scale type"""

   for i in range(_numframes):
      scale(window,i+1,scaletype)
   view(window)

def setNumFrames(num):
   """Change the number of frames variable _numframes"""

   global _numframes
   _numframes = num

def setZoomLevel(num):
   """Set zoom level to num"""

   global _zoomlevel
   _zoomlevel = _zoomlevel + num

def show(window,frame,ra,dec,delete=False,color='red'):
   """Show a given ra,dec in DS9

      window    - string with name of ds9 window
      frame     - ds9 frame number
      ra,dec    - world coordinates
      delete    - delete pre-existing regions in frame?
      color     - color for ds9 regions.  Does not seem to work"""

   os.system("xpaset -p %s frame %d" %(window,frame))
   if delete:
      os.system("xpaset -p %s regions deleteall" %window)
   os.system("xpaset -p %s regions color %s" % (window,color))
   os.system("xpaset -p %s crosshair %s %s wcs" % (window,ra,dec))
   cmd='''echo "fk5; circle %s %s .02'" | xpaset %s regions''' %(ra,dec,window)
   os.system(cmd)

def showAll(window,ra,dec,delete=False,color='red'):
   """Show a given ra,dec in all frames in DS9"""
   
   for i in range(_numframes):
      show(window,i+1,ra,dec,delete,color)
      center(window,i+1,ra,dec)
   view(window)

def view(window):
   """Final tasks in viewing frames in DS9

      Sets focus to the first frame, and sets cursor to crosshairs and
      locks them to the wcs

      window - string with name of ds9 window"""
    
   os.system("xpaset -p %s frame 1" %window)
   os.system("xpaset -p %s lock crosshairs wcs" %window)

def zoom(window,frame,level):
   """Zoom one DS9 frame in or out X levels
   
      window - string with name of ds9 window
      level  - zoom factor"""

   os.system("xpaset -p %s frame %d" %(window,frame))
   os.system("xpaset -p %s zoom to %f" %(window,level))

def zoomAll(window,nlevs=1):
   """Zoom all DS9 frames in or out X levels
   
      window - string with name of ds9 window
      nlevs  - number of levels to zoom in (+) or out (-)"""

   setZoomLevel(nlevs)
   if _zoomlevel < 1:
      bob = 1.0/abs(_zoomlevel - 2)
   else:
      bob = _zoomlevel
   
   for i in range(_numframes):
      zoom(window,i+1,bob)
   os.system("xpaset -p %s frame 1" %window)
