#!/usr/bin/env python

import os,sys,tempfile,string,math,re

_palettes = ('gray','rainbow','heat','iraf','aips','pgplot','a','bb','he','i8','ds','cyclic')

_colors = ('w','k','r','g','b','c','m','y','o','gy','gc','bc','bm','rm','dg','lg')

_fills = ('s','h','/','#')

_fonts = ('sf','rm','it','cu')

_lstyles = ('-','--','.-',':','-...')

_symbols = ('s','.','+','*','o','x','^','oplus','odot','ps','d','st','o+','david','arrow')


# Private variables set by _wipopen().

_wipfile    = '???' # the temporary wip file that holds all the plot commands
_tmplist    = []    # list of any temp files we have made
_optionsobj = None  # set to class _options
_panelobj   = None  # set to class _panel

class _options:
   def __init__(self):
      # Note, these are all defined in the way WIP would use them.
      self.font    = '2'   # default font (roman)
      self.lwidth  = '1'   # default line width
      self.lstyle  = '1'   # default line style (solid)
      self.color   = '1'   # default color (black)
      self.size    = '1'   # default size
      self.bg      = '-1'  # default background text color, i.e. transparent
      self.rgbFlag = False # set to true when rgb values are specified
   def update(self,fp,**sargs):
      '''Write out any options specified by the user'''
      for k in sargs.keys():
         if   k == 'color':
            if isinstance(sargs[k],str):
               tmp = self.rgb(fp,sargs[k])
               fp.write('color %s\n' %tmp)
         elif k == 'font':
            fp.write('font %s\n' %_translatefont(sargs[k]))
         elif k == 'size':
            fp.write('expand %s\n' %sargs[k])
         elif k == 'style':
            if isinstance(sargs[k],str):
               sym = _translatesymbol(sargs[k]) # don't attempt for symbols
               if sym == '99':
                  sym = _translatelstyle(sargs[k])
                  fp.write('lstyle %s\n' %sym)
         elif k == 'width':
            fp.write('lwidth %s\n' %sargs[k])
         elif k == 'bg':
            tmp = self.rgb(fp,sargs[k])
            fp.write('bgci %s\n' %tmp)
   def rgb(self,fp,color):
      '''Handle RGB color conversion'''
      tmp = _translatecolor(color)
      if tmp == 'rgb':
         tmp = color.replace(',',' ')
         fp.write('rgb 1 %s\n' %(tmp)) # change color index 1
         self.rgbFlag = True
         return '1'
      else:
         if self.rgbFlag: # changed index 1, so change back
            fp.write('rgb 1 0 0 0\n')
            self.rgbFlag = False
         return tmp

   def reset(self,fp,**sargs):
      '''Reset any options changed by self.update to their defaults'''
      if self.rgbFlag:
         fp.write('rgb 1 0 0 0\n') # reset color index 1 to black
         self.rgbFlag = False
      for k in sargs.keys():
         if   k == 'color':     fp.write('color %s\n' %self.color)
         elif k == 'fillcolor': fp.write('color %s\n' %self.color)
         elif k == 'font':      fp.write('font %s\n' %self.font)
         elif k == 'size':      fp.write('expand %s\n' %self.size)
         elif k == 'style':     fp.write('lstyle %s\n' %self.lstyle)
         elif k == 'width':     fp.write('lwidth %s\n' %self.lwidth)
         elif k == 'bg':        fp.write('bgci %s\n' %self.bg)
   def default(self,fp,**sargs):
      '''Change the default values'''
      for k in sargs.keys():
         if   k == 'color': self.color  = self.rgb(fp,sargs[k])
         elif k == 'font':  self.font   = _translatefont(sargs['font'])
         elif k == 'size':  self.size   = str(sargs['size'])
         elif k == 'style': self.lstyle = _translatelstyle(sargs['style'])
         elif k == 'width': self.lwidth = str(sargs['width'])
         elif k == 'bg':
            if sargs[k] == 't': # t for transparent
               self.bg = '-1'
            else:
               self.bg = self.rgb(sargs[k])

      self.update(fp,**sargs)

