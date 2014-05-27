from . import header

def text(x,y,text,align='left',angle=0,**args):
   '''Put a given text label at specified coordinates.

      x,y       - coordinates for location of text
      text      - a string of text to print out
      align     - alignment for label.  Either left, center, or right
      angle     - angle in degrees for text
      Allowed options **args:
         color     - a string giving the color for the label
         font      - a string giving the font to use for the label
         size      - a number giving the size for label
         style     - a string giving the line style for the label
         width     - a number giving the width of the lines
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.
         bg        - background color for text.  Default is -1 (transparent)'''

   _allowed = ['color','font','size','style','width','logx','logy','bg']
   fp = header._wipopen('text',args.keys(),_allowed)
   header._panelobj.set(**args)
   if header._panelobj.get('logx'):
      xtmp = math.log10(header._translatecoords(x,coord='ra'))
   else:
      xtmp = header._translatecoords(x,coord='ra')
   if header._panelobj.get('logy'):
      ytmp = math.log10(header._translatecoords(y,coord='dec'))
   else:
      ytmp = header._translatecoords(y,coord='dec')
   al = header._translatealign(align)
   header._optionsobj.update(fp,**args)
   if angle != 0:
      fp.write('angle %s\n' %angle)
   fp.write('move %f %f\n' %(xtmp,ytmp))
   fp.write('putlabel %s %s\n' %(al,header._translatelatex(text)))
   header._optionsobj.reset(fp,**args)
   if angle != 0:
      fp.write('angle 0\n')
   fp.close()
