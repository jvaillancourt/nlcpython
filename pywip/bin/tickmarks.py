#!/usr/bin/env python
"""Script to generate proper WCS tickmarks in WIP.  WIP assumes the sky is
flat, and so can be off for large fields.  This uses the worldpos module."""

from readcmd import ReadCmd

spec = """# Compute proper WCS tickmarks
          in     = ???  # FITS image to read
          out    = ???  # Output file
          xrange = None # Optional xmin,xmax range in pixels
          yrange = None # Optional ymin,ymax range in pixels
          length = 1.5  # Major tickmark length as a % of pixels along each axis
          dec    = None # steps in DEC for minor,major ticks in arcmin
          ra     = None # steps in RA for minor,major ticks in hour-min"""

def error(text):
   """Write out error message and quit"""
   sys.stderr.write("### Fatal Error! %s\n" %text)
   sys.exit()

def deg2sex(value,coord):
   '''Convert degrees to sexagesimal, unless it is already in sexagesimal'''
   
   try:
      tmp = map(float,str(value).split(':'))
   except ValueError:
      error('Invalid string given for conversion to sexagesimal: %s' %value)

   n = len(tmp)
   if n == 1: # assume it was in degrees
      junk = tmp[0]
      if coord == 'ra':
         junk = junk/15.0
      hours = int(junk)
      junk = 60*(abs(junk) - abs(hours))
      minutes = int(junk)
      if abs(minutes - 60) < 1e-7:
         minutes = 0
         hours += 1
      junk = 60*(junk - minutes)
      seconds = float(junk)
      if abs(seconds - 60) < 1e-7:
         seconds = 0
         minutes += 1
      if abs(minutes - 60) < 1e-7:
         minutes = 0
         hours += 1
      tmp[0] = hours
      tmp.append(minutes)
      tmp.append(seconds)
   elif n == 2: # assume it was already sexagesimal, but no seconds given
      tmp.append(0.0)
   return tmp

def getstepdec(mindec,maxdec):
   """Get stepdec and declabel given the range in declination plotted"""
   # label steps in arcseconds
   tmplabel = [1  ,5,10,15,20,30,60,300,600,900,1200,1800,3600,18000,36000]
   tmpstep  = [0.5,1, 5, 5, 5,10,20, 60,300,300, 300, 600,1200, 3600,18000]

   declabel = map(lambda a: a/3600.,tmplabel) # convert to degrees
   stepdec  = map(lambda a: a/3600.,tmpstep)  # convert to degrees
       
   tmp = abs(maxdec - mindec)
   guess = tmp/6. # aim for about 6 labels
   diff  = [abs(guess-a) for a in declabel]
   idx   = diff.index(min(diff))
   
   return stepdec[idx],declabel[idx]

def getstepra(minra,maxra):
   """Get stepra and ralabel for the range of RA plotted"""
   
   # label steps in hour-seconds
   tmplabel = [1  ,  2,5,10,15,20,30,60,120,300,600,900,1200,1800,3600,18000]
   tmpstep  = [0.5,0.5,1, 2, 5, 5, 5,20, 30, 60,300,300, 300, 600,1200, 3600]
   
   ralabel = map(lambda a: a/3600.,tmplabel) # convert to hours
   stepra  = map(lambda a: a/3600.,tmpstep)  # convert to hours

   tmp = abs(maxra - minra)
   guess = tmp/6. # aim for about 6 labels
   diff  = [abs(guess-a) for a in ralabel]
   idx   = diff.index(min(diff))
   
   return stepra[idx],ralabel[idx]
 
