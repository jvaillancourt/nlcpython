from . import header

def ylabel(text,offset=0,align='center',side='left',**args):
   '''Set the y label to the given text.

      text   - a string of text to print out as y axis label
      offset - offset for text in addition to standard offset for a y label
      align  - alignment for label.  Either left, center, or right, or a
               number between zero and one. (zero=left, one=right).
      side   - can be left or right to put a label on left/right sides
      angle     - angle in degrees for text
      Allowed options **args:
         color  - a string giving the color for the label
         font   - a string giving the font to use for the label
         size   - a number giving the size for label.
         style  - a string giving the line style for the label
         width  - a number giving the width of the lines
         bg     - background color for text'''

   _allowed = ['color','font','size','style','width','bg']
   fp = header._wipopen('ylabel',args.keys(),_allowed)
   header._mtext(fp,text,offset,align,side,**args)
   fp.close()
