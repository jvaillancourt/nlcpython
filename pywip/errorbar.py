from . import header

def errorbar(xcol,ycol,datafile=None,xerr=None,yerr=None,**args):
   '''Draw x,y errorbars on some data.

      xcol,ycol - Integer or list/tuple of x/y data
      datafile  - If a string, read columns xcol and ycol from datafile
      xerr      - Integer or list/tuple of x errorbars.  If int, read specified
                  column from datafile
      yerr      - Integer or list/tuple of y errorbars.  If int, read specified
                  column from datafile
      Allowed optional **args:
         color     - A string specifying the color of the errorbars
         size      - A number specifying the size of the caps on the errorbars
         style     - A string specifying the line style
         width     - A number specifying the line thickness
         limits    - If a list/tuple, use as limits.  Otherwise try to use
                     any prexisting limits or set new ones
         logx,logy - If True, make logarithmic in x/y direction.  Otherwise
                     default to what has already been set for plot/panel.'''

   _allowed = ['color','size','style','width','limits','logx','logy']
   fp = header._wipopen('errorbar',args.keys(),_allowed)
   ecol = 3 # column number for errorbar
   header._panelobj.set(**args)
   header._optionsobj.update(fp,**args)

   if not datafile:
      if header._isseq(xcol) and header._isseq(ycol):
         datafile = header._maketempfile(xcol,ycol,xerr=xerr,yerr=yerr)
      else:
         header._error('errorbar(): You must specify an input data file for errorbar!')
   else:
      datafile = header._maketempfile(xcol,ycol,datafile,xerr,yerr)

   fp.write('data %s\n' %datafile)
   fp.write('xcol 1\n')
   fp.write('ycol 2\n')
   if header._panelobj.get('logx'): fp.write('log x\n')
   if header._panelobj.get('logy'): fp.write('log y\n')
   header._panelobj.writelimits(fp,**args)
   if xerr:
      fp.write('ecol %d\n' %ecol)
      if header._panelobj.get('logx'):
         fp.write('log err\n')
         fp.write('errorbar 1\n')
         ecol = ecol + 1
         fp.write('ecol %d\n' %ecol)
         fp.write('log err\n')
         fp.write('errorbar 3\n')
      else:
         fp.write('errorbar 5\n')
      ecol = ecol + 1
   if yerr:
      fp.write('ecol %d\n' %ecol)
      if header._panelobj.get('logy'):
         fp.write('log err\n')
         fp.write('errorbar 2\n')
         ecol = ecol + 1
         fp.write('ecol %d\n' %ecol)
         fp.write('log err\n')
         fp.write('errorbar 4\n')
      else:
         fp.write('errorbar 6\n')
   header._optionsobj.reset(fp,**args)
   fp.close()
