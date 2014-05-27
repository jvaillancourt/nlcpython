from . import header

def curve(**args):

   '''Add a curve to the list plotted by legend().

      A curve is a dictionary that is set by the plot command and can
      be used with the legend command to make it easier to make legends.  This
      allows you to add an extra curve to those listed by legend() without
      having to call plot().

      Allowed optional **args:
         color - the color for the data
         size  - The size for each data point
         style - line style for the data
         width - the thickness of the line for drawing the curve
         text  - Text to describe the curve
         fillcolor - Color to fill symbols with'''

   _allowed = ['color','size','style','width','text','fillcolor']
   header._checkallowed('curve',args.keys(),_allowed)
   header._makecurve(**args)
