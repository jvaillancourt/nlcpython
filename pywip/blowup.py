from . import header

def blowup(xmin,xmax,ymin,ymax,corners=['ll','ul'],**args):
   r'''Draw a blow-up box around a given region.

      Use in conjunction with connect() to draw connecting lines from the
      blowup box to the actual zoomed region.

      xmin,xmax,ymin,ymax - four values for limits of blowup box given as
                            pixel values
      corners - a two element list of ll,ul,lr, or ur to specify which corners
                of the box to store in memory.  These correspond to lower left,
                upper left,lower right, upper right
      Allowed optional **args:
         color - a string giving the color for the box
         style - a string giving the linestyle for the box
         width - a number giving the thickness of the box'''

   _allowed = ['color','style','width']
   fp = header._wipopen('blowup',args.keys(),_allowed)
   header._optionsobj.update(fp,**args)
   fp.write('limits 1 \\7 1 \\8\n') # ensures that xmin,xmax,ymin,ymax are all
                                    # pixel coordinates.  Assumes the user has
                                    # set \7 and \8 through winadj
   fp.write('fill %s\n' %header._translatefill('h')) # always hollow
   fp.write('rect %f %f %f %f\n' %(xmin,xmax,ymin,ymax))
   if   corners[0] == 'll':  header._xytovp(fp,str(xmin),str(ymin),r'\9',r'\10')
   elif corners[0] == 'ul':  header._xytovp(fp,str(xmin),str(ymax),r'\9',r'\10')
   elif corners[0] == 'lr':  header._xytovp(fp,str(xmax),str(ymin),r'\9',r'\10')
   elif corners[0] == 'ur':  header._xytovp(fp,str(xmax),str(ymax),r'\9',r'\10')

   if   corners[1] == 'll':  header._xytovp(fp,str(xmin),str(ymin),r'\11',r'\12')
   elif corners[1] == 'ul':  header._xytovp(fp,str(xmin),str(ymax),r'\11',r'\12')
   elif corners[1] == 'lr':  header._xytovp(fp,str(xmax),str(ymin),r'\11',r'\12')
   elif corners[1] == 'ur':  header._xytovp(fp,str(xmax),str(ymax),r'\11',r'\12')
   header._optionsobj.reset(fp,**args)
   fp.close()
