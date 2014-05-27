from . import header

def winadj(xfac=1,yfac=1,image=None):
   '''Adjust the window so the plot will have the given aspect ratio.

      Note, for convenience sake, if you want to adjust a window size for
      an image, you can just call winadj(imagename) instead of
      winadj(image=imagename).

      xfac   - Relative size of x dimension
      yfac   - Relative size of y dimension
      image  - If a string of an image name (and optionally a subimage defined
               ala IRAF's method : image[xmin:xmax,ymin:ymax], then adjust
               window according to image size, taking into account xfac
               and yfac.'''

   fp = header._wipopen('winadj',[],[])
   if isinstance(xfac,str): # xfac is a string, so assume it is an image
      img = xfac
      xfac = 1
   else:
      img = image
   if img:
      header._panelobj.set(image=img)
      blah = header._readimage(fp,img)
      if blah: # a subimage was defined by the user
         nx = xfac*(blah[1] - blah[0] + 1)
         ny = yfac*(blah[3] - blah[2] + 1)
         fp.write('set \\7 %d\n' %nx)
         fp.write('set \\8 %d\n' %ny)
      else: # no subimage so use whole image.  WIP knows about nx and ny
         fp.write('set \\7 %g * nx\n' %xfac)
         fp.write('set \\8 %g * ny\n' %yfac)
      fp.write('winadj 0 \\7 0 \\8\n')
   else:
      fp.write('winadj 0 %g 0 %g\n' %(xfac,yfac))
      fp.write('set \\7 %g\n' %xfac)
      fp.write('set \\8 %g\n' %yfac)
   fp.close()
