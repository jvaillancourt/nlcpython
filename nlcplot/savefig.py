from . import header
import os

def savefig(filename,crop=True,dpi=None,orient='portrait',transparent=False):
   """Save figure
   
      filename    - string with output filename
      dpi         - dots per inch for non-ps/pdf files.  If None, a default
                    is used.
      crop        - boolean to create a bounding box around eps and pdf files
      orient      - string with orientation.  Options are 'landscape' or
                    'portrait'
      transparent - boolean to use a transparent background.  Only supported
                    for pdf and png."""

   print "Saving figure %s..." %filename
   name,ext = os.path.splitext(filename)
   if transparent is True:
      if ext not in ('.pdf','.png'):
         print("Warning! Transparent background only supported for pdf and png!")
         transparent = False
   if crop is True:
      header.plt.savefig(filename,bbox_inches='tight',orientation=orient,
         transparent=transparent,dpi=dpi)
   else:
      header.plt.savefig(filename,orientation=orient,transparent=transparent,
         dpi=dpi)
   header.plt.clf()
