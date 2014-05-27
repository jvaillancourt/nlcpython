from . import header

def arrow(xcol,ycol,taper=45,vent=0.0,fill='s',**args):
   '''Draw a single arrow.

      If you want many arrows, consider using the vector() command.  The
      coordinates given by xcol and ycol can be WCS coordinates, following the
      usual style for specifying them, i.e. as a sexagesimal string or a string
      for the coordinate in degrees.

      xcol   - a list/tuple of the begin and end x coordinates of the arrow
      ycol   - a list/tuple of the begin and end y coordinates of the arrow
      taper  - tapering angle, in degrees, for the arrowhead
      vent   - fraction of the arrowhead that is cut-away in the back.
      fill   - fill style for the arrowhead
      Allowed optional **args:
         color     - the color of the arrow and arrowhead as a string
         size      - the size of the arrowhead
         style     - line style for drawing the arrow
         width     - thickness of the line
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.
         text      - A string that can be used for the legend command.  Defaults
                     to None (don't add to legend).'''

   if args.has_key('text'):
      if args['text'] is not None:
         args['style'] = 'arrow'
         header._makecurve(**args)

   if not header._isseq(xcol) or len(xcol) != 2:
      header._error('arrow(): xcol must be a list/tuple of 2 elements!')
   if not header._isseq(ycol) or len(ycol) != 2:
      header._error('arrow(): ycol must be a list/tuple of 2 elements!')

   _allowed = ['color','size','style','width','limits','logx','logy','text']
   fp = header._wipopen('arrow',args.keys(),_allowed)
   header._panelobj.writelimits(fp,**args)
   header._optionsobj.update(fp,**args)
   tmpx = [header._translatecoords(xcol[0],coord='ra') ,
           header._translatecoords(xcol[1],coord='ra')]
   tmpy = [header._translatecoords(ycol[0],coord='dec'),
           header._translatecoords(ycol[1],coord='dec')]
   if header._panelobj.get('logx'):
      tmpx = [math.log10(tmpx[0]),math.log10(tmpx[1])]
   if header._panelobj.get('logy'):
      tmpy = [math.log10(tmpy[0]),math.log10(tmpy[1])]
   fp.write('fill %s\n' %header._translatefill(fill))
   fp.write('move %f %f\n'  %(tmpx[0],tmpy[0]))
   fp.write('arrow %f %f %f %f\n' %(tmpx[1],tmpy[1],taper,vent))
   header._optionsobj.reset(fp,**args)
   fp.close()