class _panel:
   def __init__(self):
      self.nx    = 0     # number of panels in x direction (set by self.resize)
      self.ny    = 0     # number of panels in y direction (set by self.resize)
      self.idx   = 0     # index of current panel number
      self.gapx  = 2     # space between panels in x
      self.gapy  = 2     # space between panels in y
      self.start = 'top' # control if numbering starts in top or bottom left
      self.limits  = []  # flag whether limits are set for each panel
      self.logx    = []  # flag whether logx is plotted
      self.logy    = []  # flag whether logy is plotted
      self.image   = []  # name of image, if any, for each panel
      self.header  = []  # header for each image (px, rd, etc)
      self.scale   = []  # image scaling for each panel (linear,log,sqrt)
      self.curves  = []  # curves to plot for legend
      self.palette = []  # palette used in each panel
      self.resize(nx=1,ny=1,gapx=2,gapy=2,start='top')

   def get(self,key):
      '''Return the specified value for the current panel'''
      if   key == 'limits' : return self.limits[self.idx]
      elif key == 'logx'   : return self.logx[self.idx]
      elif key == 'logy'   : return self.logy[self.idx]
      elif key == 'image'  : return self.image[self.idx]
      elif key == 'scale'  : return self.scale[self.idx]
      elif key == 'header' : return self.header[self.idx]
      elif key == 'palette': return self.palette[self.idx]
      else: _warning('_panel(): Invalid key requested: %s' %key)

   def writelimits(self,fp,**args):
      """New function for limits"""
      if args.has_key('logx'): self.logx[self.idx] = args['logx']
      if args.has_key('logy'): self.logy[self.idx] = args['logy']
      if args.has_key('limits') and args['limits'] == None:
         del(args['limits'])
      if args.has_key('limits'):
         if args['limits'] == 'last': # use last set limits from other panel
            idx = self.idx - 1
            while idx >= 0:
               if self.limits[idx]:
                  self.limits[self.idx] = self.limits[idx]
                  self.logx[self.idx] = self.logx[idx]
                  self.logy[self.idx] = self.logy[idx]
                  break
               idx = idx - 1
         else:
            tmp = list(args['limits'])
            if self.logx[self.idx]:
               ## TODO: No warning for changing these values
               if tmp[0] == 0: tmp[0] = 1e-5
               if tmp[1] == 0: tmp[1] = 1e-5
               tmp[0] = math.log10(tmp[0])
               tmp[1] = math.log10(tmp[1])
            if self.logy[self.idx]:
               if tmp[2] == 0: tmp[2] = 1e-5
               if tmp[3] == 0: tmp[3] = 1e-5
               tmp[2] = math.log10(tmp[2])
               tmp[3] = math.log10(tmp[3])
            fp.write('set \\1 %g\n' %tmp[0])
            fp.write('set \\2 %g\n' %tmp[1])
            fp.write('set \\3 %g\n' %tmp[2])
            fp.write('set \\4 %g\n' %tmp[3])
            self.limits[self.idx] = True
         fp.write('limits \\1 \\2 \\3 \\4\n')
      elif self.limits[self.idx]: # limits already exist for this panel,
         pass                     # so reuse them
         #fp.write('limits \\1 \\2 \\3 \\4\n')
      else: # no limits set in this panel, so make new ones
         fp.write('limits\n')
         fp.write('set \\1 x1\n')
         fp.write('set \\2 x2\n')
         fp.write('set \\3 y1\n')
         fp.write('set \\4 y2\n')
         if args.has_key('reversex') and args['reversex']:
            fp.write('set \\1 x2\n')
            fp.write('set \\2 x1\n')
         if args.has_key('reversey') and args['reversey']:
            fp.write('set \\1 y2\n')
            fp.write('set \\2 y1\n')
         if self.logx[self.idx]:
            ## TODO: No warning for changing these values
            fp.write('if (\\1 == 0) set \\1 1e-5\n')
            fp.write('if (\\2 == 0) set \\2 1e-5\n')
         if self.logy[self.idx]:
            fp.write('if (\\3 == 0) set \\3 1e-5\n')
            fp.write('if (\\4 == 0) set \\4 1e-5\n')
         self.limits[self.idx] = True
         fp.write('limits \\1 \\2 \\3 \\4\n')

   def resize(self,**args):
      '''Change size of a panel, either newly-created, or from panel() cmd'''
      if args.has_key('gapx'):  self.gapx = args['gapx']
      if args.has_key('gapy'):  self.gapy = args['gapy']
      if args.has_key('start'): self.start = args['start']
      if args.has_key('nx'):
         nx = args['nx']
      else:
         nx = self.nx
      if args.has_key('ny'):
         ny = args['ny']
      else:
         ny = self.ny

      if self.start not in ('top','bottom'):
         _error('_panel(): start keyword must be top or bottom!')
      for i in range(self.nx*self.ny,nx*ny):
         self.limits.append(False)
         self.logx.append(False)
         self.logy.append(False)
         self.image.append(None)
         self.scale.append(None)
         self.header.append(None)
         self.palette.append(None)
      self.nx = nx
      self.ny = ny

   def set(self,**args):
      '''Set the specified value for the current panel'''
      for k,v in args.iteritems():
         if   k == 'logx'   : self.logx[self.idx] = v
         elif k == 'logy'   : self.logy[self.idx] = v
         elif k == 'image'  : self.image[self.idx] = v
         elif k == 'scale'  : self.scale[self.idx] = v
         elif k == 'header' : self.header[self.idx] = v
         elif k == 'curve'  : self.curves.append(v)
         elif k == 'limits' : self.limits[self.idx] = v
         elif k == 'palette': self.palette[self.idx] = v

def _checkallowed(funcname,inputargs,allowedargs):
   '''Check the list of inputargs keywords against the list of allowedargs'''
   
   extra_args = list(set(inputargs) - set(allowedargs))
   if len(extra_args) != 0:
      argstring = ' '.join(extra_args)
      if len(extra_args) == 1:
         _error("%s() does not allow the keyword: %s" %(funcname,argstring))
      else:
         _error("%s() does not allow the keywords: %s" %(funcname,argstring))

