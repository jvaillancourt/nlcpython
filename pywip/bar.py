from . import header

def bar(xcol,ycol,datafile=None,fill='s',angle=0,barwidth=None,**args):
   '''Draw a bar chart from previously histogrammed data.

      xcol,ycol - either an integer specifying column in datafile or a
                  list/tuple of x/y data points
      datafile  - string containing filename with data.  Leave as None if
                  xcol and ycol are tuples/lists
      fill      - Fill style for bars, defaults to solid.
      angle     - Angle for bar chart, measured in degrees counter-clockwise
                  from the +x axis.  The only allowed values are 0,90,180,270.
      barwidth  - The width of each bar in units of x or y axis (depending on
                  the angle).  Defaults to a width equal to the spacing of the
                  bars.
      Allowed optional **args:
         color     - the color for the bar(s)
         fillcolor - color of inside of bar.  Defaults to color.  Can be an 
                     integer to specify reading that column number from the 
                     file.
         style     - line style for bars
         width     - the thickness of the lines
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.'''

   if not args.has_key('style'):
      args['style'] = '-'
   if angle not in [0,90,180,270]:
      header._error('bar(): angle must be one of: 0,90,180,270.')
   angle = angle/90 + 1 # convert angle to WIP parameter
   # Find threshhold for WIP
   if angle == 1:
      thresh = 'x1'
   elif angle == 2:
      thresh = 'y1'
   elif angle == 3:
      thresh = 'x2'
   elif angle == 4:
      thresh = 'y2'
   
   #if args.has_key('fillcolor'):
   #   _makecurve(text=text,style='-',width=10,color=args['fillcolor'])
   _allowed = ['color','fillcolor','style','width','limits','logx','logy','text']
   fp = header._wipopen('bar',args.keys(),_allowed)

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
#   fp.write('ecol 0\n') # reset ecol (color) to nothing
   header._panelobj.writelimits(fp,**args)
   if header._panelobj.get('logx'): fp.write('log x\n')
   if header._panelobj.get('logy'): fp.write('log y\n')

   if args.has_key('fillcolor'):
      if isinstance(args['fillcolor'],int):
         fp.write('ecol %d\n' %args['fillcolor'])
      else:
#         fp.write('ecol 0\n')
         header._optionsobj.update(fp,color=args['fillcolor'])
      fillstyle = header._translatefill(fill)
      fp.write('fill %s\n' %fillstyle)
      if barwidth is not None:
         fp.write('bar %d %s %f\n' %(angle,thresh,barwidth))
      else:
         fp.write('bar %d %s\n' %(angle,thresh))
      header._optionsobj.update(fp,color=args['fillcolor'])
   header._optionsobj.update(fp,**args)
   fp.write('fill %s\n' %header._translatefill('h'))
   if barwidth is not None:
      fp.write('bar %d %s %f\n' %(angle,thresh,barwidth))
   else:
      fp.write('bar %d %s\n' %(angle,thresh))
   header._optionsobj.reset(fp,**args)
   fp.close()
