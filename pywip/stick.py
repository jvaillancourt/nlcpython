from . import header
import math

def stick(xcol,ycol,anglecol,lengthcol,datafile=None,scale=1,start=90,
   align='left',**args):
   '''Draw a stick field (i.e. a polarization map, which doesn't really have
      a direction like vectors do).

      lengthcol is a column with the length of each arrow and anglecol is the
      angle for each arrow, in degrees.  Zero degrees is +x, and angles 
      increase counter-clockwise.

      xcol,ycol - either an integer, list, or tuple for x/y data points
      anglecol  - either an integer, list, or tuple for direction of sticks.
                  Note, start below to define where "0" is located.
      lengthcol - either an integer, list, or tuple for length of sticks
      datafile  - string name of input data file.  Leave as None if
                  xcol,ycol,pcol,ecol are a sequence of numbers
      scale     - scale factor for length of sticks
      start     - starting angle from +x that corresponds to zero.  The default
                  of 90 means that zero degrees is the +y axis.  This is the
                  normal convention in polarization maps.
      align     - 'left' = xcol,ycol are ends of sticks, 'center' = xcol,ycol
                  are center of sticks, 'right' = xcol,ycol are tips of sticks.
      Allowed optional **args:
         color     - string with color for each stick
         style     - string with line style to draw sticks with
         width     - Line width of sticks
         limits    - If None, set min/max to values in xcol and ycol.  If a list
                     or tuple of xmin,xmax,ymin,ymax, set to specified values.
                     If anything else, do not attempt to set any limits (i.e.
                     assume they have already been set to something sensible)
         text      - A string that can be used for the legend command.  Defaults
                     to None (don't add to legend).'''

   _allowed = ['color','style','width','limits','text']
   fp = header._wipopen('stick',args.keys(),_allowed)
   if not args.has_key('style'): # defaults to default line style
      args['style'] = header._lstyles[int(header._optionsobj.lstyle) - 1]
   if args.has_key('text'):
      if args['text'] is not None:
         header._makecurve(**args)
   if not datafile:
      n1 = len(xcol)
      n2 = len(ycol)
      n3 = len(anglecol)
      n4 = len(lengthcol)
      if n1 != n2 or n1 != n3 or n1 != n4:
         header._error('stick(): xcol, ycol, anglecol, and lengthcol must all have the same number of elements!')
      if align == 'left':
         x0 = xcol
         y0 = ycol
      else:
         x0 = [0]*n1
         y0 = [0]*n3
      x1 = [0]*n2
      y1 = [0]*n4
      for i in xrange(n1):
         a = math.pi/180.0*(start + anglecol[i])
         if align == 'center':
            l = scale*lengthcol[i]/2.0
         else:
            l = scale*lengthcol[i]
         if align != 'left':
            x0[i] = xcol[i] - l*math.cos(a)
            y0[i] = ycol[i] - l*math.sin(a)
         x1[i] = xcol[i] + l*math.cos(a)
         y1[i] = ycol[i] + l*math.sin(a)
   else:
      fp2 = open(datafile,'r')
      x0 = []
      y0 = []
      x1 = []
      y1 = []
      for line in fp2:
         if line[0] != '#':
            t = line.split()
            x = float(t[xcol-1])
            y = float(t[ycol-1])
            a = math.pi/180.0*(start + float(t[anglecol-1]))
            if align == 'center':
               l = scale*float(t[lengthcol-1])/2.0
            else:
               l = scale*float(t[lengthcol-1])
            if align == 'left':
               x0.append(x)
               y0.append(y)
            else:
               x0.append(x - l*math.cos(a))
               y0.append(y - l*math.sin(a))
            x1.append(x + l*math.cos(a))
            y1.append(y + l*math.sin(a))
      fp2.close()

   header._panelobj.set(**args)
   junk = header._panelobj.get('header')
   if junk is not None and junk != 'px':
      fp.write('header px\n')
      header._panelobj.set(header='px')
   header._panelobj.writelimits(fp,**args)
   header._optionsobj.update(fp,**args)
   line = header._translatelstyle(args['style'])
   fp.write('lstyle %s\n' %line)
   for i in xrange(len(x0)): # draw the sticks
      fp.write('move %f %f\n' %(x0[i],y0[i]))
      fp.write('draw %f %f\n' %(x1[i],y1[i]))
   header._optionsobj.reset(fp,**args)
   fp.close()
