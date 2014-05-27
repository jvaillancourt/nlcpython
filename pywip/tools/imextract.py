from .. import header
import pyfits
import tempfile

def imextract(image,ext=1,headerext=None):
   """Extract the given extension/plane and save to a new file.
   
      Returns a string with the name of the temporary file.  This filename
      is also added to pywip's internal list of temporary files, meaning it
      will automatically be deleted after savefig() is called.
      
      imextract() is often needed because WIP doesn't know what to do with
      multi-extension FITS images.

      image     - image name
      ext       - extension number, defaults to 1
      headerext - Extension number to use for header.  Defaults to same value
                  as ext"""
   
   junk = tempfile.mktemp(suffix='.fits')
   try:
      fp = pyfits.open(img)
   except IOError:
      header._error("Cannot open file `%s'" %img)

   next = len(fp)
   ext = _decode_ext(fp,ext)
   if headerext is None:
      headerext = ext
   else:
      headerext = _decode_ext(fp,headerext)
   
   data = fp[ext].data
   hdu = pyfits.PrimaryHDU(data)
   hdu.header = fp[headerext].header
   hdu.writeto(junk)
   fp.close()
   header._tmplist.append(junk)
   return junk

def _decode_ext(fp,ext):
   """Decode ext, which may be string to proper fits extension number"""

   next = len(fp)
   if isinstance(ext,str): # extension is a string name, try to decode
      found = False
      for i in range(next):
         try:
            hdrkey = fp[i].header['extname'].strip()
            if hdrkey.lower() == ext:
               ext = i
               found = True
               break
         except KeyError:
            pass
   elif isinstance(ext,int):
      ext = ext - 1 # make zero-based
      found = True
   else:
      fp.close()
      header._error("extension must be a integer or string!")
      
   if found is False:
      fp.close()
      header._error("Extension named %s not found!" %ext)

   if ext not in range(next):
      header._error("Extension # %d is not in allowed range 1-%d" %(ext,next))

   return ext
