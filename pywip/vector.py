from . import header
from . import stick
import tempfile
import math

def vector(xcol,ycol,anglecol,lengthcol,datafile=None,taper=45,vent=0.0,
   fill='s',scale=1,start=90,align='left',**args):
   '''Draw a vector field.

      lengthcol is a column with the length of each arrow and anglecol is the
      angle for each arrow, in degrees.  Zero degrees +x, and angles increase
      counter-clockwise.

      xcol,ycol - either an integer, list, or tuple for x/y data points
      anglecol  - either an integer, list, or tuple for direction of arrows.
                  Note, angles are expected to be degrees counter-clockwise from
                  the +x axis.  The normal convention for polarization is 
                  degrees counter-clockwise from North.
      lengthcol - either an integer, list, or tuple for length of arrows
      datafile  - string name of input data file.  Leave as None if
                  xcol,ycol,pcol,ecol are a sequence of numbers
      taper     - tapering angle, in degrees, for the arrowheads (0-180)
      vent      - fraction of each arrowhead that is cut-away in the back.
      fill      - fill style for arrow heads
      scale     - lengths of vectors are multiplied by this scale factor
      start     - starting angle from +x that corresponds to zero.  The default
                  of 90 means that zero degrees is the +y axis.  This is the
                  normal convention in polarization maps.
      align     - 'left' = xcol,ycol are ends of arrows, 'center' = xcol,ycol
                  are center of arrows, 'right' = xcol,ycol are tips of arrows.
                  Currently, it seems that changing this from the default only
                  works for RA,DEC world coordinate systems.
      Allowed optional **args:
         color     - string with color for each arrow
         size      - Size of arrows
         style     - string with line style to draw sticks with
                     (may only work for taper=0)
         width     - Line width of arrows
         limits    - If None, set min/max to values in xcol and ycol.  If a list
                     or tuple of xmin,xmax,ymin,ymax, set to specified values.
                     If anything else, do not attempt to set any limits (i.e.
                     assume they have already been set to something sensible)
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.
         text      - A string that can be used for the legend command.  Defaults
                     to None (don't add to legend).'''

   _allowed = ['color','size','style','width','limits','logx','logy','text']
   fp = header._wipopen('vector',args.keys(),_allowed)
   if not args.has_key('style'): # defaults to default line style
      args['style'] = header._lstyles[int(header._optionsobj.lstyle) - 1]
   if args.has_key('text'):
      if args['text'] is not None:
         if args['taper'] != 0.0:
            args['style'] = 'arrow'
         header._makecurve(**args)
   fillstyle = header._translatefill(fill)
   if taper == 0:
      stick.stick(xcol,ycol,anglecol,lengthcol,datafile,scale,start,align,**args)
   else:
      if not datafile: # if no data file, scale lengths and convert coords
         n1 = len(xcol)
         n2 = len(ycol)
         n3 = len(anglecol)
         n4 = len(lengthcol)
         if n1 != n2 or n1 != n3 or n1 != n4:
            header._error('vector(): In vector, xcol, ycol, anglecol, and lengthcol must all have the same number of elements!')
         x = [header._translatecoords(i,'ra') for i in xcol]
         y = [header._translatecoords(i,'dec') for i in ycol]
         l = [scale*i for i in lengthcol]
         a = [start+i for i in anglecol]
      else: # if there is a datafile, read in and scale
         x = []
         y = []
         l = []
         a = []
         fp2 = open(datafile,'r')
         for line in fp2:
            if line[0] != '#':
               t = line.split()
               x.append(float(t[xcol-1]))
               y.append(float(t[ycol-1]))
               l.append(scale*float(t[lengthcol - 1]))
               a.append(start+float(t[anglecol - 1]))
         fp2.close()
      # now write out new file with length's scaled, and aligned center or right
      junkfile = tempfile.mktemp()
      header._tmplist.append(junkfile)
      fp2 = open(junkfile,'w')
      for i in xrange(len(x)):
         if align == 'center':
            x1 = x[i] - 0.5*l[i]*math.cos(math.pi/180.0*a[i])
            y1 = y[i] - 0.5*l[i]*math.sin(math.pi/180.0*a[i])
         elif align == 'right':
            x1 = x[i] - l[i]*math.cos(math.pi/180.0*a[i])
            y1 = y[i] - l[i]*math.sin(math.pi/180.0*a[i])
         else:
            x1 = x[i]
            y1 = y[i]
         fp2.write('%4.4e  %4.4e  %4.4e  %4.4e\n' %(x1,y1,a[i],l[i]))
      fp2.close()
      xcol      = 1
      ycol      = 2
      anglecol  = 3
      lengthcol = 4
      datafile = junkfile

      header._panelobj.set(**args)
      junk = header._panelobj.get('header')
      if junk is not None and junk != 'px': # None means no image defined
         fp.write('header px\n')
         header._panelobj.set(header='px')
      fp.write('data %s\n' %datafile)
      fp.write('xcol %d\n' %xcol)
      fp.write('ycol %d\n' %ycol)
      fp.write('ecol %d\n' %anglecol)
      fp.write('pcol %d\n' %lengthcol)
      if header._panelobj.get('logx'): fp.write('log x\n')
      if header._panelobj.get('logy'): fp.write('log y\n')
      header._panelobj.writelimits(fp,**args)
      header._optionsobj.update(fp,**args)
      fp.write('fill %s\n' %fillstyle)
      fp.write('vector %f %f\n' %(taper,vent))
      header._optionsobj.reset(fp,**args)
      fp.close()
