from . import header
from . import getlimits
from . import tickmarks
from matplotlib.ticker import FixedLocator # needed to fix minor tick locations
from matplotlib import rcParams
import math

def axis(box="top,bottom,left,right",coord='pix',limits=None,
   number="bottom,left",xgrid="",ygrid="",xlog=False,ylog=False,
   xtick="major,minor,inside",ytick="major,minor,inside",limitscoord='pix',
   **args):
   """Plot the axis.
      box    - controls drawing the frame.  Defaults to drawing all 4 sides
      coord  - defines the label coords for x and y.  Pixels start at 1.
               Set to one of: pix, deg, hms, do (degrees offset), mo
               (arcminutes offset), so (arcseconds offset).
      limits - if specified, a list/tuple of 4 numbers and coordinate type 
               given as xmin,xmax,ymin,ymax,coord.  This is the format
               returned by getlimits().  If the coord is missing, it is assumed
               to be 'pix'.
      number - where to place numbers.  Options are top,bottom,left,right
      xgrid  - Controls drawing a grid for x axis.  Defaults to no grid.  Can
               have options of major,minor
      ygrid  - Controls drawing a grid for y axis.  Defaults to no grid.  Can
               have options of major,minor
      xlog   - If set to True, xaxis is labeled logarithmically
      ylog   - If set to True, yaxis is labeled logarithmically
      xtick  - Controls drawing xtickmarks (inside,outside,inout)
      ytick  - Controls drawing ytickmarks
   """

   wcs = header.updateWcs(None)
   a = header.translateArgs(**args)
   header.plt.axis('on') # turn axis plotting on
   ax = header.plt.gca()

   # draw parts of frame
   if 'top' in box and 'bottom' in box and 'left' in box and 'right' in box:
      pass # default is to draw all four sides
   elif box == "":
      ax.set_visible(False)
   else:
      ax.set_visible(False)
      tmp = box.split(',')
      for side in tmp:
         ax.spines[side].set_visible(True)
      # control displaying tickmarks, which are tied to whether frame is shown
      if 'left' in tmp and 'right' in tmp: # default puts ticks on both sides
         pass
      elif 'left' in tmp:
         ax.yaxis.tick_left()
      elif 'right' in tmp:
         ax.yaxis.tick_right()
      else: # no left or right ticks
         header.plt.yticks([],[])
      if 'top' in tmp and 'bottom' in tmp: # default puts ticks on both sides
         pass
      elif 'top' in tmp:
         ax.xaxis.tick_top()
      elif 'bottom' in tmp:
         ax.xaxis.tick_bottom()
      else: # no top or bottom ticks
         header.plt.xticks([],[])

   # set limits, if specified
   if limits is not None:
      if len(limits) == 4: # default to pix if not present
         limitscoord = 'pix'
      else:
         limitscoord = limits[4]
      if wcs is not None:  # this means a FITS image is plotted
         if limitscoord in ('do','mo','so'): # convert offsets to degrees
            crval = wcs.wcs.crval # get center coordinates
            rafac = 1.*math.cos(math.pi*crval[1]/180.)
            decfac = 1.
            if limitscoord == 'do':
               pass
            elif limitscoord == 'mo':
               rafac = 60*rafac
               decfac = 60*decfac
            elif limitscoord == 'so':
               rafac = 60*rafac
               decfac = 60*decfac
            limits[0] = limits[0]/rafac + crval[0]
            limits[1] = limits[1]/rafac + crval[0]
            limits[2] = limits[2]/decfac + crval[1]
            limits[3] = limits[3]/decfac + crval[1]
         
         if limitscoord == 'pix':
            limits[0] = limits[0] - 0.5 # subtract 0.5 to include left edge
            limits[1] = limits[1] + 0.5 # add 0.5 to include right edge
            limits[2] = limits[2] - 0.5 # subtract 0.5 to include bottom edge
            limits[3] = limits[3] + 0.5 # add 0.5 to include top edge
         elif limitscoord == 'hms':
            limits[0] = header._sex2deg(limits[0],'ra')
            limits[1] = header._sex2deg(limits[1],'ra')
            limits[2] = header._sex2deg(limits[2],'dec')
            limits[3] = header._sex2deg(limits[3],'dec')
            x,y = wcs.wcs_sky2pix([limits[0],limits[1],limits[0],limits[1]],
               [limits[2],limits[2],limits[3],limits[3]],1)
            limits = [min(x),max(x),min(y),max(y)]
         else:
            # convert degrees to pixels
            x,y = wcs.wcs_sky2pix([limits[0],limits[1],limits[0],limits[1]],
               [limits[2],limits[2],limits[3],limits[3]],1)
            limits = [min(x),max(x),min(y),max(y)]
            
         lims = [a - 1 for a in limits[:4]]
      else:
         l = list(header.plt.axis()) # this gets limits in pixel coordinates
         lims = limits[:4] # eliminate last item, which is limitscoord
         if lims[0] > l[1] or lims[2] > l[3]: # xmin > maximum x value plotted
            header.error("Limits outside image!")# or ymix > maximum y value
      header.plt.axis(lims)

   # control drawing numbers
   lbottom = ltop = lleft = lright = False
   if 'bottom' in number:
      lbottom = True
   if 'top' in number:
      ltop = True
   if 'left' in number:
      lleft = True
   if 'right' in number:
      lright = True
   header.plt.tick_params('x',labelbottom=lbottom,labeltop=ltop)
   header.plt.tick_params('y',labelleft=lleft,labelright=lright)

   # control drawing major/minor tickmarks
   if 'major' not in xtick:
      header.plt.xticks([],[])
   if 'minor' in xtick:
      header.plt.minorticks_on() #TODO: set minor ticks for x,y separately
   if 'major' not in ytick:
      header.plt.yticks([],[])
   if 'minor' in ytick:
      header.plt.minorticks_on()
   if 'outside' in xtick: # draw xticks outside box
      header.plt.tick_params(axis=='x',direction='out')
   if 'inout' in xtick: # draw xticks inside and outside
      header.plt.tick_params(axis=='x',direction='inout')
   if 'outside' in ytick: # draw yticks outside box
      header.plt.tick_params(axis=='y',direction='out')
   if 'inout' in ytick: # draw yticks inside and outside
      header.plt.tick_params(axis=='y',direction='inout')

   # now do grid
   if xgrid != "": #TODO: Doesn't seem to work (matplotlib error)
      if 'major' in xgrid and 'minor' in xgrid:
         which = 'both'
      elif 'major' in xgrid:
         which = 'major'
      elif 'minor' in xgrid:
         which = 'minor'
      elif 'both' in xgrid:
         which = 'both'
      else:
         which = None
      if which is not None:
         header.plt.grid(which,axis='x')
   if ygrid != "": #TODO: Doesn't seem to work (matplotlib error)
      if 'major' in ygrid and 'minor' in ygrid:
         which = 'both'
      elif 'major' in ygrid:
         which = 'major'
      elif 'minor' in ygrid:
         which = 'minor'
      elif 'both' in ygrid:
         which = 'both'
      else:
         which = None
      if which is not None:
         header.plt.grid(which,axis='y')
   
   if coord != 'pix':
      ext = 0
      # TODO: Why must I put getlimits.getlimits() when rect() doesn't
      # have to have polygon.polygon()?
      if limits is None:
         limits = getlimits.getlimits()
      xlocs,xlabels,xminor = tickmarks.getcoord(wcs,limits,'bottom',coord)
      ylocs,ylabels,yminor = tickmarks.getcoord(wcs,limits,'left',coord)
      #print xlocs,xlabels
      header.plt.xticks(xlocs,xlabels)
      header.plt.yticks(ylocs,ylabels)
      ax.xaxis.set_minor_locator(FixedLocator(xminor))
      ax.yaxis.set_minor_locator(FixedLocator(yminor))
