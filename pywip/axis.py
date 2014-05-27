from . import header

def axis(**args):
   '''Draw the axes.

      There are many allowed **args.  Most of the time you can probably get by
      without specifying any of them.  If you need to tweak the plotting of the
      axis, consult the User's Manual for a table of all the keywords.

      Additionally, there are the "standard" optional **args:
         color - the color of the axis as a string
         font  - the font to use for the axis
         size  - the size for numbers on axis
         style - the line style
         width - the thickness of the lines'''

   nx    = header._panelobj.nx # number of panels in x and y directions
   ny    = header._panelobj.ny # used for automatically labelling axes
   image = header._panelobj.get('image') # name of image in panel

   _axis_allowed = ['box','number','tickstyle','format','xinterval',
      'yinterval','drawtickx','drawticky','firstx','firsty','gridx','gridy',
      'logx','logy','subtickx','subticky','majortickx','majorticky',
      'verticaly','zerox','zeroy']
   _allowed = _axis_allowed + ['color','font','size','style','width']
   fp = header._wipopen('axis',args.keys(),_allowed)
   header._optionsobj.update(fp,**args)
   if args.has_key('xinterval'):
      xtick = args['xinterval']
   else:
      xtick = (0,0)
   if args.has_key('yinterval'):
      ytick = args['yinterval']
   else:
      ytick = (0,0)
   if header._isseq(xtick) and len(xtick) == 2:
      pass
   else:
      header._error('axis(): You must provide two arguments for xinterval!')
   if header._isseq(ytick) and len(ytick) == 2:
      pass
   else:
      header._error('axis(): You must provide two arguments for yinterval!')

   if args.has_key('xinterval') or args.has_key('yinterval'):
      fp.write('ticksize %g %g '  %tuple(xtick))
      fp.write('%g %g\n' %tuple(ytick))

   if not args.has_key('box'):
      args['box'] = ('bottom','left','top','right')
   for k in ('logx','logy'):
      if not args.has_key(k):
         if header._panelobj.get(k): args[k] = True
   if not args.has_key('number'):
      args['number'] = []
      # space between panels or on last row
      if header._panelobj.gapy > 0 or header._panelobj.idx/nx == (ny - 1):
         args['number'].append('bottom')
      # space between panels or on first column
      if header._panelobj.gapx > 0 or header._panelobj.idx%nx == 0:
         args['number'].append('left')
   if header._panelobj.get('image'):
      if not args.has_key('format'):
         hd = header._panelobj.get('header')
         if hd == 'rd':
            args['format'] = ['wcs','wcs']
      if not args.has_key('verticaly'):
         args['verticaly'] = True
   if args.has_key('drawtickx') and not args['drawtickx']: # exists and False
      args['subtickx'] = False
      args['majortickx'] = False
   else:
      for k in ('subtickx','majortickx'):
         if not args.has_key(k): args[k] = True
   if args.has_key('drawticky') and not args['drawticky']: # exists and False
      args['subticky'] = False
      args['majorticky'] = False
   else:
      for k in ('subticky','majorticky'):
         if not args.has_key(k): args[k] = True

   xlab,ylab = header._translateaxis(**args)
   fp.write('box %s %s\n' %(xlab,ylab))
   header._optionsobj.reset(fp,**args)
   if args.has_key('xinterval') or args.has_key('yinterval'): # unset tick values
      fp.write('ticksize 0 0 0 0\n')
   fp.close()
