from . import header

def panel(idx,**args):
   '''Switch to panel idx.

      The nx,ny (and optionally gapx,gapy, and start) parameters should only
      be set for the first call to panel().  Thereafter, those values will be
      remembered.

      There are nx,ny panels in a grid.  The space between panels in the
      x and y directions is controlled by gapx and gapy.  By default, panels
      are counted from the top left going across, then down.  To start at
      the bottom left going across and up, set the start keyword to 'bottom'.


      idx   - Current panel number, (starts counting at 1)
      Optional **args:
         nx    - Number of panels in x direction (defaults to 1)
         ny    - Number of panels in y direction (defaults to 1)
         gapx  - space between panels in the x direction (defaults to 2)
         gapy  - space between panels in the y direction (defaults to 2)
         start - Panel number 1 will be at the top-left ('top') or bottom-left
                 ('bottom').  Defaults to 'top' '''

   _allowed = ['nx','ny','gapx','gapy','start']
   fp = header._wipopen('panel',args.keys(),_allowed)
   if args.has_key('nx') and args.has_key('ny'): # start new panels
      header._panelobj.resize(**args)
      fp.write('set xsubmar %f\n' %header._panelobj.gapx)
      fp.write('set ysubmar %f\n' %header._panelobj.gapy)
   elif args.has_key('nx') or args.has_key('ny'):
      header._error('panel(): you must specify nx and ny!')
   if idx not in range(1,header._panelobj.nx*header._panelobj.ny+1):
      header._error('panel(): idx must be between 1 and nx*ny!')
   header._panelobj.idx = idx - 1
   if header._panelobj.start == 'top':
      fp.write('panel %d %d %d\n' %(header._panelobj.nx,header._panelobj.ny,-1*idx))
   else:
      fp.write('panel %d %d %d\n' %(header._panelobj.nx,header._panelobj.ny,idx))
   fp.write('color %s\n'  %header._optionsobj.color)
   fp.write('font %s\n'   %header._optionsobj.font)
   fp.write('expand %s\n' %header._optionsobj.size)
   fp.write('lstyle %s\n' %header._optionsobj.lstyle)
   fp.write('lwidth %s\n' %header._optionsobj.lwidth)
   fp.write('bgci %s\n'   %header._optionsobj.bg)
   fp.close()
