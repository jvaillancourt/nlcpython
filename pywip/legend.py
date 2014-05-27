from . import header

def legend(x,y,height=2,length=2,**args):
   '''Make an entire legend box.

      x      - x location of upper left corner as a fraction
               (e.g. 0.5 would be centered)
      y      - y location of upper left corner as a fraction
      height - vertical skip (in char. units) between entries
      length - horizontal space (in char. units) for line/symbol

      Allowed options **args:
         color - a string giving the color for the text
         font  - a string giving the font to use for the text
         size  - a number giving the size for text
         style - a string giving the line style for the text
         width - a number giving the thickness of the line
         bg    - color for background of text.  Default is transparent'''

   _allowed = ['color','font','size','style','width','bg']
   fp = header._wipopen('legend',args.keys(),_allowed)
   fp.write('new tmpxlin tmpxsym tmpxlen tmpylin tmpxtxt tmpytxt\n')
   fp.write('new dx dy length height charheight\n')
   # I sort of determined by trail and error that 0.012/(vy2 - vy1) would
   # be the character height.  But then I found I need a fudge factor for dy.
   # oh, well.  These seem to work no matter what, even if they are kludgey.
   fp.write('limits 0 1 0 1\n')
   if not args.has_key('size'):
      fp.write('set charheight %s * 0.012 / (vy2 - vy1)\n' %header._optionsobj.size)
   else:
      fp.write('set charheight %f * 0.012 / (vy2 - vy1)\n' %args['size'])
   # space between line and text
   fp.write('set dx 0.8 * charheight\n')
   # vertical offset of line/symbol from text
   fp.write('set dy 0.4 * charheight\n')
   # length of line
   fp.write('set length %f * charheight\n' %length)
   # vertical skip for each entry in legend
   fp.write('set height %f * charheight\n' %height)
   # starting x coordinate for symbol
   fp.write('set tmpxsym %g + (length / 2.0)\n' %x)
   # end x coordinate for line
   fp.write('set tmpxlen %g + length\n' %x)
   # starting y coordinate for text
   fp.write('set tmpytxt %g - height\n' %y)
   # y coordinate for line
   fp.write('set tmpylin tmpytxt + dy\n')
   # starting x coordinate for text
   fp.write('set tmpxtxt %g + length + dx\n' %x)
   #fp.write('echo vx1 vx2 vy1 vy2 tmpxlin tmpytxt\n')
   for c in header._panelobj.curves: # put each curve in the legend
      sym = c['style']
      # First do the symbol or line for the entry
      if sym in header._lstyles: # draw a line
         fp.write('move %g tmpylin\n' %x) # starting x/y coordinates
         header._optionsobj.update(fp,**c)
         fp.write('draw tmpxlen tmpylin\n')
         header._optionsobj.reset(fp,**c)
      else: # put individual symbol
         fp.write('move tmpxsym tmpylin\n')
         header._optionsobj.update(fp,**c)
         fp.write('symbol %s\n' %header._translatesymbol(c['style']))
         fp.write('dot\n')
         header._optionsobj.reset(fp,**c)
         if c['fillcolor'] != '-1':
            header._optionsobj.update(fp,color=c['fillcolor'],size=c['fillsize'],width=c['width'])
            fp.write('symbol %s\n' %header._translatesymbol(c['fillstyle']))
            fp.write('dot\n')
            header._optionsobj.reset(fp,color=c['fillcolor'],size=c['fillsize'],width=c['width'])
      # Now do the text label for the entry
      header._optionsobj.update(fp,**args)
      fp.write('move tmpxtxt tmpytxt\n')
      fp.write('putlabel 0.0 %s\n' %c['text'])
      header._optionsobj.reset(fp,**args)
      fp.write('set tmpylin tmpylin - height\n')
      fp.write('set tmpytxt tmpytxt - height\n')
   fp.write('free tmpxlin tmpxsym tmpxlen tmpylin tmpxtxt tmpytxt\n')
   fp.write('free dx dy length height charheight\n')
   fp.close()
   header._panelobj.curves = [] # reset curves to nothing after a legend is made
