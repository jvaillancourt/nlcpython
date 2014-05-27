from . import header

def beam(x,y,amajor,aminor,angle=0,scale='rd',**args):
   '''Draw an ellipse showing a beam.  Useful for radio data.

      x,y           - Central coordinates for beam.  If a string, convert WCS
                      into units usable by WIP.  The WCS can be given as
                      hh:mm:ss, dd:mm:ss or as degrees.
      amajor,aminor - major and minor axes for ellipse as arcseconds. Like x,y
                      this can be given as a string to specify the WCS.
      angle         - tilt angle for ellipse given as degrees from the +x axis
      scale         - set to None for no scaling of x axis
      Allowed optional **args:
         color     - color of edge of ellipse
         fillcolor - color of inside of ellipse.  Defaults to color
         style     - line style for edge of ellipse
         width     - line thickness
         bg        - color for background box surrounding beam.  Defaults to
                     transparent.'''

   _allowed = ['color','fillcolor','style','width','bg']
   fp = header._wipopen('beam',args.keys(),_allowed)
   if scale == 'rd':
      scl = '-1'
   else:
      scl = '1'
   if args.has_key('bg'):
      bgrect = header._translatecolor(args['bg'])
      if bgrect == 'rgb':
         tmp = bgrect.replace(',',' ')
         fp.write("rgb 1 %s\n" %tmp)
         bgrect = '1'
   else:
      bgrect = header._optionsobj.bg
   if args.has_key('fillcolor'):
      fillcl = header._translatecolor(args['fillcolor'])
   elif args.has_key('color'):
      fillcl = header._translatecolor(args['color'])
      if fillcl == 'rgb':
         tmp = fillcl.replace(',',' ')
         fp.write("rgb 1 %s\n" %tmp)
         fillcl = '1'
   else:
      fillcl = header._optionsobj.color
   header._optionsobj.update(fp,**args)
   fp.write('move %f %f\n' %(header._translatecoords(x,coord='ra'),
      header._translatecoords(y,coord='dec')))
   tmpx = header._translatecoords(amajor,coord='ra')
   tmpy = header._translatecoords(aminor,coord='dec')
   fp.write('beam %f %f %f 0 0 %s %s %s\n' %(tmpx,tmpy,angle,scl,fillcl,bgrect))
   header._optionsobj.reset(fp,**args)
   fp.close()
