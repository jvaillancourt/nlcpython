from . import header

def bin(xcol,ycol,datafile=None,coord='center',**args):
   '''Draw a histogram from previously histogrammed data.

      xcol,ycol - either an integer specifying column in datafile or a
                  list/tuple of x/y data points
      datafile  - string containing filename with data.  Leave as None if
                  xcol and ycol are tuples/lists
      coord     - are x coordinates the center or left side of the bin?
      Allowed optional **args:
         color     - the color for the histogram
         style     - line style for histogram
         width     - the thickness of the histogram
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.
         text      - A string that can be used for the legend command.  Defaults
                     to None (don't add to legend).'''

   if not args.has_key('style'):
      args['style'] = '-'
   if args.has_key('text'):
      if args['text'] is not None:
         header._makecurve(**args)
   _allowed = ['color','style','width','limits','logx','logy','text']
   fp = header._wipopen('bin',args.keys(),_allowed)
   if   coord == 'center': k = 1
   elif coord == 'left':   k = 0
   else: header._error('bin(): coord must be either center or left.')

   if not datafile:
      datafile = header._maketempfile(xcol,ycol)
      xcol = 1
      ycol = 2
   header._panelobj.set(**args)
   fp.write('data %s\n' %datafile)
   fp.write('xcol %d\n' %xcol)
   fp.write('ycol %d\n' %ycol)
#   fp.write('ecol 0\n') # reset ecol (color) to nothing.
   header._panelobj.writelimits(fp,**args)
   if header._panelobj.get('logx'): fp.write('log x\n')
   if header._panelobj.get('logy'): fp.write('log y\n')
   header._optionsobj.update(fp,**args)
   fp.write('bin %d\n' %k)
   header._optionsobj.reset(fp,**args)
   fp.close()
