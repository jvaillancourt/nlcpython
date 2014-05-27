#!/usr/bin/env python
"""Script to generate proper WCS tickmarks in WIP.  WIP assumes the sky is
flat, and so can be off for large fields.  This uses the worldpos module."""

import nlclib

def deg2sex(value,coord):
   '''Convert degrees to sexagesimal, unless it is already in sexagesimal'''
   
   try:
      tmp = map(float,str(value).split(':'))
   except ValueError:
      nlclib.error('Invalid string given for conversion to sexagesimal: %s' %value)

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

def wcslabels(wcs,xmin,xmax,ymin,ymax,side='bottom'):
   """Determine WCS labeling"""
   
   if side == 'bottom':
      ra,dec = wcs.wcs_pix2sky([xmin,xmax],[ymin,ymin],1)
   elif side == 'top':
      ra,dec = wcs.wcs_pix2sky([xmin,xmax],[ymax,ymax],1)
   elif side == 'left':
      ra,dec = wcs.wcs_pix2sky([xmin,xmin],[ymin,ymax],1)
   elif side == 'right':
      ra,dec = wcs.wcs_pix2sky([xmax,xmax],[ymin,ymax],1)
   ra = ra/15. # convert to hours
   stepra,ralabel   = getstepra(ra[0],ra[1])
   stepdec,declabel = getstepdec(dec[0],dec[1])
   mylabel = []
   myticks = []

   firstFlag = True # set to false after first label written
   if side in ('bottom','top'): # bottom or top edges
      # find starting RA on left-hand side
      tmpra = int(ra[0]) # integer number of hours
      while tmpra < ra[0]:
         tmpra += stepra
      if tmpra > ra[0]:
         tmpra = tmpra - stepra

      slope = (ra[1] - ra[0])/(xmax-xmin)
      intercept = ra[0] - slope*xmin

      while tmpra >= ra[1]: # step by hours, not degrees
         x = (tmpra - intercept)/slope
         y = ymin
         #myticks.append(x)
         junk = tmpra/ralabel
         if abs(junk - round(junk)) < 1e-7: # major tickmark
            myticks.append(x)
            hms = deg2sex(15*tmpra,'ra')
            amin = '%02d' % hms[1]
            if ralabel < 1/3600.: # increment smaller than 1 hour-second
               asec = '%04.1f' %hms[2]
            else:
               asec = '%02.0f' %hms[2]

            junk1 = tmpra/1. # test for full hours
            junk2 = tmpra/0.016666666 # test for full hour-minutes
            if ralabel >= 1:
               mylabel.append(r"$%s^\mathrm{h}$" %hms[0])
            elif ralabel >= 1/60.:
               if abs(junk1 - round(junk1)) < 1e-7: # full hours
                  mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}$" %(hms[0],amin))
               else: # only put arcminutes
                  mylabel.append(r"$%s^\mathrm{m}$" %(amin))
            else:
               if firstFlag or abs(junk1 - round(junk1)) < 1e-7: # full hours
                  mylabel.append(r"$%s^\mathrm{h}%s^\mathrm{m}%s^\mathrm{s}$" %(hms[0],amin,asec))
                  firstFlag = False
               elif abs(junk2 - round(junk2)) < 1e-7: # full arcminutes
                  mylabel.append(r"$\mathrm{%s^m%s^s}$" %(amin,asec))
               else:
                  mylabel.append(r"$\mathrm{%s^s}$" %(asec))
         else:
            pass
            #mylabel.append('')
         tmpra = tmpra - stepra
   elif side in ('left','right'):      
      tmpdec = int(dec[0])
      if tmpdec < 0:
         while tmpdec > dec[0]:
            tmpdec = tmpdec - stepdec
         if tmpdec < dec[0]:
            tmpdec = tmpdec + stepdec # overshoot by 1 step
      else:
         while tmpdec < dec[0]:
            tmpdec = tmpdec + stepdec
         if tmpdec > dec[0]:
            tmpdec = tmpdec - stepdec
      # compute slopes and intercepts
      slope = (dec[1] - dec[0])/(ymax-ymin)
      intercept = dec[0] - slope*ymin
   
      while tmpdec <= dec[1]:
         y = (tmpdec - intercept)/slope
         x = xmin
         junk = tmpdec/declabel
         #myticks.append(y)
         if abs(junk - round(junk)) < 1e-7: # major tickmark
            myticks.append(y)
            dms = deg2sex(tmpdec,'dec')
            amin = '%02d' % dms[1]
            if stepdec < 1/3600.: # increment smaller than 1 arcsecond
               asec = '%04.1f' %dms[2]
            else:
               asec = '%02.0f' %dms[2]
            junk1 = tmpdec/1. # test for full degrees
            junk2 = tmpdec/0.016666666 # test for full arcminutes
            if declabel >= 1:
               mylabel.append(r"$%s^\circ$" %dms[0]) # full degrees
            elif declabel >= 1/60.:
               if abs(junk1 - round(junk1)) < 1e-3: # full degree mark
                  mylabel.append(r"$%s^\circ%s^'$" %(dms[0],amin))
               else: # only put arcminutes
                  mylabel.append(r"%s^'" %(amin))
            else:
               if firstFlag or abs(junk1 - round(junk1)) < 1e-3: # full degree mark
                  mylabel.append(r"$%s^\circ%s^'%s^{''}$" %(dms[0],amin,asec))
                  firstFlag = False
               elif abs(junk2 - round(junk2)) < 1e-3: # full arcminutes
                  mylabel.append(r"$%s^'%s^{''}$" %(amin,asec))
               else:
                  mylabel.append(r"$%s^{''}$" %(asec))
         else:
            pass
            #mylabel.append('')
         tmpdec = tmpdec + stepdec
   return myticks,mylabel
