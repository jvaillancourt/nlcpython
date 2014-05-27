from . import header

def connect(corners=['ll','ul'],**args):
   '''Draw lines connecting a blow-up region to the current viewport coordinates.

      corners - a two element list of ll,ul,lr, or ur to specify which corners
                of the box to store in memory.  These correspond to lower left,
                upper left,lower right, upper right
      Allowed optional **args:
         color - a string giving the color for the lines
         style - a string giving the linestyle for the lines
         width - a number giving the thickness of the lines'''

   _allowed = ['color','style','width']
   fp = header._wipopen('connect',args.keys(),_allowed)
   header._optionsobj.update(fp,**args)
   fp.write('new tmp1 tmp2 tmp3 tmp4 xp yp\n')
   if corners[0] == 'll':
      header._xytovp(fp,'x1','y1','tmp1','tmp2')
   elif corners[0] == 'ul':
      header._xytovp(fp,'x1','y2','tmp1','tmp2')
   elif corners[0] == 'lr':
      header._xytovp(fp,'x2','y1','tmp1','tmp2')
   elif corners[0] == 'ur':
      header._xytovp(fp,'x2','y2','tmp1','tmp2')
   if corners[1] == 'll':
      header._xytovp(fp,'x1','y1','tmp3','tmp4')
   elif corners[1] == 'ul':
      header._xytovp(fp,'x1','y2','tmp3','tmp4')
   elif corners[1] == 'lr':
      header._xytovp(fp,'x2','y1','tmp3','tmp4')
   elif corners[1] == 'ur':
      header._xytovp(fp,'x2','y2','tmp3','tmp4')
   fp.write('viewport 0 1 0 1\n')
   header._vptoxy(fp,r'\9',r'\10','xp','yp')
   fp.write('move xp yp\n')
   header._vptoxy(fp,'tmp1','tmp2','xp','yp')
   fp.write('draw xp yp\n')
   header._vptoxy(fp,r'\11',r'\12','xp','yp')
   fp.write('move xp yp\n')
   header._vptoxy(fp,'tmp3','tmp4','xp','yp')
   fp.write('draw xp yp\n')
   fp.write('free tmp1 tmp2 tmp3 tmp4 xp yp\n')
   header._optionsobj.update(fp,**args)
   fp.close()