def _count(datafile):
   '''Count number of non-comment lines in given datafile and return'''
   if os.path.exists(datafile):
      fp = open(datafile,'r')
      line = fp.readline()
      num = 0
      while line:
         if line[0] != '#':
            num = num + 1
         line = fp.readline()
      fp.close()
      return num
   else:
      _error("_count(): datafile %s does not exist!" %datafile)
      return 0

def _error(msg):
   '''Print the error message to standard error'''
   if msg[-1] == '\n':
      sys.stderr.write('### PyWip Error! %s' %msg)
   else:
      sys.stderr.write('### PyWip Error! %s\n' %msg)
   sys.exit()

def _isseq(var):
   '''Test whether var is a list or tuple'''

   return isinstance(var,(list,tuple))

def _lookup(rcol=1,gcol=2,bcol=3,scol=4,datafile=None,reverse=False):
   '''Define a color palette using RGB values.
   
      Note, the halftone() command can use a lookup table directly through
      the palette keyword.  You probably only really need this command if
      you want to specify a lookup table without a datafile.
      
      The red, green, and blue values must be given as fractions between 0 
      and 1.  Same for the scale column (scol).  scol defines the rgb color
      for fractions of the max values plotted by halftone().  Linear 
      interpolation for values in the image between specified levels will be 
      performed.  I think WIP has an inherent limit of 255 color levels 
      (probably something to do with PGPLOT).
      
      rcol,gcol,bcol - Integers or list/tuple of red, green, blue data
      scol           - Integer or list/tuple of scaling data.
      datafile       - String name of input data file.  Leave as None if
                       rcol,gcol,bcol, and scol are all sequences of numbers
      reverse        - Set to True if you want to invert the color lookup 
                       table (like putting a negative sign for palette).'''
   
   ## TODO: Can probably simplify this a lot by hard-coding some things.
   ## I don't think anyone would ever want to call this manually.
   fp = _wipopen('_lookup')
   if datafile is None:
      nr = len(rcol)
      ng = len(gcol)
      nb = len(bcol)
      ns = len(scol)
      if nr == ng == nb == ns:
         blah = tempfile.mktemp()
         _tmplist.append(blah)
         fp2 = open(blah,'w')
         for r,g,b,s in zip(rcol,gcol,bcol,scol):
            fp2.write("%g  %g  %g  %g\n" %(r,g,b,s))
         fp2.close()
         rcol = 1
         gcol = 2
         bcol = 3
         scol = 4
         datafile = blah
      else:
         _error("_lookup(): You must have equal # of elements for rcol, gcol, bcol, scol!")
   else:
      fp.write("data %s\n" %datafile)
      fp.write("xcol %d\n" %rcol)
      fp.write("ycol %d\n" %gcol)
      fp.write("ecol %d\n" %bcol)
      fp.write("pcol %d\n" %scol)
      if reverse is True:
         fp.write("lookup -1\n")
      else:
         fp.write("lookup\n")
      fp.close()

def _makecurve(**args):
   '''Does all the stuff for adding a curve to the legend().  This does
      NOT check for allowed arguments since this function is called 
      directly by plot() and others which may have additional args.'''

   c = {'color' : _colors[int(_optionsobj.color)], 'size' : _optionsobj.size,
        'style' : _lstyles[int(_optionsobj.lstyle)-1],
        'width' : _optionsobj.lwidth, 'text' : 'Generic Curve',
        'fillcolor' : _optionsobj.bg,
        'fillsize' : _optionsobj.size,
        'fillstyle' : _lstyles[int(_optionsobj.lstyle)-1]}

   if args.has_key('style') and args['style'] == None: # don't add style=None
      return                                           # to legend
   for k in args.keys():
      if k == 'text':
         if args['text']: # not set to None
            c[k] = _translatelatex(args['text'])
         else:
            return # don't add to list of curves for legend
      else:
         c[k] = str(args[k])
   # to properly set fill factor requires all other args to be parsed first
   if args.has_key('fillcolor'):
      fillstyle,fillfactor = _translatefillsymbol(args['style'])
      c['fillcolor'] = c['fillcolor']
      c['fillsize']  = fillfactor*float(c['size'])
      c['fillstyle'] = fillstyle
   _panelobj.set(curve=c)

