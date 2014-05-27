#!/usr/bin/env python

import commands,math,sys
import tempfile,os
import re

def band2wave(band):
   """Given a bandname return the central wavelength in microns as a string"""

   junk = band.lower()
   if   junk == "ir1": return '3.550'
   elif junk == "ir2": return '4.493'
   elif junk == "ir3": return '5.731'
   elif junk == "ir4": return '7.872'
   elif junk == "mp1": return '24.0'
   elif junk == "mp2": return '70.0'
   elif junk == "mp3": return '160.0'
   elif junk == "u"  : return '0.36'  # Johnson
   elif junk == "b"  : return '0.44'  # Johnson
   elif junk == "v"  : return '0.55'  # Johnson
   elif junk == "r"  : return '0.640' # Johnson From Juan Alcala  WFI - ESO
   elif junk == "i"  : return '0.790' # Johnson From Juan Alcala  WFI - ESO
   elif junk == "z"  : return '0.965' # Johnson From Juan Alcala  WFI - ESO
   elif junk == "j"  : return '1.235' # 2mass
   elif junk == "h"  : return '1.662' # 2mass
   elif junk == "ks" : return '2.159' # 2mass
   elif junk == "k"  : return '2.22'  # Johnson
   else:
      error('Unsupported band %s. Try U,B,V,R,I,Z,J,H,Ks,K,IR1-IR4,MP1-MP3' %band)

def check_exist(*files):
   """Given an input file name as a string or a list of filenames will check to
      make sure each file exists.  If not, a fatal error will occur using
      error"""

   if len(files) == 0:
      error('You must pass at least one argument to check_existance()!')   
   for f in files:
      if isinstance(f,str): # check a single filename
         if not os.path.exists(f):
            t = os.path.split(f)[1]
            error('Required file %s is missing!' %f)
      elif isinstance(f,(list,tuple)): # a list or tuple
         for a in f:
            if not os.path.exists(a):
               t = os.path.split(a)[1]
               error('Required file %s is missing!' %t)
      else:
         error('check_existance() can only check types str,list, and tuple!')
      
def check_nonexist(*files):
   """Given an input file list, will check to make sure each files does NOT
      exist.  If any one of the files exists, a fatal error will occur
      using error"""
   
   if len(files) == 0:
      error('You must pass at least one argument to check_existance()!')   
   for f in files:
      if isinstance(f,str): # check a single filename
         if os.path.exists(f):
            t = os.path.split(f)[1]
            error('File %s already exists!' %f)
      elif isinstance(f,(list,tuple)): # a list
         for a in f:
            if os.path.exists(a):
               t = os.path.split(a)[1]
               error('File %s already exists!' %t)
      else:
         error('check_nonexistance() can only check tyles str,list, and tuple!')

def createtemp(mode='w',dir=None,suffix=None,delete=False):
   """Create temporary file.  Returns a file pointer.  The name can be 
   retrieved via fp.name. Default dir is cwd()."""
   
   if dir is None:
      if suffix is None: # workaround for bug in tempfile
         suffix = ''
      fp = tempfile.NamedTemporaryFile(mode=mode,dir=os.getcwd(),suffix=suffix,
         delete=delete)
   else:
      fp = tempfile.NamedTemporaryFile(mode=mode,dir=dir,suffix=suffix,
         delete=delete)
   return fp
   
def createtempname(mode='w',dir=None,suffix=None,delete=True):
   """Create a temporary filename.  Returns a string with name.  File does
      NOT exist. Default dir is cwd()."""
   
   if dir is None:
      if suffix is None: # workaround for bug in tempfile
         suffix = ''
      fp = tempfile.NamedTemporaryFile(mode=mode,dir=os.getcwd(),suffix=suffix,
         delete=delete)
   else:
      fp = tempfile.NamedTemporaryFile(mode=mode,dir=dir,suffix=suffix,
         delete=delete)
   name = fp.name
   fp.close()
   return name

def error(text):
   """Print a string of text as a fatal error and quit"""
   sys.stderr.write("### Fatal Error! %s\n" %text)
   sys.exit()

def flux2mag(flux,unc,band):
   """Converts input flux (in mJys) to a magnitude and uncertainty"""
   F0 = _findfzero(band)   # Zero flux in Jansky's
   try:
      m  = 2.5*math.log10(F0*1000.0/float(flux))
      dm = 2.5*float(unc)/(math.log(10)*float(flux))
   except ZeroDivisionError:
      m  = 99.0
      dm = 99.0
   except ValueError: # means flux was < 0
      m  = 99.0
      dm = 99.0
   return m,dm

