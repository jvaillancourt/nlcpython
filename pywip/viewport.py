from . import header

def viewport(xmin,xmax=None,ymin=None,ymax=None):
   '''Use this to set the plot area.

      Sometimes WIP gets this wrong and part of your plot is off the page.
      winadj can alter these values, but only within the bounds of the viewport.

      xmin - either a number or a list/tuple of four numbers
      xmax - leave as None if xmin is a list/tuple
      ymin - leave as None if xmin is a list/tuple
      ymax - leave as None if xmin is a list/tuple'''

   fp = header._wipopen('viewport',[],[])
   if header._isseq(xmin):
      if len(xmin) != 4:
         header._error('viewport(): You must specify four limits as xmin,xmax,ymin,ymax!')
      limits = tuple(xmin)
   else:
      try:
         limits = map(float,(xmin,xmax,ymin,ymax))
      except ValueError:
         header._error('viewport(): You must specify numbers for xmin,xmax,ymin,ymax!')
   fp.write('viewport %f %f %f %f\n' %tuple(limits))
   fp.close()