def _maketempfile(xcol,ycol,datafile=None,xerr=None,yerr=None,**args):
   '''Make a temporary data file for reading by wip.

      xcol  - either an integer (for a column from datafile) or a list/tuple
      ycol  - either an integer (for a column from datafile) or a list/tuple
      xerr  - either an integer (for a column from datafile) or a list/tuple
      yerr  - either an integer (for a column from datafile) or a list/tuple
      datafile - set to a filename to read data from that file'''
   global _tmplist

   eFlag = False # set to true if color for each point
   sFlag = False # set to true if symbol for each point
   fFlag = False # set to true if fillcolor for each point
   
   logx = _panelobj.get('logx')
   logy = _panelobj.get('logy')
   if not datafile:
      if xcol == 'NR':
         xcol = range(len(ycol))
      elif ycol == 'NR':
         ycol = range(len(xcol))
      n1 = len(xcol)
      n2 = len(ycol)
      if n1 != n2: _error('_maketempfile(): x and y arrays must be the same length!')
      if xerr:
         if len(xerr) != n1:
            _error('_maketempfile(): xerr array must have same length as x and y arrays!')
      if yerr:
         if len(yerr) != n1:
            _error('_maketempfile(): yerr array must have same length as x and y arrays!')
      if args.has_key('color') and _isseq(args['color']):
         eFlag = True
         ecol = args['color']
         if len(ecol) != n1:
            _error('_maketempfile(): color array must have same length as x and y arrays!')         
      if args.has_key('style') and _isseq(args['style']):
         sFlag = True
         pcol = args['style']
         if len(pcol) != n1:
            _error('_maketempfile(): style array must have same length as x and y arrays!')
      if args.has_key('fillcolor') and _isseq(args['fillcolor']):
         fFlag = True
         fcol = args['fillcolor']
         if len(fcol) != n1:
            _error('_maketempfile(): fillcolor array must have same length as x and y arrays!')
   elif not os.path.exists(datafile):
      _error('_maketempfile(): file %s does not exist for reading!' %datafile)

   blah = tempfile.mktemp()
   _tmplist.append(blah)
   fp2 = open(blah,'w')

   idx = 0 # counting for cases where xcol or ycol is NR
   if datafile:
      fp1 = open(datafile,'r')
      line = fp1.readline()
      while line:
         if line[0] != '#':
            tmp = line.split()
            if xcol == 'NR':
               xtmp = idx
               idx += 1
            else:
               xtmp = tmp[xcol-1]
            if ycol == 'NR':
               ytmp = idx
               idx += 1
            else:
               ytmp = tmp[ycol-1]
            if _panelobj.get('image') and _panelobj.get('header') == 'rd':
               fp2.write('%6.6e %6.6e ' %(_translatecoords(xtmp,'ra'),
                  _translatecoords(ytmp,'dec')))
            else:
               fp2.write('%s %s ' %(xtmp,ytmp))
            if xerr:
               _maketemphelper(fp2,float(xtmp),float(tmp[xerr-1]),logx)
            if yerr:
               _maketemphelper(fp2,float(ytmp),float(tmp[yerr-1]),logy)
            fp2.write('\n')
         line = fp1.readline()
      fp1.close()
   else:
      for i in range(n1):
         fp2.write('%6.6e %6.6e ' %(_translatecoords(xcol[i],'ra'),
            _translatecoords(ycol[i],'dec')))
         if xerr:
            _maketemphelper(fp2,float(xcol[i]),float(xerr[i]),logx)
         if yerr:
            _maketemphelper(fp2,float(ycol[i]),float(yerr[i]),logy)
         if eFlag:
            fp2.write('%s ' %(_translatecolor(ecol[i])))
         else:
            fp2.write('0 ')
         if sFlag:
            fp2.write('%s ' %(_translatesymbol(pcol[i])))
         else:
            fp2.write('0 ')
         if fFlag:
            fp2.write('%s ' %(_translatecolor(fcol[i])))
         else:
            fp2.write('0 ')
         fp2.write('\n')
   fp2.close()
   return blah

def _maketemphelper(fp,value,error,logFlag):
   '''Helper function for _maketempfile that consolidates the code for making
      errorbars and log errorbars with WIP.  You have to do some extra
      gymnastics to make these happen in WIP.'''
   if logFlag:
      if value == 0:
         fp.write('1 ')
      else:
         fp.write('%6.6e ' %((value+error)/value))
      if value == error:
         fp.write('1 ')
      else:
         # when value-err < 0, this causes the errorbars to be drawn funny
         # due to taking the log of a negative number.  So, we fix
         # by forcing err, the errorbar value to be ~99% of value.  This
         # reduces the value/(value-err) to 99.
         if value - error < 0:
            fp.write('%6.6e ' %99)
         else:
            fp.write('%6.6e ' %(value/(value-error)))
   else:
      fp.write('%s ' %error)

def _mtext(fp,text,offset=0,align='center',side='top',**args):
   '''Combine stuff for using mtext, which is used by xlabel(), ylabel(),
      and title()
      text   - a string of text
      offset - offset for text in addition to standard offset (which depends
               on the chosen side).
      align  - alignment for label.  Either left, center, or right, or a
               number between zero and one. (zero=left, one=right).
      side   - put text on this side.  Options are left, right, top, bottom.
      Allowed optional **args:
         color  - a string giving the color for the title
         font   - a string giving the font to use for the title
         size   - a number giving the size for the title
         style  - a string giving the line style for the title
         width  - a number giving the width of the lines
         bg     - background color for text'''
   al = _translatealign(align)
   if side == 'top':
      off = str(2.0 + float(offset))
   elif side == 'left':
      off = str(2.2 + float(offset))
   elif side == 'right':
      off = str(2.2 + float(offset))
   elif side == 'bottom':
      off = str(3.2 + float(offset))
   else:
      _error('_mtext(): Side keyword must be one of: top, bottom left, right!')

   # doesn't seem to properly pick-up default parameters that are set, so
   # we force them to be written out. TODO: Still a problem?
   #_optionsobj.reset(fp,color=1,font=1,size=1,style=1,width=1,bg=1)
   # Now override defaults
   _optionsobj.update(fp,**args)
   fp.write('mtext %c %s 0.5 %s %s\n' %(side[0].upper(),off,al,_translatelatex(text)))
   _optionsobj.reset(fp,**args)