def func(x,pars,fit):
   '''Return a list of y values given x values, using pars and the fit type.
   
      Used in conjunction with tabnllsqfit'''
      
   if fit == 'line':
      y = map(lambda a: pars[0][0] + pars[1][0]*a,x)
   elif fit == 'gauss1d':
      y = map(lambda a: pars[0][0] + pars[1][0]*math.exp(-(a-pars[2][0])**2/(2*pars[3][0]**2)),x)
   return y

def inside(px,py,datax=None,datay=None,out=False,mask=False):
   """Determine which data points, datax,datay, are inside the polygon specified
      by vertices px,py.
      
      Returns data points inside region as a 1D or 2D array(s), depending on how
      data was input.  Can also return data points outside region if out keyword
      is set to True.
      
      If mask is set to true, the mask itself is returned instead of the data

      All coordinates must be given in pixels.
      
      If two arguments are specified, then the first is assumed to be a 2-D
      numpy array of polygon vertices and the second argument is assumed to
      be a 2D array of data points.
      
      3 arguments = px, py are 1D arrays of polygon vertices, datax is a 2D
      array of data points.
      
      4 arguments = px,py,datax,datay are all 1D numpy arrays"""
   
   ncol = px.shape[0]
   polyx = ones(ncol+1)
   polyy = ones(ncol+1)
   if datax is None and datay is None:
      nrow = py.shape[0]
      d0 = py[:,0]
      d1 = py[:,1]
      polyx[:-1] = px[:,0]
      polyx[-1]  = px[0,0]
      polyy[:-1] = py[:,1]
      polyy[-1]  = py[0,1]
   elif datax is not None and datay is None:
      nrow = datax.shape[0]
      d0 = datax[:,0]
      d1 = datax[:,1]
      polyx[:-1] = px
      polyx[-1]  = px[0]
      polyy[:-1] = py
      polyy[-1]  = py[0]
   else:
      nrow = datax.shape[0]
      d0 = datax
      d1 = datay
      polyx[:-1] = px
      polyx[-1]  = px[0]
      polyy[:-1] = py
      polyy[-1]  = py[0]

   # tile and broadcast to 2D arrays
   X1 = tile(polyx[:-1],(nrow,1)) - ones(ncol)*d0[:,newaxis]
   X2 = tile(polyx[1:],(nrow,1))  - ones(ncol)*d0[:,newaxis]
   Y1 = tile(polyy[:-1],(nrow,1)) - ones(ncol)*d1[:,newaxis]
   Y2 = tile(polyy[1:],(nrow,1))  - ones(ncol)*d1[:,newaxis]

   theta = abs(sum(arctan2(X1*Y2 - Y1*X2,X1*X2 + Y1*Y2),1))
   mask1 = where(theta > pi)
   if out is True:
      mask2 = where(theta <= pi)
      if mask is True:
         return mask1,mask2
      elif datax is None and datay is None:
         return py[mask1],py[mask2]
      elif datax is not None and datay is None:
         return datax[mask1],datax[mask2]
      else:
         return datax[mask1],datay[mask1],datax[mask2],datay[mask2]
   else:
      if mask is True:
         return mask1
      elif datax is None and datay is None:
         return py[mask1]
      elif datax is not None and datay is None:
         return datax[mask1]
      else:
         return datax[mask1],datay[mask1]
   
def j2000(ra,dec):
   """Compute J2000 coordinates of input B1950 ones"""
   
   data = commands.getoutput("skycoor %s %s fk4" %(str(ra),str(dec))).split()
   return data[0],data[1]

def mag2flux(mag,dmag,band):
   """Converts input mag to flux and dflux (in mJys)"""
   F0 = _findfzero(band)
   flux  = F0*1000.0 * 10**(-1*float(mag)/2.5)
   dflux = 0.4*math.log(10)*flux*float(dmag)
   return flux,dflux

