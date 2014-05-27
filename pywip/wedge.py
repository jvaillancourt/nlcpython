from . import header

def wedge(side='right',offset=1,thickness=1,minmax=None,**args):
   '''Draw a halftone wedge on the image.

      This is only useful for halftone images, though you could draw a wedge
      without first calling halftone(), if you felt perverse.  Note that in
      that case, you cannot set the palette.

      side      - string containing side to draw wedge on.  One of left, right,
                  top, or bottom
      offset    - offset of wedge from side
      thickness - thickness of wedge
      minmax    - a list/tuple of the min/max values for the wedge.  Defaults
                  to whatever min/max was for halftone
      Allowed optional **args:
         all the axis() options.  Too many to list here; see the User's Manual.
         color     - color for the box around the wedge
         font      - font for labelling the wedge
         size      - size of box labels around wedge
         style     - line style for box
         width     - thickness of box around wedge'''

   if side not in ('bottom','top','left','right'):
      header._error('wedge(): unknown side parameter: %s!' %side)

   _axis_allowed = ['box','number','tickstyle','format','xinterval','yinterval',
                    'drawtickx','drawticky','firstx','firsty','gridx','gridy',
                    'logx','logy','subtickx','subticky','majortickx',
                    'majorticky','verticaly','zerox','zeroy']
   _allowed = _axis_allowed + ['color','font','size','style','width']

   fp = header._wipopen('wedge',args.keys(),_allowed)
   header._optionsobj.update(fp,**args)
   if not args.has_key('box'):
      args['box'] = ('bottom','left','top','right')
   if args.has_key('drawtickx') and not args['drawtickx']: # exists and False
      args['majortickx'] = False
   else:
      if not args.has_key('majortickx'): args['majortickx'] = True
   if args.has_key('drawticky') and not args['drawticky']: # exists and False
      args['majorticky'] = False
   else:
      if not args.has_key('majorticky'): args['majorticky'] = True
   if not args.has_key('number'):
      args['number'] = [side]
   xlab,ylab = header._translateaxis(**args)
   if side in ('left','right'):
      label = ylab
   else:
      label = xlab
   pal = header._panelobj.get('palette')
   if pal == None: # default to gray
      pal = 'gray'
   fp.write('palette %s\n' %header._translatepalette(pal))
   fp.write('wedge %s %f %f ' %(side[0],offset,thickness))
   if minmax:
      fp.write('%g %g %s\n' %(minmax[0],minmax[1],label))
   else:
      fp.write('\\5 \\6 %s\n' %label)
   header._optionsobj.reset(fp,**args)
   if pal != 'gray': # reset palette.  TODO: Is this here for lookup tables?
      fp.write("palette 0\n")
   fp.close()
