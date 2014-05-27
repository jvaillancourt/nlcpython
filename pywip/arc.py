from . import header

def arc(x,y,majorx,majory,deg=360,start=0,angle=0,fill='s',**args):
   '''Draw a curved line to make circles, ellipses, arcs, etc.

      x,y           - central coordinates for arc.  If a string, convert WCS
                      into units usable by WIP.  The WCS can be given as
                      hh:mm:ss, dd:mm:ss or as degrees.  Note that you don't
                      have to give all three parts, you can omit the ss.  x is
                      always assumed to be RA and y is always assumed to be DEC.
      majorx,majory - major axes for x and y.  Like x,y this can be given as
                      a string to specify the WCS.
      deg           - draw arc over this many degrees
      start         - start drawing at this degree angle measured counter-
                      clockwise from +x axis.
      angle         - Tilt angle in degrees measured counter-clockwise
                      from +x axis.
      fill          - a string specifying the fill style
      Allowed optional **args:
         color     - a string with the color of the line
         style     - a string specifying the line style
         width     - thickness of lines
         fillcolor - color to fill arc with.  Defaults to color.
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.'''

   _allowed = ['color','style','width','fillcolor','limits','logx','logy']
   fp = header._wipopen('arc',args.keys(),_allowed)
   if fill != 'h':
      if args.has_key('fillcolor'):
         pass
      elif args.has_key('color'):
         args['fillcolor'] = args['color']
      else:
         args['fillcolor'] = header._colors[int(header._optionsobj.color)]
   header._panelobj.set(**args)
   
   header._panelobj.writelimits(fp,**args)
   if fill != 'h': # not hollow:
      header._optionsobj.update(fp,color=args['fillcolor'])
      fillstyle = header._translatefill(fill)
      fp.write('fill %s\n' %fillstyle)
      fp.write('move %f %f\n' %(header._translatecoords(x,coord='ra'),
               header._translatecoords(y,coord='dec')))
      fp.write('angle %f\n' %angle)
      tmpx = header._translatecoords(majorx,coord='ra')
      tmpy = header._translatecoords(majory,coord='dec')
      fp.write('arc %f %f %f %f\n' %(tmpx,tmpy,deg,start))
      header._optionsobj.reset(fp,color=args['fillcolor'])
   header._optionsobj.update(fp,**args)
   fp.write('fill %s\n' %header._translatefill('h'))
   fp.write('move %f %f\n' %(header._translatecoords(x,coord='ra'),
            header._translatecoords(y,coord='dec')))
   fp.write('angle %f\n' %angle)
   tmpx = header._translatecoords(majorx,coord='ra')
   tmpy = header._translatecoords(majory,coord='dec')
   fp.write('arc %f %f %f %f\n' %(tmpx,tmpy,deg,start))
   header._optionsobj.reset(fp,**args)
   fp.write('angle 0\n')
   fp.close()