def nlcopen(filename,fmt='r'):
   '''Attempt to open a file for reading or writing.  Checks for existance of
      file and also understands a dash to be stdin/stdout and a period to be
      /dev/null'''
   if fmt == 'r':
      if filename == '-':
         fp = sys.stdin
      elif os.path.exists(filename):
         fp = open(filename,'r')
      else:
         error('Filename "%s" does not exist for reading!' %filename)
   elif fmt in ('w','w!','a'):
      if filename == '-':
         fp = sys.stdout
      elif filename == '.':
         fp = open('/dev/null','w')
      elif fmt == 'w':
         if os.path.exists(filename):
            error('Output file "%s" already exists!' %filename)
         fp = open(filename,'w')
      elif fmt == 'w!':
         fp = open(filename,'w')
      elif fmt == 'a':
         fp = open(filename,'a')
   else:
      error('Invalid format string for nlcopen.  Try r,w,w!,or a.')
   return fp

class progressbar:
   def __init__(self,text,maxval):
      '''Create a new progress bar instance'''
      self._msgtext  = text
      self._stepsize = 100.0/maxval
      self._percent  = 0.0
      self._backspace = '\b\b\b\b'
      sys.stderr.write("%s %3d%%" %(self._msgtext,int(self._percent)))
      
   def update(self,size):
      '''Update the current percent complete for this progress bar'''
      if (size*self._stepsize > self._percent):
         self._percent = self._percent + self._stepsize
         sys.stderr.write("%s%3d%%" %(self._backspace,int(self._percent)))
   def finish(self):
      '''Ensure progress bar finished at 100%'''
      sys.stderr.write("%s%3d%%\n" %(self._backspace,100))

def readcolumns(filename,col,dtype='str',comment='#'):
   '''Reads a file and return a list(s) for a given
      column number(s).  will automatically convert values to integers, floats,
      or leave as strings based on value paramerter.  The first column is
      1.'''

   if dtype not in ('str','int','float'):
      error('value parameter must be str, int, or float!')
      
   data = readdata(filename,comment)

   if isinstance(col,(str,int)):
      x = int(col) - 1
      tmp = [line[x] for line in data]
      if dtype == 'int':
         tmp = map(int,tmp)
      elif dtype == 'float':
         tmp = map(float,tmp)
   elif isinstance(col,(list,tuple)):
      tmp = []
      for i in col:
         x = int(i) - 1
         junk = [line[x] for line in data]
         if dtype == 'int':
            junk = map(int,junk)
         elif dtype == 'float':
            junk = map(float,junk)
         tmp.append(junk)
   else:
      error('col must be a string, integer, list, or tuple!')
   return tmp   

def readdata(filename,comment='#',split=True,dtype=str):
   """Read a data file, ignore all the comment lines, and split lines
      
      filename - name of filename to read
      comment  - ignore parts of lines after this character (set to None
                 to use the entire line)
      split    - If true, split each line by whitespace before appending"""

   # set null comment strings to something that can be used by partition()
   if comment is None:
      comment = '\n'
   elif comment == '':
      comment = '\n'

   fp = nlcopen(filename)
   if split:
      tmp  = [line.partition(comment)[0].split() for line in fp]
      data = [map(dtype,a) for a in tmp if len(a) > 0]
   else:
      tmp  = [line.partition(comment)[0].strip() for line in fp]
      data = [dtype(a) for a in tmp if len(a) > 0]
   fp.close()
   return data

def readRegion(region):
   """Read a region keyword given as xmin:xmax,ymin:ymax and check for limits
      and valid integers"""
      
   if region is None:
      return None
   else:
      if len(region) == 0:
         return None
      tmp1 = region[0].split(':')
      tmp2 = region[1].split(':')
      if len(tmp1) != 2 or len(tmp2) != 2:
         error('Specify region keyword as xmin:xmax,ymin:ymax')
      try:
         xmin = int(tmp1[0]) - 1
         if xmin < 0:
            error('xmin must be >= 1 for region keyword')
      except ValueError:
         if tmp1[0] == 'xmin':
            xmin = 0
      try:
         xmax = int(tmp1[1])
         if xmax < 1:
            error('xmax must be >= 1 for region keyword')

      except ValueError:
         if tmp1[1] == 'xmax':
            xmax = int(header['naxis1'])
         else:
            error('Specify region keyword as xmin:xmax,ymin:ymax')

      try:
         ymin = int(tmp2[0]) - 1
         if ymin < 0:
            error('ymin must be >= 1 for region keyword')
      except ValueError:
         if tmp2[0] == 'ymin':
            ymin = 0
      try:
         ymax = int(tmp2[1])
         if ymax < 1:
            error('ymax must be >= 1 for region keyword')
      except ValueError:
         if tmp2[1] == 'ymax':
            ymax = int(header['naxis2'])
         else:
            error('Specify region keyword as xmin:xmax,ymin:ymax')
      return xmin,xmax,ymin,ymax

