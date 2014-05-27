from . import header

def default(**args):
   '''Set default parameters that will be used for everything in the plot.

      Allowed optional **args:
         color  - a string giving the default color
         font   - a string giving the default font
         size   - a number giving the default size for everything
         style  - a string giving the default line style
         width  - a number giving the default width of lines
         bg     - a string giving the background color for text.  Use 't' for
                  transparent (the default).'''

   _allowed = ['color','font','size','style','width','bg']
   fp = header._wipopen('default',args.keys(),_allowed)
   header._optionsobj.default(fp,**args)
   fp.close()
