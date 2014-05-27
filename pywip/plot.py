from . import header

def plot(xcol,ycol,datafile=None,**args):
   '''Plot data from a file or input lists/tuples.

      This function is extremely versatile and can be used to plot data
      points and lines.  Note that when specifying column numbers from a file,
      columns are counted starting from 1.

      xcol,ycol - either an integer, list, or tuple for x/y data points.  If
                  integers, these are column numbers to read from the specified
                  datafile.
      datafile  - string name of input data file.  Leave as None if
                  xcol and ycol are a sequence of numbers
      Allowed options **args:
         color     - If a string, use as the color for every point.  If an
                     integer, read that column from the datafile for color
                     index for each point.  You can also specify a sequence to
                     have different colors for each point.  This somewhat works,
                     provided number of points > 10.  There are probably other
                     limitations too.  Note that lines cannot have multiple
                     colors (this is a WIP limitation).
         size      - The size for each data point.
         style     - If a string, use as the symbol or line style.  If an
                     integer, then read from datafile for symbol for each point.
         width     - Line width
         fillcolor - Color to fill symbols with.  Only available for five-point
                     stars, squares, circles, and triangles.  If used
                     inappropriately, an error will occur.  Use in the same way
                     as for color keyword.  You can specify an integer, which
                     will then read the specified color from the datafile for
                     each point.  You can also specify a sequence, as for
                     color.
         limits    - If None, set min/max to values in xcol and ycol.  If a list
                     or tuple of xmin,xmax,ymin,ymax, set to specified values.
                     If anything else, do not attempt to set any limits (i.e.
                     assume they have already been set to something sensible)
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.
         text      - A string that can be used for the legend command.  Defaults
                     to None (don't add to legend).'''

   eFlag = False # Set to true if we are reading a column from the file for
                 # a color for each point
   sFlag = False # Set to true if we are reading a column from the file for
                 # a symbol for each point
   fFlag = False # Set to true if we are plotting filled symbols
   
   _allowed = ['color','size','style','width','fillcolor','limits','logx',
               'logy','text']
   fp = header._wipopen('plot',args.keys(),_allowed)
   if args.has_key('fillcolor'):
      fillcolor = args['fillcolor']
      fFlag = True
   if args.has_key('color') and isinstance(args['color'],int):
      eFlag = True
      ecol = args['color']
   if args.has_key('style') and isinstance(args['style'],int):
      sFlag = True
      pcol = args['style']

   if not args.has_key('style'): # defaults is default line style
      args['style'] = header._lstyles[int(header._optionsobj.lstyle) - 1]
   if not args.has_key('width'):
      args['width'] = header._optionsobj.lwidth

   if fFlag:
      if isinstance(args['style'],str):
         fillstyle,fillfactor = header._translatefillsymbol(args['style'])
      if args.has_key('size'):              # fill size must be larger because
         fillsize = fillfactor*args['size'] # filled symbols are smaller than
      else:                                 # regular versions
         fillsize = fillfactor*float(header._optionsobj.size)

   if args.has_key('text'):
      if args['text'] is not None:
         header._makecurve(**args) #stuff for a legend
   if datafile is None:
      if xcol == 'NR':
         num = len(ycol)
         xcol = range(num)
      elif ycol == 'NR':
         num = len(ycol)
         ycol = range(num)
      if header._isseq(xcol) and header._isseq(ycol):
         num = len(xcol)
         if num > 10 or not args.has_key('limits'):
            datafile = header._maketempfile(xcol,ycol,**args)
            xcol = 1
            ycol = 2
            if args.has_key('fillcolor') and header._isseq(args['fillcolor']):
               fillcolor = 5
               fFlag = True
            if args.has_key('color') and header._isseq(args['color']):
               eFlag = True
               ecol = 3
            if args.has_key('style') and header._isseq(args['style']):
               sFlag = True
               pcol = 4
         else:
            header._plotpoints(fp,xcol[:],ycol[:],**args)
            if fFlag:
               header._plotpoints(fp,xcol[:],ycol[:],color=fillcolor,size=fillsize,
                  style=fillstyle,width=args['width'])
      else:
         header._error('plot(): Both xcol and ycol must be sequences when datafile is None!')
   else:
      num = header._count(datafile)
   if num == 0: # datafile is empty
      return
   if xcol == 'NR' or ycol == 'NR':
      datafile = header._maketempfile(xcol,ycol,datafile,**args)
      xcol = 1
      ycol = 2
         
   if datafile is not None:
      if xcol == 0 or ycol == 0: # make sure user doesn't enter zero-based numbers
         header._error('plot(): Column numbers start at 1, not zero!')
      header._panelobj.set(**args)
      fp.write('data %s\n' %datafile)
      fp.write('xcol %d\n' %xcol)
      fp.write('ycol %d\n' %ycol)
      if header._panelobj.get('logx'): fp.write('log x\n')
      if header._panelobj.get('logy'): fp.write('log y\n')
      header._panelobj.writelimits(fp,**args)
      header._optionsobj.update(fp,**args)
      if eFlag:
         fp.write('ecol %d\n' %ecol)
#      else:
#         fp.write('ecol 0\n') # reset ecol (color) to nothing
      if sFlag:
         fp.write('pcol %d\n' %pcol)
         sym = '1'
      elif args['style'] == None: # skip actual plotting if style=None
         return
      else:
         sym = header._translatesymbol(args['style'])
         if sym == '99': # not a symbol so see if it is a line style
            line = header._translatelstyle(args['style'])
      if sym != '99': # plot a symbol instead of a line
         if not sFlag: # i.e. don't read symbols from datafile
            fp.write('symbol %s\n' %sym)
         if eFlag: # read colors for each point from the file
            fp.write('points 1\n')
         else:
            fp.write('points\n')
         header._optionsobj.reset(fp,**args)
         if fFlag:
            fp.write('symbol %s\n' %header._translatesymbol(fillstyle))
            if isinstance(fillcolor,int):
               header._optionsobj.update(fp,size=fillsize)
               fp.write('ecol %d\n' %fillcolor)
               fp.write('points 1\n')
            else:
               header._optionsobj.update(fp,color=fillcolor,size=fillsize)
               fp.write('points\n')
            header._optionsobj.reset(fp,color=fillcolor,size=fillsize)
      else: # plot a line
         fp.write('lstyle %s\n' %line)
         fp.write('connect\n')
         header._optionsobj.reset(fp,**args)
   fp.close()
