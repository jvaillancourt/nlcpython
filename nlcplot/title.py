from . import header

def title(text, **args):
   """Put a title on the plot
      
      text   - string of text to place
      
      Supported optional arguments:
      angle  - text angle.  Defaults to zero degrees (horizontal)
      color  - text color
      font   - text style
      size   - text size
      width  - text width (boldness)
      halign - horizontal alignment.  Defaults to center
      valign - vertical alignment"""

   a = header.translateArgs(**args)
   z = header.updateZorder()

   if not args.has_key('valign'): # if no valign defined, use default
      a['va'] = 'baseline'
   if not args.has_key('halign'): # if no valign defined, use default
      a['ha'] = 'center'
   header.plt.title(text,color=a['color'],family=a['family'],
      fontsize=a['fontsize'],fontweight=a['fontweight'],rotation=a['rotation'],
      va=a['va'],ha=a['ha'],zorder=z)
