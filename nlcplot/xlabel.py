from . import header

def xlabel(text, side='bottom', offset=0, **args):
   """Put x-axis label
      
      text   - string of text to place
      side   - location of label.  Either bottom or top
      offset - Offset for x label added to default offset

      Supported optional arguments:
      angle  - text angle.  Defaults to horizontal
      color  - text color
      font   - text style
      size   - text size
      width  - text width (boldness)
      halign - horizontal alignment
      malign - Not sure
      valign - vertical alignment"""

   a = header.translateArgs(**args)
   z = header.updateZorder()

   if not args.has_key('valign'): # if no valign defined, use default
      a['va'] = 'top'
   if not args.has_key('halign'): # if no valign defined, use default
      a['ha'] = 'center'
   #if not args.has_key('size'):
   #   a['fontsize'] = 'medium'
   header.plt.xlabel(text,color=a['color'],family=a['family'],
      fontsize=a['fontsize'],fontweight=a['fontweight'],rotation=a['rotation'],
      va=a['va'],ha=a['ha'],multialignment=a['multialignment'],zorder=z)
   if side == 'top':
      ax = header.plt.gca()
      ax.xaxis_set_label_position("top")

   ax = header.plt.gca()
   ax.xaxis.labelpad = ax.xaxis.labelpad + offset
