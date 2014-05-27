from . import header

def arc(x,y,xmajor,ymajor,angle=0,theta1=0,theta2=360,**args):
   """Draw an Arc, circle, or ellipse
   
      x,y    - coordinates for center of arc
      xmajor,ymajor - major and minor axes (TODO: MUST be in pixels for now)
      
      Supported optional arguments:
      coord - Input coordinates for x,y.  Set to one of: pix, deg, hms,
              do (degrees offset), mo (arcminutes offset), so (arcseconds 
              offset). Pixels start at 1.
      fill  - Fill style.  Set to None for no fill.  TODO: other options?
      wcs   - The wcs (defined by pywcs) used to convert from world coords
              to pixels.  If none, try to use a previously defined one
              (i.e., when halftone or contours were plotted)."""

   z = header.updateZorder()
   
   a = header.translateArgs(**args)
   a['linestyle'] = header.lineStyleToText(a['linestyle'])

   if a['fillstyle'] == 'full':
      a['fillstyle'] = True
   else:
      a['fillstyle'] = False

   x2,y2 = header.translateCoords(x,y,a['coord'],a['wcs'])
   lw = 0.5*a['linewidth']
   if theta1 == 0 and theta2 == 360: # draw circle or Ellipse
      shape = header.Ellipse((x2,y2),xmajor,ymajor,angle,alpha=a['alpha'],
         edgecolor=a['edgecolor'],facecolor=a['facecolor'],fill=a['fillstyle'],
         ls=a['linestyle'],lw=lw,zorder=z)
   else: # draw an Arc
      shape = header.Arc((x2,y2),xmajor,ymajor,angle,theta1=theta1,theta2=theta2,
         color=a['color'],ls=a['linestyle'],lw=lw,zorder=z)
   fig = header.plt.gcf()
   fig.gca().add_artist(shape)
