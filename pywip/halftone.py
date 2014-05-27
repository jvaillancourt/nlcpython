from . import header

def halftone(image,head='rd',palette='gray',minmax=('immin','immax'),
   scale='linear',**args):
   '''Plot a halftone image with specified palette.

      Before using this, one should call winadj to make sure your pixels come
      out square.

      image   - string with name of image
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
      palette - color palette for halftone
      minmax  - list or tuple of (min,max) halftone limits to display.  The
                default is the minimum and maximum of the image.
      scale   - scale for image can be linear, log (logarithmic), or sqrt
                (square root).
      Allowed optional **args:
         limits - The standard limits keyword'''

   _allowed = ['limits']
   fp = header._wipopen('halftone',args.keys(),_allowed)
   pal = header._translatepalette(palette)
   if header._panelobj.get('image') != image:
      header._readimage(fp,image)
   fp.write('header %s\n' %head)
   if scale == 'linear':
      fp.write('ITF 0\n')
   elif scale == 'log':
      fp.write('ITF 1\n')
   elif scale == 'sqrt':
      fp.write('ITF 2\n')
   else:
      header._error("halftone(): scale must be one of linear, log, or sqrt!")
   if pal == 'lookup':
      if palette[0] == '-':
         header._lookup(datafile=palette[1:],reverse=True)
      else:
         header._lookup(datafile=palette)
   else:
      fp.write('palette %s\n' %pal)
   if args.has_key('limits'):
      header._panelobj.writelimits(fp,**args)
   fp.write('halftone ')
   if header._isseq(minmax) and len(minmax) == 2:  # convert to string of two values,
      junkminmax = ' '.join(map(str,minmax))# one or both of which can be
      fp.write('%s\n' %junkminmax)           # immin or immax
   else:
      header._error('halftone(): minmax must be given as a list/tuple of two values!')
   fp.write('set \\1 x1\n') # store map limits in registers 1-4
   fp.write('set \\2 x2\n') # useful for contour overlays
   fp.write('set \\3 y1\n')
   fp.write('set \\4 y2\n')
   if minmax:
      fp.write('set \\5 %s\n' %str(minmax[0]))
      fp.write('set \\6 %s\n' %str(minmax[1]))
   else:
      fp.write('set \\5 immin\n')
      fp.write('set \\6 immax\n')
   header._panelobj.set(image=image,limits=True,header=head,scale=scale,palette=palette)
   if palette != 'gray': # reset palette.  TODO: Is this here for lookup tables?
      fp.write("palette 0\n")
   fp.close()
