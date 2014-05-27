from . import header

def plot(xcol,ycol,filename=None,xerr=None,yerr=None,label='_nolegend_',
   **args):
   """Plot data as points or lines

      Supported optional arguments:
      fcolor - Color of inside of symbol (facecolor)
      ecolor - Color of border of symbol (edgecolor)
      color  - Color of both inside and border of symbol
      coord  - set to either 'pix' or 'wcs', which defines the input coords
               for x and y.  Pixels are one-based.
      style
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
      width"""

   a = header.translateArgs(**args)
   z = header.updateZorder()

   if not args.has_key('style'): # default style is a circle, without connecting
      if not args.has_key('lstyle'): # line.
         a['linestyle'] = 'None'
   if filename is not None:
      _cols = [xcol-1,ycol-1]
      if xerr is not None:
         _cols.append(xerr-1)
      if yerr is not None:
         _cols.append(yerr-1)
      _data = header.loadtxt(filename,usecols=_cols)
      xcol = _data[:,0]
      ycol = _data[:,1]
      if xerr is not None:
         xerr = _data[:,2]
      if yerr is not None:
         if xerr is None:
            yerr = _data[:,2]
         else:
            yerr = _data[:,3]
   if len(xcol) == 0 or len(ycol) == 0:
      header.error("Empty data set!")

   x2,y2 = header.translateCoords(xcol,ycol,a['coord'],a['wcs'])

   if a['lineflag']:
      header.plt.errorbar(x2,y2,xerr=xerr,yerr=yerr,alpha=a['alpha'],
         color=a['color'],ecolor=a['color'], lw=a['linewidth'],
         ls=a['linestyle'],label=label,zorder=z)
   else:
      header.plt.errorbar(x2,y2,xerr=xerr,yerr=yerr,alpha=a['alpha'],
         fillstyle=a['fillstyle'],ls=a['linestyle'],marker=a['marker'],
         mfc=a['markerfacecolor'],mec=a['markeredgecolor'],
         ecolor=a['markeredgecolor'],mew=a['markeredgewidth'],
         ms=a['markersize'],label=label,zorder=z)
   header.plt.axis('off') # turn off axis plot
