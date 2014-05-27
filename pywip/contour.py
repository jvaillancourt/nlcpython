from . import header

def contour(image,levels,head='rd',routine='smooth',unit='step',**args):
   r'''Draw contours with the specified levels.

      image   - string with name of image
      levels  - a list/tuple,string,or integer of contour levels.
         list/tuple - draw contours at specified levels
         number     - If unit='nbin', autogenerate the given number of
                      levels between the min and max.  unit='step' is not
                      supported (there is no way for wip/pywip to know the min
                      value).
         string     - If 'border', draw a box around the border of the
                      image.  Otherwise, must be three numbers formatted as
                      'val1:val2:val3'.  Depending on the keyword unit, the
                      values have different meanings:
                         unit='step'  - string is 'min:max:step'
                         unit='nbin'  - string is 'min:max:nbin'
                         unit='sigma' - string is 'start:step:sigma', e.g.
                            '3:1:0.1' would start at 3 sigma, in steps of
                            1 sigma, with 1 sigma being 0.1.
      head    - string of header for image.  x and y can be different, e.g.
         'rd px', but if only one value is given, it will be the same for y
         as well.  The allowed values are:
            rd - Right Ascension/Declination
            so - Arcsecond offset
            mo - Arcminute offset
            po - pixel offset
            px - Absolute pixels
            gl - General linear coordinates
            go - General linear coordinate offsets
      routine - how to draw contours: smooth, fast, neg.  neg will draw negative
                contours with the same line style as positive ones.  By default,
                negative contours are drawn dashed.
      unit    - units for levels keyword.  See description of levels.
      Allowed optional **args:
         limits  - The standard limits keyword
         color   - color for contour lines
         font    - font for contour labelling (TODO: not supported)
         style   - line style for contours
         width   - thickness of contour lines'''

   _allowed = ['limits','color','font','style','width']
   fp = header._wipopen('contour',args.keys(),_allowed)
   if levels == 'border':
      borderFlag = True
   else:
      borderFlag = False

   if header._panelobj.get('image') != image:
      header._readimage(fp,image)
   header._panelobj.set(**args)
   fp.write('header %s\n' %head)
   if borderFlag:
      fp.write('set \\13 x1\n')
      fp.write('set \\14 x2\n')
      fp.write('set \\15 y1\n')
      fp.write('set \\16 y2\n')
   else:
      blah = header._translatelevels(levels,unit)
      if isinstance(blah,str):
         fp.write('levels %s\n' %blah)
         if unit == 'sigma':
            tmp = levels.split(':')
            fp.write('slevel a %s\n' %tmp[2])
         else:
            fp.write('slevel a 1\n')
      else: # use autolevs
         if unit == 'nbin':
            fp.write('autolevs %d\n' %blah)
         elif unit == 'step':
            header._error('contour(): unit=step not allowed when level=a number!')
         #if _isseq(minmax) and len(minmax) == 2:
         #   fp.write('autolevs %d lin %g %g\n' %(blah,minmax[0],minmax[1]))
         #else:
         #   fp.write('autolevs %d\n' %blah)
   if header._panelobj.get('limits'):
      fp.write('limits \\1 \\2 \\3 \\4 \n')
   else:
      fp.write('set \\1 x1\n') # store map limits in registers 1-4
      fp.write('set \\2 x2\n') # useful for contour overlays
      fp.write('set \\3 y1\n')
      fp.write('set \\4 y2\n')
      header._panelobj.set(limits=True)
   header._optionsobj.update(fp,**args)
   if borderFlag:
      fp.write('move \\13 \\15\n')
      fp.write('draw \\14 \\15\n')
      fp.write('draw \\14 \\16\n')
      fp.write('draw \\13 \\16\n')
      fp.write('draw \\13 \\15\n')
   else:
      if args.has_key('style') and args['style'] == '--':
         routine = 'fast' # must set to fast to get dashed contours to show up
      elif header._optionsobj.lstyle == '--':
         routine = 'fast'
      if routine == 'smooth':
         fp.write('contour t\n')
      elif routine == 'fast':
         fp.write('contour s\n')
      elif routine == 'neg': # draw negative contours with same lstyle as + ones
         fp.write('contour -t\n')
      else:
         header._error('contour(): Invalid routine keyword.  Try fast, smooth, or neg!')
   header._optionsobj.reset(fp,**args)
   header._panelobj.set(image=image,header=head)
   fp.close()
