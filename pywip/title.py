from . import header

def title(text,offset=0,align='center',**args):
   '''Set the title of the plot to the given text.

      text   - a string of text to print out as title of plot
      offset - offset for text in addition to standard offset for a title
      align  - alignment for label.  Either left, center, or right, or a
               number between zero and one. (zero=left, one=right).
      Allowed optional **args:
         color  - a string giving the color for the title
         font   - a string giving the font to use for the title
         size   - a number giving the size for the title
         style  - a string giving the line style for the title
         width  - a number giving the width of the lines
         bg     - background color for text'''

   _allowed = ['color','font','size','style','width','bg']
   fp = header._wipopen('title',args.keys(),_allowed)
   header._mtext(fp,text,offset,align,side='top',**args)
   fp.close()
