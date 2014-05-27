from . import header
from . import poly

def rect(xmin,xmax,ymin,ymax,fill='s',**args):
   '''Draw a rectangle on the figure.

      This function uses the poly() command behind the scenes.

      xmin,xmax,ymin,ymax - the limits of the rectangle
      fill                - fill style for rectangle
      Allowed optional **args:
         color     - string with color to use for line style
         style     - string with line style to draw rectangle with
         width     - thickness of line used to draw rectangle
         fillcolor - color to fill polygon with
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.'''
   _allowed = ['color','style','width','fillcolor','limits','logx','logy']
   fp = header._wipopen('rect',args.keys(),_allowed)
   fp.close()
   poly([xmin,xmax,xmax,xmin],[ymin,ymin,ymax,ymax],fill=fill,**args)
