#!/usr/bin/env python

import matplotlib
matplotlib.use('agg') # non-interactive backend that allows png, ps, pdf
import matplotlib.pyplot as plt
from matplotlib.patches import Arc,Ellipse
import pyfits # to read fits files
from numpy import loadtxt,cos,sin,pi,sqrt,array,arange,isnan,arcsin,arctan2
import tickmarks3
import pywcs
import os
import sys

_options = {'backgroundcolor' : 'none', # background color for text boxes
            'facecolor'  : 'k', 'markerfacecolor' : 'k',
            'edgecolor'  : 'k', 'markeredgecolor' : 'k',
            'color'      : 'k',
            'markersize' :  6,
            'fontsize'   : 'medium',
            'linewidth'  :   1, 'markeredgewidth' : 1,
            'fontweight' : 'normal',
            'alpha'      : 1.0,
            'marker'     : 'o',
            'linestyle'  : '-',
            'fillstyle'  : 'full',
            'va'         : 'center',
            'ha'         : 'left',
            'multialignment' : 'center', # align text in multi-line strings
            'rotation'   : 0,
            'family'     : 'serif',
            'hatch'      : None,
            'lineflag'   : False, # used by plot(). True if plotting a line
            'overhang'   : 0,     # used to cut out a fraction of the back of an arrow
            'coord'      : 'pix', # default coordinate type for x,y
            'wcs'        : None,  # default wcs (means read from _fig)
            'fixed'      : False} # Set to true if lengths of polarization
                                  # vectors should be fixed equal to scale
                                  # parameter instead of being variable
_lstyles = ('-','--','-.',':')

# dictionary containing common info about the plot
_fig = {'quiver' : None, # quiver key returned by quiver() command.  Used to
                         # make quiverkey()
        'scale'  : 1,    # scale factor for length of vectors plotted by
                         # stick() and vector() commands
        'wcs'    : None, # world coordinates of plot.  Set automatically by
                         # halftone and contour if none given (read from input
                         # file.  Format is produced by pywcs
        'zorder': 1,     # increment after every plot command.  Starts at
                         # two so that errorbars are drawn underneath symbols
                         # TODO: should I start at 2 instead of 1?
        'panel' : []     # list of matplotlib axes for all subplots in the
                         # figure.  Used by subplot() to switch between them
                         # the zeroth subplot is always 1,1,1 for plotting
                         # shared xlabel and ylabel
       }

matplotlib.rc('font',family=_options['family']) # set default font for plots

def error(msg):
   '''Print the error message to standard error'''
   if msg[-1] == '\n':
      sys.stderr.write('### NLCPlot Error! %s' %msg)
   else:
      sys.stderr.write('### NLCPlot Error! %s\n' %msg)
   sys.exit()

def eq2gal(ra,dec,wcs):
   """Convert Equatorial (ra/dec) coords to Galactic"""

   equinox = _translateEquinox(wcs)
   ra  = pi/180.*_sex2deg(ra,ctype='ra')
   dec = pi/180.*_sex2deg(dec,ctype='none')
   if equinox.lower() == 'b1950':
      alphag = 192.25 * pi/180.
      deltag = 27.4   * pi/180.
      ellg   = 33.0   * pi/180.
   elif equinox.lower() == 'j2000':
      alphag = 192.85948123 * pi/180.
      deltag = 27.12825120  * pi/180.
      ellg   = 32.9319186   * pi/180.
   else:
      error("eq2gal(): Unknown equinox %s" %equinox)

   gb = arcsin(cos(dec)*cos(deltag)*cos(ra - alphag) + sin(dec)*sin(deltag))
   gl = arctan2(sin(dec) - sin(gb)*sin(deltag),
        cos(dec)*sin(ra - alphag)*cos(deltag)) + ellg

   return 180./pi*gl,180./pi*gb

def gal2eq(gl,gb,wcs):
   """Convert Galactic coords to Equatorial (ra/dec)"""

   equinox = _translateEquinox(wcs)
   gl = pi/180.*_sex2deg(gl,ctype='gal') # ensure in radians
   gb = pi/180.*_sex2deg(gb,ctype='gal') # ensure in radians
   if equinox.lower() == 'b1950':
      alphag = 192.25 * pi/180.
      deltag = 27.4   * pi/180.
      ellg   = 33.0   * pi/180.
   elif equinox.lower() == 'j2000':
      alphag = 192.85948123 * pi/180.
      deltag = 27.12825120  * pi/180.
      ellg   = 32.9319186   * pi/180.
   else:
      error("gal2eq(): Unknown equinox %s" %equinox)

   dec = arcsin(cos(gb)*cos(deltag)*sin(gl - ellg) + sin(gb)*sin(deltag))
   ra  = arctan2(cos(gb)*cos(gl - ellg),sin(gb)*cos(deltag) -
         cos(gb)*sin(deltag)*sin(gl - ellg)) + alphag

   return 180./pi*ra,180./pi*dec

