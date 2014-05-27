from . import header

def ylabel(text, side='left', offset=0, **args):
   """Put y-axis label
      
      text   - string of text to place
      side   - location of label.  Either left or right
      offset - Offset for y label added to default offset

      Supported optional arguments:
      angle  - text angle.  Defaults to vertical
      color  - text color
      font   - text style
      size   - text size
      width  - text width (boldness)
      halign - horizontal alignment (defaults to center)
      malign - Not sure
      valign - vertical alignment"""

   a = header.translateArgs(**args)
   z = header.updateZorder()

   #if not args.has_key('size'): # no font size defined, use default
   #   a['fontsize'] = 'small'
   if not args.has_key('valign'): # if no valign defined, use default
      a['va'] = 'center'
   if not args.has_key('halign'): # if no valign defined, use default
      a['ha'] = 'center'
   if not args.has_key('angle'):
      a['rotation'] = 'vertical'
   
   header.plt.ylabel(text,color=a['color'],family=a['family'],
      fontsize=a['fontsize'],fontweight=a['fontweight'],rotation=a['rotation'],
      va=a['va'],ha=a['ha'],multialignment=a['multialignment'],zorder=z)
   if side == 'right':
      ax = header.plt.gca()
      ax.yaxis.set_label_position("right")
   
   ax = header.plt.gca()
   ax.yaxis.labelpad = ax.yaxis.labelpad + offset
