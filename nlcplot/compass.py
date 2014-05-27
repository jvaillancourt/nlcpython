from . import header

def compass(x,y,size=1,**args):
   """Plot a galactic compass

      x,y    - coordinates for placement of base of compass
      size   - length of compass (all but pix supported for coordinates)
      
      Supported optional arguments:
      color  - color of arrows and text

      coord - Input coordinates for x,y and size.  Set to one of: pix, deg, 
              hms, do (degrees offset), mo (arcminutes offset), so (arcseconds 
              offset).  Pixels start at 1.
      wcs    - The wcs (defined by pywcs) used to convert from world coords
               to pixels.  If none, try to use a previously defined one
               (i.e., when halftone or contours were plotted).
      width  - Thickness of lines and text"""

   a = header.translateArgs(**args)
   wcs = header.updateWcs(a['wcs'])
   ctype = header.translateCtype(wcs)
   z = header.updateZorder()

   x1,y1 = header.translateCoords(x,y,a['coord'],a['wcs'])
   if ctype == 'ra':
      ra,dec = wcs.wcs_pix2sky(x1,y1,0)
      gl,gb  = header.eq2gal(ra[0],dec[0],wcs) # convert to galactic
   elif ctype == 'glon':
      gl,gb  = wcs.wcs_pix2sky(x1,y1)

   if a['coord'] in ('deg','hms','do'):
      size = header._sex2deg(size,ctype)
   elif a['coord'] == 'mo':
      size = float(size)/60.
   elif a['coord'] == 'so':
      size = float(size)/3600.
   else:
      header.error('compass(): size cannot be given as pixels!')
   gl2,gb2  = (gl+size,gb+size) # find directions of increasing galactic

   if ctype == 'ra':
      ra2,dec2 = header.gal2eq(gl2,gb,wcs) # convert new galactic to new ra/dec
      ra3,dec3 = header.gal2eq(gl,gb2,wcs) # convert new galactic to new ra/dec
      x2,y2    = wcs.wcs_sky2pix([ra2,ra3],[dec2,dec3],0) # convert radec back to pix
      ra2,dec2 = header.gal2eq(gl+1.3*size,gb,wcs) # convert new galactic to new ra/dec
      ra3,dec3 = header.gal2eq(gl,gb+1.3*size,wcs) # convert new galactic to new ra/dec
      x3,y3    = wcs.wcs_sky2pix([ra2,ra3],[dec2,dec3],0) # convert radec back to pix
   elif ctype == 'glon':
      x2,y2 = wcs.wcs_sky2pix([gl2,gl],[gb,gb2])
      x3,y3 = wcs.wcs_sky2pix([gl+1.3*size,gl],[gb,gb+1.3*size])
   else:
      header.error("compass(): Unknown ctype: %s" %ctype)

   header.plt.arrow(x1,y1,x2[0]-x1,y2[0]-y1,length_includes_head=True,
      head_width=10,color=a['color'],linewidth=a['linewidth'],zorder=z)
   header.plt.arrow(x1,y1,x2[1]-x1,y2[1]-y1,length_includes_head=True,
      head_width=10,color=a['color'],linewidth=a['linewidth'],zorder=z)

   header.plt.text(x3[0],y3[0],r'$\ell$',color=a['color'],va='center',
      ha='center',fontweight=a['fontweight'],zorder=z)
   header.plt.text(x3[1],y3[1],r'$\it{b}$',color=a['color'],va='center',
      ha='center',fontweight=a['fontweight'],zorder=z)
   
   #TODO: finish compass() command to actually plot something.
