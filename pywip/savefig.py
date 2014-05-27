from . import header
import os

def savefig(filename,orient='portrait',color=True,debug=False):
   '''Make the output plot by actually running wip.

      filename - a string or list/tuple giving the output filename(s) with
                 .gif or .ps extension (files) or .xs for an xwindow (e.g. 1.xs).
      orient   - make plot portrait or landscape orientation?
      color    - set to False to make a black and white plot
      debug    - set to True if you do not want to delete all the temp files needed by wip'''

   if orient not in ('landscape','portrait'):
      header._error('savefig(): invalid orient option in savefig.  Try landscape or portrait')

   if header._isseq(filename):
      fileseq = filename
   else:
      fileseq = [filename]
   for f in fileseq:
      if f.endswith('.gif'):
         dev = '%s/gif' %f
      elif f.endswith('.ps'):
         dev = '%s/' %f
         if orient == 'portrait':
            dev = dev + 'v'
         if color:
            dev = dev + 'c'
         dev = dev + 'ps'
      elif f.endswith('.xs'):
         dev = '%s/xs' %f[:-3]
      else:
         header._error('savefig(): Invalid output plot filename suffix.  Try .ps or .gif')
      if header._wipfile != '???':
         os.system('wip -x -d %s %s' %(dev,header._wipfile))
   if not debug:
      os.remove(header._wipfile)
      for f in header._tmplist:
         os.remove(f)
   header._wipfile = '???'
   header._tmplist = []