def _plotpoints(fp,xlist,ylist,**args):
   '''Plot data points from input lists of coordinates.

      This function is a helper to the plot command.  When there are less
      than 10 data points, plot will call this function rather than go through
      the process of making a temp file.  Like plot(), you can show points
      and lines.

      fp        - The file pointer where wip commands are written
      xlist,ylist - Lists or tuples with the x and y positions of points to
                  plot
      Allowed optional **args:
         color - If a string, use as the color for every point.  If an integer,
                 read that column from the datafile for color index for each
                 point.
         size  - The size for each data point.
         style - If a string, use as the symbol or line style.  If an integer,
                 then read from datafile for symbol for each point.
         width - Line width'''

   _panelobj.set(**args)
   _optionsobj.update(fp,**args)
   if _panelobj.get('logx'):
      for i in range(len(xlist)):
         try:
            xlist[i] = math.log10(xlist[i])
         except ValueError:
            _error("_plotpoints(): problem with taking log of %f" %xlist[i])
   if _panelobj.get('logy'):
      for i in range(len(ylist)):
         try:
            ylist[i] = math.log10(ylist[i])
         except ValueError:
            _error("_plotpoints(): problem with taking log of %f" %ylist[i])
   _panelobj.writelimits(fp,**args)
   if args.has_key('style'):
      if args['style'] == None: # skip plotting if style=None
         return
      else:
         sym = _translatesymbol(args['style'])
   else:
      sym = _translatesymbol('o')
   if sym == '99':
      line = _translatelstyle(args['style'])
      fp.write('lstyle %s\n' %line)
      fp.write('move %f %f\n' %(_translatecoords(xlist[0],'ra'),_translatecoords(ylist[0],'dec')))
      for i in range(1,len(xlist)):
         fp.write('draw %f %f\n' %(_translatecoords(xlist[i],'ra'),_translatecoords(ylist[i],'dec')))
      _optionsobj.reset(fp,**args)
   else:
      fp.write('symbol %s\n' %sym)
      for a,b in zip(xlist,ylist):
         fp.write('move %f %f\n' %(_translatecoords(a,'ra'),_translatecoords(b,'dec')))
         fp.write('dot\n')
      _optionsobj.reset(fp,**args)

def _readimage(fp,image):
   '''Perform image and subimage commands on a given image name.

      Return x and y pixel limits as a tuple.'''

   blah = re.findall(r'(\(|\[){1}',image)
   if len(blah) == 0:
      name = image
   else:
      name = image[:image.index(blah[0])]
   subimage = re.findall(r'\[.*\]',image) # get subimage pixels
   planenum = re.findall(r'\([0-9]*\)',image) # get plane number

   if len(planenum) > 1:
      _error('_readimage(): found more than one plane number!')
   elif len(planenum) == 1:
      planenum = int(planenum[0][1:-1])
   else:
      planenum = 1

   if os.path.exists(name):
      fp.write('image %s %d\n' %(name,planenum))
   else:
      _error('_readimage(): Image %s does not exist!' %name)

   if len(subimage) > 1:
      _error('_readimage(): found more than one subimage range!')
   elif len(subimage) == 1:
      blah = subimage[0][1:-1].split(',') #[1:-1] splits off [] at begin/end
      if len(blah) != 2:
         _error('_readimage(): You must specify image range as [xmin:xmax,ymin:ymax]!')
      try:
         blah = tuple(map(int,blah[0].split(':') + blah[1].split(':')))
      except ValueError:
         _error('_readimage(): Image range must be integer pixel values!')
      if len(blah) != 4:
         _error('_readimage(): You must specify image range as [xmin:xmax,ymin:ymax]!')
      fp.write('subimage %d %d %d %d\n' %blah)
      return blah
   else:
      return None

def _translatealign(align):
   '''Take useful alignment string and convert to wip format.'''
   if   align == 'left':    return '0.0'
   elif align == 'center':  return '0.5'
   elif align == 'right':   return '1.0'
   else:
      try:
         blah = float(align)
         if blah < 0 or blah > 1:
            _error('_translatealign(): Invalid alignment.  Try left,center,right, or a number')
         return align
      except ValueError:
         _error('_translatealign(): Invalid alignment.  Try left,center,right, or a number')

