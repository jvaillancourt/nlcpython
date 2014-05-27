from . import header

def poly(xcol,ycol,datafile=None,fill='s',**args):
   '''Draw a closed polygon.

      xcol,ycol - either an integer, list, or tuple for x/y data points
      datafile  - string name of input data file.  Leave as None if
                  xcol and ycol are a sequence of numbers
      fill      - Fill style for polygon, defaults to solid
      Allowed optional **args:
         color     - string with color to use for line style
         style     - string with line style to draw polygon with
         width     - Line width of polygon
         fillcolor - color to fill polygon with.  Defaults to color.
         limits    - If None, set min/max to values in xcol and ycol.  If a list
                     or tuple of xmin,xmax,ymin,ymax, set to specified values.
                     If anything else, do not attempt to set any limits (i.e.
                     assume they have already been set to something sensible)
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.'''

   _allowed = ['color','style','width','fillcolor','limits','logx','logy']
   fp = header._wipopen('poly',args.keys(),_allowed)
   if not datafile:
      datafile = header._maketempfile(xcol,ycol)
      xcol = 1
      ycol = 2
   if fill != 'h':
      if args.has_key('fillcolor'):
         pass
      elif args.has_key('color'):
         args['fillcolor'] = args['color']
      else:
         args['fillcolor'] = header._colors[int(header._optionsobj.color)]

   header._panelobj.set(**args)
   fp.write('data %s\n' %datafile)
   fp.write('xcol %d\n' %xcol)
   fp.write('ycol %d\n' %ycol)
   if header._panelobj.get('logx'): fp.write('log x\n')
   if header._panelobj.get('logy'): fp.write('log y\n')
   header._panelobj.writelimits(fp,**args)
   header._optionsobj.update(fp,**args)
   if args.has_key('fillcolor'):
      header._optionsobj.update(fp,color=args['fillcolor'])
      fillstyle = header._translatefill(fill)
      fp.write('fill %s\n' %fillstyle)
      fp.write('poly\n')
      header._optionsobj.update(fp,color=args['fillcolor'])
   header._optionsobj.update(fp,**args)
   fp.write('fill %s\n' %header._translatefill('h'))
   fp.write('poly\n')
   header._optionsobj.reset(fp,**args)
   fp.close()