def remove(*files):
   """Delete file(s).  Will also remove the files listed inside an @file."""
   
   for f in files:
      if isinstance(f,str): # delete single filename
         if f[0] == '@':
            if os.path.exists(f[1:]):
               data = readdata(f[1:])
               for g in data:
                  _deleteit(g[0])
               _deleteit(f[1:])
         else:
            _deleteit(f)
      elif isinstance(f,(list,tuple)): # delete a list of files given as strings
         for g in f:
            _deleteit(g)
      else:
         error('remove() can only handle types str,list, and tuple!')

def smart_sort(a, b):
    "Natural string comparison, ignores case."
    ta = a.split()
    tb = b.split()
    xl = map(_try_int, re.findall(r'(\d+|\D+)', ta[0].lower()))
    yl = map(_try_int, re.findall(r'(\d+|\D+)', tb[0].lower()))
    if len(xl) == 1 or len(yl) == 1:
       return cmp(ta[0].lower(),tb[0].lower())
    else:
       return cmp(xl,yl)

def tabbin(cmd):
   """Run tabbin and return output as a dictionary.
   
      Keys are: xvalue, number, x, dx, stdx, y, dy, stdy"""
   
   data = {'xvalue' : [], 'number' : [], 'x' : [], 'dx' : [], 'stdx' : [],
      'y' : [], 'dy' : [], 'stdy' : []}

   junk = commands.getoutput('tabbin %s' %cmd).split('\n')
   for line in junk:
      if line[0] != '#':
         tmp = map(float,line.split())
         data['xvalue'].append(tmp[0])
         data['number'].append(tmp[1])
         data['x'].append(tmp[2])
         data['dx'].append(tmp[3])
         data['stdx'].append(tmp[4])
         data['y'].append(tmp[5])
         data['dy'].append(tmp[6])
         data['stdy'].append(tmp[7])
   return data
   
def tabnllsqfit(cmd):
   '''Run nemo's tabnllsqfit and return the best-fit parameters'''
   
   data = {}
   junk = commands.getoutput('tabnllsqfit %s' %cmd).split('\n')
   for line in junk:
      if line.startswith('### Fatal error'):
         print junk
         error('Unable to fit, try different intial parameter estimates!')
      for c in ('a','b','c','d','e'):
         if line.startswith('%s=' %c):
            bob = line.split()
            data[c] = map(float,bob[1:])
   return data

def warning(text):
   """Print a string of text as a warning"""
   sys.stderr.write("### Warning! %s\n" %text)

### Private functions ###

def _findfzero(band):
   """Convert bandname to F0 value in Jansky's and return it"""
   junk = band.lower()
   if   junk == 'u':   F0 = 1823 # Johnson
   elif junk == 'b':   F0 = 4130 # Johnson
   elif junk == 'v':   F0 = 3781 # Johnson
   elif junk == 'r':   F0 = 3080 # Johnson From Juan Alcala
   elif junk == 'i':   F0 = 2550 # Johnson From Juan Alcala
   elif junk == 'z':   F0 = 2620 # Johnson From Juan Alcala
   elif junk == "j":   F0 = 1594 # 2MASS
   elif junk == "h":   F0 = 1024 # 2MASS
   elif junk == "ks":  F0 = 666.7 # 2MASS
   elif junk == 'ir1': F0 = 280.9 # Spitzer
   elif junk == 'ir2': F0 = 179.7 # Spitzer
   elif junk == 'ir3': F0 = 115.0 # Spitzer
   elif junk == 'ir4': F0 =  64.13 # Spitzer
   elif junk == 'mp1': F0 = 7.140 # Spitzer
   elif junk == 'mp2': F0 = 0.775 # Spitzer
   elif junk == 'mp3': F0 = 0.159 # Spitzer
   else:
      print 'Invalid band "%s".  Try U,B,V,R,I,Z,J,H,Ks,IR1,IR2,IR3,IR4,MP1,MP2,MP3' %band
      sys.exit()
   return F0

def _deleteit(name):
   """Delete directories and files.  Helper function for remove()"""
   if os.path.exists(name):
      if os.path.isdir(name):
         os.system('rm -rf %s' %name)
      else:
         os.remove(name)

def _try_int(s):
    "Convert to integer if possible.  Helper function for smart_sort()"
    try: return int(s)
    except: return s