def _translateaxis(**args):
   """Convert **args into wip format box commands."""

   xaxis = ''
   yaxis = ''
   for k,v in args.iteritems():
      if k == 'box':
         for side in v:
            if   side == 'bottom':  xaxis += 'b'
            elif side == 'top':     xaxis += 'c'
            elif side == 'left':    yaxis += 'b'
            elif side == 'right':   yaxis += 'c'
            else: _error('_translateaxis(): unknown side for box: %s' %side)
      elif k == 'drawtickx': pass # if True, don't do anything since defaults
      elif k == 'drawticky': pass # to draw.  if False, again do nothing
      elif k == 'firstx':
         if not v: xaxis += 'f'
      elif k == 'firsty':
         if not v: yaxis += 'f'
      elif k == 'format':
         if len(v) != 2: _error('_translateaxis(): format must have two values!')
         if   v[0] == 'wcs':  xaxis += 'hz'
         elif v[0] == 'dec':  xaxis += '1'
         elif v[0] == 'exp':  xaxis += '2'
         elif v[0] == 'auto': pass

         else: _error('_translateaxis(): unknown format style: %s' %v[0])
         if   v[1] == 'wcs':  yaxis += 'dz'
         elif v[1] == 'dec':  yaxis += '1'
         elif v[1] == 'exp':  yaxis += '2'
         elif v[1] == 'auto': pass
         else: _error('_translateaxis(): unknown format style: %s' %v[1])
      elif k == 'gridx':
         if v: xaxis += 'g'
      elif k == 'gridy':
         if v: yaxis += 'g'
      elif k == 'logx':
         if v: xaxis += 'l'
      elif k == 'logy':
         if v: yaxis += 'l'
      elif k == 'majortickx':
         if v: xaxis += 't'
      elif k == 'majorticky':
         if v: yaxis += 't'
      elif k == 'number':
         for side in v:
            if   side == 'bottom':  xaxis += 'n'
            elif side == 'top':     xaxis += 'm'
            elif side == 'left':    yaxis += 'n'
            elif side == 'right':   yaxis += 'm'
            else: _error('_translateaxis(): unknown side for number: %s' %side)
      elif k == 'subtickx':
         if v: xaxis += 's'
      elif k == 'subticky':
         if v: yaxis += 's'
      elif k == 'tickstyle':
         if len(v) != 2: _error('_translateaxis(): drawtick must have two values!')
         if   v[0] == 'inside':     pass # the default
         elif v[0] == 'outside':    xaxis += 'i'
         elif v[0] == 'both':       xaxis += 'p'
         else: _error('_translateaxis(): unknown tickstyle location: %s' %v[0])

         if   v[1] == 'inside':     pass # the default
         elif v[1] == 'outside':    yaxis += 'i'
         elif v[1] == 'both':       yaxis += 'p'
         else: _error('_translateaxis(): unknown tickstyle location: %s' %v[1])
      elif k == 'verticaly':
         if v: yaxis += 'v'
      elif k == 'xinterval': pass
      elif k == 'yinterval': pass
      elif k == 'zerox':
         if not v: xaxis += 'o'
      elif k == 'zeroy':
         if not v: yaxis += 'o'
   if xaxis == '': xaxis = '0'
   if yaxis == '': yaxis = '0'
   return xaxis,yaxis

def _translatecolor(col):
   '''Take useful color string and convert to wip format.

      Note that for k and w, I assume you have changed your PGPLOT_BACKGROUND
      and PGPLOT_FOREGROUND colors so that black and white are switched.'''
   try:
      return str(list(_colors).index(col))
   except ValueError:
      junk = str(col)
      if junk.startswith('gray'):
         try:
            junk2 = int(junk[4:])
            if junk2 not in range(1,101):
               _error('_translatecolor(): Invalid gray index "%s"' %col)
            junk2 = round((junk2-1)*2.4141 + 16) # interpolate to 16-255
            return junk2
         except ValueError:
            _error('_translatecolor(): Invalid gray color name "%s"' %col)
      else:
         tmp = junk.split(',')
         if len(tmp) == 3: # see if rgb color code
            return 'rgb'
         else:
            _error('_translatecolor(): Invalid color name "%s"' %col)

def _translatecoords(text,coord):
   '''Translate ra/dec coordinates into ones useful for WIP'''
   if isinstance(text,str): # if a string, assume we have ra/dec coords
      tmp = text.split(':')
      mul = 3600.0
      outval = 0
      for x in tmp:
         outval = outval + abs(mul*float(x))
         mul = mul/60.0
      if float(tmp[0]) < 0:
         outval = -1*outval
      if len(tmp) == 1: # didn't split by :, so assume user input degrees
         if coord == 'ra':
            outval = outval/15.0 # convert arcseconds to hour-seconds
      return outval
   else: # If user didn't give a string, assume coordinates are okay as-is
      return text

def _translatefill(fill):
   '''Take useful fill string and convert to wip format.

      This is the type of fill string used for boxes.  For filled symbols,
      see below.'''
   try:
      return str(list(_fills).index(fill)+1)
   except ValueError:
      _error('_translatefill(): Invalid fill style %s.  Try s,h,/, or #.' %fillstr)

def _translatefillsymbol(style):
   '''Translate a symbol style into a fill style (later retranslated by
      _translatesymbol).  This is for filled symbols.  For filling of boxes, see
      above'''
   if   style == 'o':  fillstyle = 'fo'
   elif style == '^':  fillstyle = 'f^'
   elif style == 's':  fillstyle = 'fs'
   elif style == 'st': fillstyle = 'fst'
   else: _error('_translatefillsymbol(): Only circles, triangles, squares, and five-point stars can have a fill color!')

   if fillstyle in ['fo','fs']:
      fillfactor = 1.4
   elif fillstyle == 'fst':
      fillfactor = 0.8
   else:
      fillfactor = 0.8

   return fillstyle,fillfactor

def _translatefont(fontname):
   '''Translate a useful font name into wip.'''
   try:
      return str(list(_fonts).index(fontname)+1)
   except ValueError:
      _error('_translatefont(): Invalid font %s.  Try rm, it, sf, or cu!' %fontname)

