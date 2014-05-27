#!/usr/bin/env python

from readcmd import ReadCmd
import os
import tempfile

spec = """# Take a ds9 contour file and make it usable by WIP
          in    = ??? # DS9 contour file
          out   = ??? # Output WIP file
          dir   = ??? # Output directory with WIP contours
          units = wcs # Units of contour file, other option is linear"""

if __name__ == "__main__":
   arg = ReadCmd(spec)
   infile   = arg.getstr('in',exist=True)
   outfile  = arg.getstr('out',exist=False)
   units    = arg.getstr('units',option=['wcs','linear'])
   contdir  = arg.getstr('dir',exist=False)
      
   os.mkdir(contdir)

   fp0 = open(infile,'r')
   fp1 = open(outfile,'w')
   fp1.write("symbol -1\n")
   written = 0
   fp2 = tempfile.NamedTemporaryFile(mode='w',dir=contdir,delete=False)
   for line in fp0:
      if len(line) == 0: # blank line starts/ends a contour
         fp2.close()
         if written:
            fp1.write("data %s\n" %fp2.name)
            fp1.write("xcol 1\n")
            fp1.write("ycol 2\n")
            fp1.write("points\n")
            fp1.write("connect\n")
         fp2 = tempfile.NamedTemporaryFile(mode='w',dir=contdir,delete=False)
         written = 0
      else: # data on the line
         tmp = map(float,line.split())
         if units == 'wcs':
            fp2.write("%f  %f\n" %(240*tmp[0],3600*tmp[1]))
         elif units == 'linear':
            fp2.write("%f %f\n" %tuple(tmp))
         written = 1
   fp1.close()
   fp2.close()