def getdata(image,ext):
   """Get FITS data.  ext can be a string or integer.  Checks for valid
      extension name/number and gets the header using pyfits"""

   if os.path.exists(image):
      img = pyfits.open(image)
      ext = _findExt(img,ext)
      data = img[ext].data
      img.close()
      return data
   else:
      error("getdata(): File '%s' does not exist!" %image)

def getheader(image,ext):
   """Get FITS header.  ext can be a string or integer.  Checks for valid
      extension name/number and gets the header using pyfits"""

   img = pyfits.open(image)
   ext = _findExt(img,ext)
   header = img[ext].header
   img.close()
   return header

def lineStyleToText(style):
   """Translate a line style of -, --, -., or : into a text equivalent and
      return it.  Annoyingly, some matplotlib commands require text versions
      of the linestyle"""

   if style == '-':
      return 'solid'
   elif style == '--':
      return 'dashed'
   elif style == '-.':
      return 'dashdot'
   elif style  == ':':
      return 'dotted'
   else:
      error("lineStyleToText(): Unknown line style '%s'!" %style)

def translateArgs(**args):
   """Translate **args to values used by matplotlib"""

   junk = _options.copy()
   for a in args.keys():
      if a == 'angle':
         junk['rotation'] = args[a]
      elif a == 'bg':
         junk['backgroundcolor'] = args[a]
      elif a == 'color':
         junk['color']           = args[a]
         junk['facecolor']       = args[a]
         junk['markerfacecolor'] = args[a]
         junk['edgecolor']       = args[a]
         junk['markeredgecolor'] = args[a]
      elif a == 'coord':
         junk['coord'] = args[a]
      elif a == 'ecolor':
         junk['edgecolor']       = args[a]
         junk['markeredgecolor'] = args[a]
      elif a == 'fcolor':
         junk['facecolor']       = args[a]
         junk['markerfacecolor'] = args[a]
      elif a == 'fixed':
         junk['fixed'] = args[a]
      elif a == 'font':
         junk['family'] = args[a]
      elif a == 'size':
         junk['markersize'] = args[a]
         junk['fontsize']   = args[a]
      elif a == 'width':
         junk['linewidth']       = args[a]
         junk['fontweight']      = args[a]
         junk['markeredgewidth'] = args[a]
      elif a == 'alpha':
         junk['alpha'] = args[a]
      elif a == 'style':
         if args[a] in _lstyles:
            junk['marker']    = 'None'
            junk['linestyle'] = args[a]
            junk['lineflag']  = True
         else:
            junk['marker']    = args[a]
            junk['linestyle'] = 'None'
      elif a == 'lstyle':
         junk['linestyle'] = args[a]
         junk['lineflag']  = True
      elif a == 'fill':
         junk['fillstyle'] = args[a]
         junk['hatch']     = args[a] # fill style for polygons
      elif a == 'valign':
         junk['va'] = args[a]
      elif a == 'halign':
         junk['ha'] = args[a]
      elif a == 'malign':
         junk['multialignment'] = args[a]
      elif a == 'overhang':
         junk['overhang'] = args[a]
      elif a == 'wcs':
         junk['wcs'] = updateWcs(args[a])
      else: # add anything else as-is
         junk[a] = args[a]
   return junk