def _translatelatex(latex):
   '''Translate latex string into something usable by WIP.'''

   greeklatex = (r'\alpha',r'\beta',r'\xi',r'\delta',r'\epsilon',r'\phi',
      r'\gamma',r'\theta',r'\iota',r'\kappa',r'\lambda',r'\mu',r'\nu',r'\pi',
      r'\psi',r'\rho',r'\sigma',r'\tau',r'\upsilon',r'\omega',r'\chi',r'\eta',
      r'\zeta',r'\Xi',r'\Delta',r'\Phi',r'\Gamma',r'\Theta',r'\Lambda',r'\Pi',
      r'\Psi',r'\Sigma',r'\Upsilon',r'\Omega')
   wiplatex = (r'\ga',r'\gb',r'\gc',r'\gd',r'\ge',r'\gf',r'\gg',r'\gh',r'\gi',
      r'\gk',r'\gl',r'\gm',r'\gn',r'\gp',r'\gq',r'\gr',r'\gs',r'\gt',r'\gu',
      r'\gw',r'\gx',r'\gy',r'\gz',r'\gC',r'\gD',r'\gF',r'\gG',r'\gH',r'\gL',
      r'\gP',r'\gQ',r'\gS',r'\gU',r'\gW')
   stack = [] # keep track of super/subscript stuff

   if _optionsobj.font   == '1':
      defaultfont = r'\fn'
   elif _optionsobj.font == '2':
      defaultfont = r'\fr'
   elif _optionsobj.font == '3':
      defaultfont = r'\fi'
   elif _optionsobj.font == '4':
      defaultfont = r'\fs'
   else:
      _error('_translatelatex(): Invalid default font: %s!' %defaultfont)

   outstr = latex
   for g,w in zip(greeklatex,wiplatex):
      outstr = outstr.replace(g,w)
   i = 0
   outstr = outstr.replace(r'\times',r'\x')
   outstr = outstr.replace(r'\AA','\A')
   outstr = outstr.replace(r'\odot',r'\(2281)')
   outstr = outstr.replace(r'\oplus',r'\(2284)')
   outstr = outstr.replace(r'\pm',r'\(2233)')
   outstr = outstr.replace(r'\geq',r'\(2244)')
   outstr = outstr.replace(r'\leq',r'\(2243)')
   outstr = outstr.replace(r'#',r'\(733)') #wip thinks pound signs are comments
   outstr = outstr.replace(r'\circ',r'\(902)')
   outstr = outstr.replace(r'\propto',r'\(2245)')
   while i < len(outstr):
      if outstr[i:i+2] == '^{':
         outstr = outstr[:i] + r'\u' + outstr[i+2:]
         i = i + 2
         stack.append(r'\d')
      elif outstr[i:i+2] == '_{':
         outstr = outstr[:i] + r'\d' + outstr[i+2:]
         i = i + 2
         stack.append(r'\u')
      elif outstr[i:i+4] == r'\sf{':
         outstr = outstr[:i] + r'\fn' + outstr[i+4:]
         i = i + 4
         stack.append(defaultfont)
      elif outstr[i:i+4] == r'\rm{':
         outstr = outstr[:i] + r'\fr' + outstr[i+4:]
         i = i + 4
         stack.append(defaultfont)
      elif outstr[i:i+4] == r'\it{':
         outstr = outstr[:i] + r'\fi' + outstr[i+4:]
         i = i + 4
         stack.append(defaultfont)
      elif outstr[i:i+4] == r'\cu{':
         outstr = outstr[:i] + r'\fs' + outstr[i+4:]
         i = i + 4
         stack.append(defaultfont)
      elif outstr[i:i+2] == r'\{':
         outstr = outstr[:i] + '{' + outstr[i+2:]
         i = i + 2
      elif outstr[i:i+2] == '\}':
         outstr = outstr[:i] + '}' + outstr[i+2:]
         i = i + 2
      elif outstr[i] == '}':
         try:
            char = stack.pop()
            outstr = outstr[:i] + char + outstr[i+1:]
         except IndexError: # emptystack
            pass
         i = i + 1
      else:
         i = i + 1
   # fix bug where the carat, ^, doesn't render properly with WIP
   outstr = outstr.replace(r'^',r'\(756)')
   return outstr

def _translatelevels(levels,unit):
   '''Translate levels which can be a list, tuple, string, or int into something
      usable by wip'''

   if isinstance(levels,str):
      levs = []
      blah = levels.split(':')
      try:
         blah2 = map(float,blah) # convert to floats
      except ValueError:
         _error('_translatelevels(): Specify levels values as numbers!')
      if len(blah2) == 3:
         if unit == 'step':
            count = int((blah2[1] - blah2[0])/blah2[2])
         elif unit == 'nbin':
            count = blah2[2]
            blah2[2] = (blah2[1] - blah2[0])/blah2[2] # set stepsize
         else:
            count = 39
            blah2[2] = blah2[1]
         if count > 39:
            _error('_translatelevels(): You cannot plot more than 40 contours!')
         elif count < 0:
            _error('_translatelevels(): Number of contour levels is negative!')
         levs = tuple(blah2[0] + n*blah2[2] for n in range(count+1))
      else:
         _error('_translatelevels(): Specify levels as val1:val2:val3 !')
      return ' '.join(map(str,levs))
   elif _isseq(levels):
      if len(levels) > 40:
         _error('_translatelevels(): You cannot plot more than 40 contours!')
      return ' '.join(map(str,levels))
   elif isinstance(levels,int):
      return levels
   else:
      _error('_translatelevels(): You must give a list/tuple, string, or integer for the levels command!')

