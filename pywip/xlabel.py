from . import header

def xlabel(text,offset=0,align='center',**args):
   '''Set the x label to the given text.

      text   - a string of text to print out as x axis label
      offset - offset for text in addition to standard offset for an x label
      align  - alignment for label.  Either left, center, or right, or a
               number between zero and one. (zero=left, one=right).
      Allowed optional **args:
         color  - a string giving the color for the label
         font   - a string giving the font to use for the label
         size   - a number giving the size for label.
         style  - a string giving the line style for the label
         width  - a number giving the width of the lines
         bg     - background color for text'''

   _allowed = ['color','font','size','style','width','bg']
   fp = header._wipopen('xlabel',args.keys(),_allowed)
   header._mtext(fp,text,offset,align,side='bottom',**args)
   fp.close()