def translateCoords(x,y,coord,wcs):
   """Translate coordinates from input system to pixel"""

   wcs = updateWcs(wcs)
   if wcs is None: # if no wcs, return input values no matter what
      if coord != 'pix':
         error('translateCoords(): No wcs defined for coord=%s!' %coord)
      return x,y
   elif coord == 'pix':
      if isinstance(x,(float,int)):
         return x - 1,y - 1
      elif isinstance(x,str):
         try:
            return float(x) - 1, float(y) - 1
         except:
            error("translateCoords(): Cannot read '%s','%s' as pixel coordinates!" %(x,y))
      else:
         xtmp = [a - 1 for a in x]
         ytmp = [a - 1 for a in y]
         if len(xtmp) == 1:
            return xtmp[0],ytmp[0]
         else:
            return xtmp,ytmp
   elif coord in ('deg', 'hms'): # degrees
      ctype = translateCtype(wcs)
      x2 = _sex2deg(x,ctype)
      y2 = _sex2deg(y,'none')
      # TODO: this doesn't work, but seems to be a problem with pywcs
      # EDIT: maybe only when input image has naxis=3.  Even if naxis3 = 1,
      # pywcs seems to panic
      x3,y3 = wcs.wcs_sky2pix(x2,y2,0) # convert degrees to pix
      if x3.shape[0] == 1: # return number instead of array if one value
         return x3[0],y3[0]
      else:
         return x3,y3
   elif coord in ('do','mo','so'): # degrees/arcminutes/arcseconds offset
      # TODO: proper distance offset calculation
      crval = wcs.wcs.crval
      if coord == 'do':
         fac = 1.0
      elif coord == 'mo':
         fac = 60.
      elif coord == 'so':
         fac = 3600.
      x2 = crval[0] + array(x)/(fac*cos(pi/180.*crval[1]))
      y2 = crval[1] + array(y)/fac
      x3,y3 = wcs.wcs_sky2pix(x2,y2,0) # convert degrees to pix
      if x3.shape[0] == 1: # return number instead of array if one value
         return x3[0],y3[0]
      else:
         return x3,y3
   else:
      error("translateCoords(): unknown coord=%s!" %coord)

def translateCtype(wcs):
   """"Translate ctype read from wcs to 'ra' or 'glon'"""

   if wcs is None:
      wcs = _fig['wcs']
   ctype = wcs.wcs.ctype[0] # get ctype, i.e. RA, GLON
   if ctype.startswith('RA'):
      return 'ra'
   elif ctype.startswith('GLON'):
      return 'glon'
   else:
      error("translateCtype(): unknown ctype: %s" %ctype)

def updateWcs(wcs):
   """Update stored wcs and return current wcs"""

   global _fig
   if wcs is not None:
      _fig['wcs'] = wcs

   return _fig['wcs']

def updateZorder():
   """Increment zorder by 0.01 and return it"""

   global _fig

   x = _fig['zorder']
   _fig['zorder'] = _fig['zorder'] + 0.01
   #print "zorder = %f" %x
   return x

def _findExt(img,extname):
   """Try to match extname, which is a either an integer or string, with
      the extension in img (a pyfits hdu)"""

   n = len(img) # number of HDUs
   fname = img.filename()

   if isinstance(extname,int):
      if 1 <= extname <= n:
         tmp = extname - 1
      else:
         img.close()
         error("_findExt(): Extension number must be in range %d-%d for %s!" %(1,n,fname))
   elif isinstance(extname,str):
      junk = [img[i].name.strip().lower() for i in xrange(n)]
      if 'EXTNAME' in img[0].header.keys():
         junk[0] = img[0].header['extname'].strip().lower()
      
      if extname.lower() in junk:
         tmp = junk.index(extname.lower())
      else:
         img.close()
         error("_findExt(): Extension name '%s' not found in %s!" %(extname,fname))
   else:
      img.close()
      error("_findExt(): Extension must be an integer or string!")
   return tmp

def _sex2deg(value,ctype):
   '''Convert sexagesimal to degrees, unless it is already in degrees'''

   if isinstance(value,str): # is a string
      negFlag = 1 # set to -1 if negative declination
      if value.strip()[0] == '-':
         negFlag = -1
      tmp = array(map(float,value.split(':')))
      fac = 60**arange(tmp.shape[0])
      degrees = negFlag*sum(abs(tmp)/fac)
      if ctype == 'ra' and len(tmp) > 1: # first value is ra, multiply by 15
         degrees = 15*degrees # convert hours to degrees
   elif isinstance(value,(float,int)): # assume it is already in degrees
      degrees = value
   else: # assume it is a list,tuple, or array
      degrees = [_sex2deg(a,ctype) for a in value]
   return degrees

def _translateEquinox(wcs):
   """Translate Equinox into simple strings of either B1950 or J2000"""

   if wcs is None:
      return 'J2000'
   equinox = wcs.wcs.equinox
   #print equinox
   if isnan(equinox):
      return 'J2000'
   elif isinstance(equinox,str) and equinox.lower() == 'j2000':
      return 'J2000'
   elif isinstance(equinox,str) and equinox.lower() == 'b1950':
      return 'B1950'
   else:
      try:
         tmp = float(equinox)
         if tmp == 1950.0:
            return 'B1950'
         elif tmp == 2000.0:
            return 'J2000'
         else:
            error("_translateEquinox(): Unknown equinox %s" %equinox)
      except ValueError:
         error("_translateEquinox(): Unknown equinox %s" %equinox)
