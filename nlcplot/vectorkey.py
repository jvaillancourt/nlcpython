from . import header

def vectorkey(x,y,length,text,**args):
   """Plot a vector key (which could be a polarization key).
   
      TODO: In the future this should probably be renamed to vectorlegend()
      
      This will only plot a key based on the last stick() or vector() command.
      x,y    - floats specifying location
      length - float giving length of vector (scale factor is the same as
               specified for the last stick() or vector() command.
      text   - string describing reference vector
      
      Supported optional arguments:
      coord - Input coordinates for x,y.  Set to one of: pix, deg, do (degrees
              offset), mo (arcminutes offset), so (arcseconds offset).
              Pixels start at 1.
      color  - color of text label
      size   - font size
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted)."""
   
   a     = header.translateArgs(**args)
   Q     = header._fig['quiver']
   scale = header._fig['scale']
   x2,y2 = header.translateCoords(x,y,a['coord'],a['wcs'])
   
   header.plt.quiverkey(Q,x2,y2,length*scale,text,coordinates='data',
      labelcolor=a['color'],fontproperties={'size' : a['fontsize']})