def _translatepalette(palette):
   '''Translate a useful palette string to wip format.'''

   palettestr = str(palette)
   negFlag = 1 # set to one if we want the reverse palette
   if palettestr[0] == '-':
      negFlag = -1
      palettestr = palettestr[1:]
   if palettestr in _palettes:
      return str(negFlag*(list(_palettes).index(palettestr)+1))
   elif palettestr == 'lookup':
      return 'lookup'
   else:
      if not os.path.exists(palettestr):
         _error('_translatepalette(): Cannot find lookup table %s!' %palettestr)
      return 'lookup'

def _translatelstyle(lstyle):
   '''Translate a useful line style into wip.'''
   try:
      return str(list(_lstyles).index(lstyle)+1)
   except ValueError:
      _error('_translatelstyle(): Invalid line style %s.  Try - , -- , .- , : , or -...' %lstyle)

def _translatesymbol(sym):
   '''Take useful symbol string and convert to wip format.'''
   symbol = str(sym) # ensure we have a string
   if   symbol == 's':     return '0'  # square
   elif symbol == '.':     return '1'  # dot
   elif symbol == '+':     return '2'  # plus sign
   elif symbol == '*':     return '3'  # asterisks
   elif symbol == 'o':     return '4'  # circle
   elif symbol == 'x':     return '5'  # cross
   elif symbol == '^':     return '7'  # triangle
   elif symbol == 'oplus': return '8'  # circle with plus sign
   elif symbol == 'odot':  return '9'  # circle with dot
   elif symbol == 'ps':    return '10' # pointed square
   elif symbol == 'd':     return '11' # diamond
   elif symbol == 'st':    return '12' # five-point star
   elif symbol == 'f^':    return '13' # filled triangle
   elif symbol == 'o+':    return '14' # open plus symbol
   elif symbol == 'david': return '15' # star of david
   elif symbol == 'fs':    return '16' # filled square
   elif symbol == 'fo':    return '17' # filled circle
   elif symbol == 'fst':   return '18' # filled five-point star
   elif symbol == 'arrow': return '29' # an arrow, or \(29)
   else: return '99'

def _vptoxy(fp,x,y,r1,r2):
   '''Convert viewport x/y to physical x/y.

      x/y   - floats of x/y viewport values
      r1,r2 - strings of register names to set holding values'''
   fp.write(r'set %s ((x2 - x1) * (%s - vx1) / (vx2 - vx1)) + x1' %(r1,x))
   fp.write('\n')
   fp.write(r'set %s ((y2 - y1) * (%s - vy1) / (vy2 - vy1)) + y1' %(r2,y))
   fp.write('\n')

def _warning(msg):
   '''Print the warning message to standard error.'''
   if msg[-1] == '\n':
      sys.stderr.write('### PyWip Warning! %s' %msg)
   else:
      sys.stderr.write('### PyWip Warning! %s\n' %msg)

def _wipopen(funcname,keys,allowed):
   '''Open the wip file for writing.  If one does not already exist, start a
      new one
      
      funcname - a string with the name of the calling function
      keys     - a list of the keys given as variable arguments
      allowed  - a list of allowed keys'''

   _checkallowed(funcname,keys,allowed)
   global _wipfile,_optionsobj,_panelobj

   if _wipfile == '???':
      tempfile.tempdir = os.getcwd()
      _wipfile = tempfile.mktemp(suffix='.wip')
      _optionsobj = _options()
      _panelobj = _panel()
      fp = open(_wipfile,'w')
      fp.write('set print ignore\n')
      fp.write('set maxarray 1000000\n') #TODO: does this work?
      fp.write('color %s\n'  %_optionsobj.color)
      fp.write('font %s\n'   %_optionsobj.font)
      fp.write('expand %s\n' %_optionsobj.size)
      fp.write('lstyle %s\n' %_optionsobj.lstyle)
      fp.write('lwidth %s\n' %_optionsobj.lwidth)
      fp.write('bgci %s\n'   %_optionsobj.bg)
      fp.write('### Start %s()\n' %funcname)
   else:
      fp = open(_wipfile,'a')
      fp.write('### Start %s()\n' %funcname)
   return fp

def _xytovp(fp,x,y,r1,r2):
   '''Convert x/y values to viewport values
      x,y   - x and y coordinates as floats
      r1,r2 - strings of registers or variables to set holding values'''
   fp.write(r'set %s ((vx2 - vx1) * (%s - x1) / (x2 - x1)) + vx1' %(r1,x))
   fp.write('\n')
   fp.write(r'set %s ((vy2 - vy1) * (%s - y1) / (y2 - y1)) + vy1' %(r2,y))
   fp.write('\n')
