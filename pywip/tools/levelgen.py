import numpy

def levelgen(start,stop,step=1,unit='step',fac=1):
   """Generate levels for contour() command.
   
      Returns a list of the specified levels.
      
      start - start value
      stop  - stop value (included, unlike normal python convention)
      step  - step size or number of output levels (depending on unit)
      unit  - controls how step keyword is handled.  Can be step or num
      fac   - a factor to multiply each output unit by."""
   
   if unit == 'step':
      levs = fac*numpy.arange(start,stop+step,step)
      if levs[-1] > fac*stop: # endpoint outside range, so exclude
         levs = levs[:-1]
   elif unit == 'num':
      levs = fac*numpy.linspace(start,stop,step)
   return levs.tolist()