if __name__ == "__main__":
   arg = ReadCmd(spec)
   image      = arg.getstr('in',exist=True)
   rangex     = arg.getlistfloat('xrange',length=2)
   rangey     = arg.getlistfloat('yrange',length=2)
   tmplength  = arg.getfloat('length')
   tmpra      = arg.getlistfloat('ra',length=2)
   tmpdec     = arg.getlistfloat('dec',length=2)
   outfile    = arg.getstr('out',exist=False)

   import worldpos
   wcs = worldpos.wcs(image)
   if wcs.header['rot'] != 0:
      error('WIP cannot handle rotations!')
      
   if len(rangex) == 0:
      xmin = 0.5
      xmax = naxis1 + 0.5
   else:
      xmin = rangex[0] - 0.5
      xmax = rangex[1] + 0.5
   if len(rangey) == 0:
      ymin = 0.5
      ymax = naxis2 + 0.5
   else:
      ymin = rangey[0] - 0.5
      ymax = rangey[1] + 0.5

   xlength = tmplength*(xmax-xmin)/100.
   ylength = tmplength*(ymax-ymin)/100.

   fp = open(outfile,'w')
   
   fp.write("### Start of tickmarks()\n")
   stack = ['\n# Axis Labels\n'] # hold all drawing information for numbers
   stack.append('new xoffset yoffset\n')
   stack.append('set xoffset %g\n' %(xmin-xlength))
   stack.append('set yoffset %g\n\n' %(ymin-2*ylength))

   # bottom edge
   # ra,dec for the two corners
   ra1,dec1 = wcs.xy2sky([xmin,xmax],[ymin,ymin])
   # ra,dec inset by a tickmark length (major ticks)
   ra2,dec2 = wcs.xy2sky([xmin,xmax],[ymin+ylength,ymin+ylength])
   # ra,dec inset by half a tickmark length (minor ticks)
   ra3,dec3 = wcs.xy2sky([xmin,xmax],[ymin+ylength/2.,ymin+ylength/2.])
   
   # convert ra's to hours
   ra1 = map(lambda a: a/15., ra1)
   ra2 = map(lambda a: a/15., ra2)
   ra3 = map(lambda a: a/15., ra3)
   
   if len(tmpra) == 2:
      stepra  = tmpra[0]/60.
      ralabel = tmpra[1]/60.
   else:
      stepra,ralabel = getstepra(ra1[0],ra1[1])

   m1 = (ra1[1] - ra1[0])/(xmax-xmin)
   b1 = ra1[0] - m1*xmin
   m2 = (ra2[1] - ra2[0])/(xmax-xmin)
   b2 = ra2[0] - m2*xmin
   m3 = (ra3[1] - ra3[0])/(xmax-xmin)
   b3 = ra3[0] - m3*xmin
   tmpra = int(ra1[0]) # integer number of hours
   while tmpra < ra1[0]:
      tmpra += stepra
   if tmpra > ra1[0]:
      tmpra = tmpra - stepra

   stack.append('# RA Labels\n')
   fp.write('#Bottom Edge\n')
   while tmpra >= ra1[1]: # step by hours, not degrees
      x1 = (tmpra - b1)/m1
      y1 = ymin
      junk = tmpra/ralabel
      if abs(junk - round(junk)) < 1e-7: # major tickmark
         x2 = (tmpra - b2)/m2
         y2 = ymin + ylength
         stack.append("move %g yoffset\n" %x1)
         hms = deg2sex(15*tmpra,'ra')
         amin = '%02d' % hms[1]
         if stepra < 1/3600.: # increment smaller than 1 hour-second
            asec = '%04.1f' %hms[2]
         else:
            asec = '%02d' %hms[2]

         junk1 = tmpra/1. # test for full hours
         junk2 = tmpra/0.016666666 # test for full hour-minutes
         if ralabel >= 1:
            mystr = "putlabel 0.5 %d\uh\d\n" %hms[0] # full hours
         elif ralabel >= 1/60.:
            if abs(junk1 - round(junk1)) < 1e-7: # full hours
               mystr = "putlabel 0.5 %s\uh\d%s\um\d\n" %(hms[0],amin)
            else: # only put arcminutes
               mystr = "putlabel 0.5 %s\um\d\n" %(amin)
         else:
            if abs(junk1 - round(junk1)) < 1e-7: # full hours
               mystr = "putlabel 0.5 %s\uh\d%s\um\d%s\us\d\n" %(hms[0],amin,asec)
            elif abs(junk2 - round(junk2)) < 1e-7: # full arcminutes
               mystr = "putlabel 1 %s\um\d%s\us\d\n" %(amin,asec)
            else:
               mystr = "putlabel 1 %s\us\d\n" %(asec)
         stack.append(mystr)

         # get remainder and convert to integer arcmin
         #frac = tmpra%int(tmpra)
         #frac = int(round(60*frac))
         #stack.append("move %g yoffset\n" %x1)
         #stack.append("putlabel 0.5 %s\um\d\n" %frac)
      else:
         x2 = (tmpra - b3)/m3
         y2 = ymin + ylength/2.
      fp.write("move %g %g\n" %(x1,y1))
      fp.write("draw %g %g\n" %(x2,y2))
      tmpra = tmpra - stepra
      
   # top edge
   # ra,dec for the two corners
   ra1,dec1 = wcs.xy2sky([xmin,xmax],[ymax,ymax])
   # ra,dec inset by a tickmark length (major ticks)
   ra2,dec2 = wcs.xy2sky([xmin,xmax],[ymax-ylength,ymax-ylength])
   # ra,dec inset by half a tickmark length (minor ticks)
   ra3,dec3 = wcs.xy2sky([xmin,xmax],[ymax - ylength/2.,ymax - ylength/2.])

   m1 = (ra1[1] - ra1[0])/(15*(xmax-xmin))
   b1 = ra1[0]/15. - m1*xmin
   m2 = (ra2[1] - ra2[0])/(15*(xmax-xmin))
   b2 = ra2[0]/15. - m2*xmin
   m3 = (ra3[1] - ra3[0])/(15*(xmax-xmin))
   b3 = ra3[0]/15. - m3*xmin
   tmpra = int(ra1[0]/15.)
   while tmpra < ra1[0]/15.:
      tmpra += stepra
   if tmpra > ra1[0]/15.:
      tmpra = tmpra - stepra

   fp.write('#Top Edge\n')
   while tmpra >= ra1[1]/15.:
      x1 = (tmpra - b1)/m1
      y1 = ymax
      junk = tmpra/ralabel
      if abs(junk - round(junk)) < 1e-7: # major tickmark
         x2 = (tmpra - b2)/m2
         y2 = ymax - ylength
      else:
         x2 = (tmpra - b3)/m3
         y2 = ymax - ylength/2.
      fp.write("move %g %g\n" %(x1,y1))
      fp.write("draw %g %g\n" %(x2,y2))
      tmpra = tmpra - stepra

   # left edge
   # ra,dec for the two corners
   ra1,dec1 = wcs.xy2sky([xmin,xmin],[ymin,ymax])
   # ra,dec inset by a tickmark length (major ticks)
   ra2,dec2 = wcs.xy2sky([xmin+xlength,xmin+xlength],[ymin,ymax])
   # ra,dec inset by half a tickmark length (minor ticks)
   ra3,dec3 = wcs.xy2sky([xmin + xlength/2.,xmin + xlength/2.],[ymin,ymax])

   if len(tmpdec) == 2:
      stepdec  = tmpdec[0]/60.
      declabel = tmpdec[1]/60.
   else:
      stepdec,declabel = getstepdec(dec1[0],dec1[1])

   # compute slopes and intercepts
   m1 = (dec1[1] - dec1[0])/(ymax-ymin)
   b1 = dec1[0] - m1*ymin
   m2 = (dec2[1] - dec2[0])/(ymax-ymin)
   b2 = dec2[0] - m2*ymin
   m3 = (dec3[1] - dec3[0])/(ymax-ymin)
   b3 = dec3[0] - m3*ymin
   tmpdec = int(dec1[0])

   if tmpdec < 0:
      while tmpdec > dec1[0]:
         tmpdec = tmpdec - stepdec
      if tmpdec < dec1[0]:
         tmpdec = tmpdec + stepdec # overshoot by 1 step
   else:
      while tmpdec < dec1[0]:
         tmpdec = tmpdec + stepdec
   
   stack.append('\n# DEC Labels\n')
   fp.write('#Left Edge\n')
   while tmpdec <= dec1[1]:
      y1 = (tmpdec - b1)/m1
      x1 = xmin
      junk = tmpdec/declabel
      if abs(junk - round(junk)) < 1e-7: # major tickmark
         y2 = (tmpdec - b2)/m2
         x2 = xmin + xlength
         stack.append("move xoffset %g\n" %(y1-0.5*ylength))
         dms = deg2sex(tmpdec,'dec')
         amin = '%02d' % dms[1]
         if stepdec < 1/3600.: # increment smaller than 1 arcsecond
            asec = '%04.1f' %dms[2]
         else:
            asec = '%02d' %dms[2]
         junk1 = tmpdec/1. # test for full degrees
         junk2 = tmpdec/0.016666666 # test for full arcminutes
         if declabel >= 1:
            mystr = "putlabel 1 %d\u\(902)\d\n" %dms[0] # full degrees
         elif declabel >= 1/60.:
            if abs(junk1 - round(junk1)) < 1e-7: # full degree mark
               mystr = "putlabel 1 %s\u\(902)\d%s'\n" %(dms[0],amin)
            else: # only put arcminutes
               mystr = "putlabel 1 %s'\n" %(amin)
         else:
            if abs(junk1 - round(junk1)) < 1e-7: # full degree mark
               mystr = "putlabel 1 %s\u\(902)\d%s'%s''\n" %(dms[0],amin,asec)
            elif abs(junk2 - round(junk2)) < 1e-7: # full arcminutes
               mystr = "putlabel 1 %s'%s''\n" %(amin,asec)
            else:
               mystr = "putlabel 1 %s''\n" %(asec)
         stack.append(mystr)
      else:
         y2 = (tmpdec - b3)/m3
         x2 = xmin + xlength/2.
      fp.write("move %g %g\n" %(x1,y1))
      fp.write("draw %g %g\n" %(x2,y2))
      tmpdec = tmpdec + stepdec

   # right edge
   # ra,dec for the two corners
   ra1,dec1 = wcs.xy2sky([xmax,xmax],[ymin,ymax])
   # ra,dec inset by a tickmark length (major ticks)
   ra2,dec2 = wcs.xy2sky([xmax-xlength,xmax-xlength],[ymin,ymax])
   # ra,dec inset by half a tickmark length (minor ticks)
   ra3,dec3 = wcs.xy2sky([xmax - xlength/2.,xmax - xlength/2.],[ymin,ymax])

   m1 = (dec1[1] - dec1[0])/(ymax-ymin)
   b1 = dec1[0] - m1*ymin
   m2 = (dec2[1] - dec2[0])/(ymax-ymin)
   b2 = dec2[0] - m2*ymin
   m3 = (dec3[1] - dec3[0])/(ymax-ymin)
   b3 = dec3[0] - m3*ymin
   tmpdec = int(dec1[0])
   if tmpdec < 0:
      while tmpdec > dec1[0]:
         tmpdec = tmpdec - stepdec
      if tmpdec < dec1[0]:
         tmpdec = tmpdec + stepdec # overshoot by 1 step
   else:
      while tmpdec < dec1[0]:
         tmpdec = tmpdec + stepdec
   fp.write('#Right Edge\n')
   while tmpdec <= dec1[1]:
      y1 = (tmpdec - b1)/m1
      x1 = xmax
      junk = tmpdec/declabel
      if abs(junk - round(junk)) < 1e-7: # major tickmark
         y2 = (tmpdec - b2)/m2
         x2 = xmax - xlength
      else:
         y2 = (tmpdec - b3)/m3
         x2 = xmax - xlength/2.
      fp.write("move %g %g\n" %(x1,y1))
      fp.write("draw %g %g\n" %(x2,y2))
      tmpdec = tmpdec + stepdec
   
   # print out stack now
   for line in stack:
      fp.write(line)
   fp.write('free xoffset yoffset\n')
   fp.close()
