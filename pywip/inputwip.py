from . import header
import os

def inputwip(filename,**args):
   """Input the given filename directly as raw WIP commands.
   
      This is a hack for my manually drawn tickmarks because WIP does not do
      proper WCS projections.  For now, I have another script to make the
      tickmarks file, which should be added to the plot as raw WIP commands.

      Allowed options **args:
         color - a string giving the color for the text
         font  - a string giving the font to use for the text
         size  - a number giving the size for text
         style - a string giving the line style for the text
         width - a number giving the thickness of the line
         bg    - color for background of text.  Default is transparent"""

   _allowed = ['color','font','size','style','width','bg']
   if os.path.exists(filename):
      fp = header._wipopen('inputwip',args.keys(),_allowed)
      header._optionsobj.update(fp,**args)
      fp2 = open(filename,'r')
      for line in fp2:
         fp.write(line)
      header._optionsobj.reset(fp,**args)
      fp.close()
      fp2.close()
   else:
      header._error('inputwip(): File %s does not exist!' %filename)
