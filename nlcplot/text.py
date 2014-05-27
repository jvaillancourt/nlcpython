from . import header

def text(x,y,text,**args):
   """Place text

      x,y    - coordinates for placement of text
      text   - string containing text

      Supported optional arguments:
      angle  - text angle (defaults to 0 deg.)
      bg     - background color of text box
      color  - color of text
      coord - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
              offset), mo (arcminutes offset), so (arcseconds offset).
              Pixels start at 1.
      font   - font family
      halign - horizontal alignment
      size   - font size
      valign - vertical alignment
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
      width  - font weight (thickness)"""

   a = header.translateArgs(**args)
   z = header.updateZorder()

   x2,y2 = header.translateCoords(x,y,a['coord'],a['wcs'])

   header.plt.text(x2,y2,text,color=a['color'],family=a['family'],
      fontsize=a['fontsize'],fontweight=a['fontweight'],rotation=a['rotation'],
      va=a['va'],ha=a['ha'],backgroundcolor=a['backgroundcolor'],zorder=z)
