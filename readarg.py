#!/usr/bin/env python
"""Routine to make it easy to read command line arguments in standard
-letter format.

lists can be given as e.g.: 1-3;5,6 which becomes: [[1,2,3],[5,6]]
File globbing and expansion of ~ is supported for strings
@filename will read filename and put each line as an element in a list
"""
#   14 Sept 2012  Forked from readcmd.py and starting changing
import glob,os,re,sys

class ReadArg(object):
   def __init__(self,spec,head=None):
      """Create ReadArg object to read commandline with validation
      
         spec = must be a multi-line string, list of strings, or a single 
                string specifying a filename.
         
         head = pass header as a string here.  Any string here will be 
                prepended to header parsed from spec."""
      # [keyword][0+ space]=[0+space][1+ non whitespace][1+ whitespace][# sign][0+ any char]
      pattern0 = r"#(.*)" # full line comment
      pattern1 = r"(-[a-zA-Z0-9])\s*(\S+)\s+#(.*)" # with a comment
      pattern2 = r"(-[a-zA-Z0-9])\s*(\S+)\s*"      # without a comment
      pattern3 = r"([a-zA-Z0-9]+)\s*(\S+)\s+#(.*)" # positional argument+comment
      pattern4 = r"([a-zA-Z0-9]+)\s*(\S+)\s*"      # positional argument
      pattern3 = r"(\w+)=(\S+)" # key=value on command line

      if isinstance(spec,str):
         if os.path.isfile(spec): # read spec from a file
            fp = open(spec,'r')
            speclist = fp.readlines()
            fp.close()
         else:
            speclist = spec.split('\n')
      elif isinstance(spec,list) or isinstance(spec,tuple):
         speclist = list(spec)
      else:
         self._error("TypeError: spec must be string, list, or tuple")
      
      self.name = sys.argv[0]
      self.args = {}
      if head is None:
         self.head = [] # will hold head comments on usage
      else:
         self.head = [head]
      for line in speclist: # first read spec file for defaults and help
         if line.strip() == '': # skip blank lines
            continue
         m = re.match(pattern0,line.strip()) # look for comment lines
         if m is not None:
            self.head.append(m.group(1).strip())
         else:
            m = re.match(pattern1,line.strip())
            if m is None: # didn't match with a comment, try without
               m = re.match(pattern2,line.strip())
               if m is None:
                  self._error("SyntaxError: Cannot read '%s' from spec" %line)
               key     = m.group(1).strip()
               value   = m.group(2).strip()
               comment = ""
            else:
               key    = m.group(1).strip()
               value  = m.group(2).strip()
               comment= m.group(3).strip()
            if self.args.has_key(key):
               self._error("KeyError: Duplicate keyword '%s' in spec" %key)
            self.args[key] = [value,comment]
      self.validkeys = self.args.keys() # valid keywords
      
      if len(sys.argv) > 1: # stuff given on command line
         junk = {} # will hold all keys read from command line
         
         # check to see if user wants help first
         if '-h' in sys.argv or '--help' in sys.argv or 'help=h' in sys.argv:
            print self
            sys.exit()

         # now loop over command line and parse key=value pairs   
         for tmp in sys.argv[1:]:
            m = re.match(pattern3,tmp)
            if m is None:
               self._error("SyntaxError: Cannot read '%s'" %tmp)
            key   = m.group(1)
            value = m.group(2)
            if junk.has_key(key):
               self._error("KeyError: Duplicate keyword '%s'" %key)
            junk[key] = value
         
         # now substitute command line keywords for defaults
         for key in junk.iterkeys():
            if key not in self.validkeys:
               self._error("KeyError: Unknown keyword %s" %key)
            self.args[key][0] = junk[key] # replace value, but not comment
      self._checkRequired()
      
   def getbool(self,key):
      """Return keyword value as a boolean True/False.  A value of None returns
         None.

         Can understand True,False,1,0,yes,no, and None.  Any capitalization
         accepted (except for None).
         
         key = keyword given as a string"""

      self._checkKey(key)
      temp = self.args[key][0]
      try:
         value = self._convertBool(temp)
         return value
      except ValueError:
         self._error("ValueError: %s is not a valid boolean for keyword %s" %(temp,key))
      
   def getfloat(self,key,min=None,max=None,option=None):
      """Return keyword value as a float.  A value of None returns None.

         key    = keyword given as a string
         min    = check for minimum value 
         max    = check for maximum value
         option = list/tuple of allowed values"""

      self._checkKey(key)
      value = self.args[key][0]
      if value == 'None':
         return None
      else:
         try:
            tmp = float(value)
            if min is not None or max is not None:
               self._checkMinMax(key,tmp,min,max)
            if option is not None:
               self._checkOption(key,tmp,option)
            return tmp
         except ValueError:
            self._error("ValueError: %s is not a valid float for keyword %s" %(value,key))
      
   def getint(self,key,min=None,max=None,option=None):
      """Return keyword value as integer.  A value of None returns None.

         key    = keyword given as a string
         min    = check for minimum value 
         max    = check for maximum value
         option = list/tuple of allowed values"""

      self._checkKey(key)
      value = self.args[key][0]
      if value == 'None':
         return None
      else:
         try:
            tmp = int(value)
            if min is not None or max is not None:
               self._checkMinMax(key,tmp,min,max)
            if option is not None:
               self._checkOption(key,tmp,option)
            return tmp
         except ValueError:
            self._error("ValueError: %s is not a valid integer for keyword %s" %(value,key))
      
   def getkeys(self,comment='#',format=False):
      """Make a short string of all keyword=values.
      
         Can format for 80 chars per line and also add a comment symbol 
         at the beginning of each line
         
         comment = comment character for each line (can be None)
         format  = Boolean True/False on whether to format output to 80 chars"""

      keys = self.validkeys
      keys.sort()
      outstr = ""
      if comment is not None:
         outstr += "%s " %(str(comment))
      outstr += "%s " %self.name
                  
      n = len(outstr)
      for k in keys:
         tmp = '%s=%s ' %(k,self.args[k][0])
         n += len(tmp)
         if format is True and n > 80:
            outstr += "\n"
            if comment is not None:
               outstr += "%s " %(str(comment))
            n = len(tmp) + 2
         outstr += tmp
      outstr += "\n"
      return outstr

   def getlistbool(self,key,length=None):
      """Return keyword value as a list of booleans.  A value of None returns
         an empty list.
         
         key     = keyword given as a string
         length  = int/list/tuple of allowed number of elements in list"""
         
      out = self._getlistbase(key,type=bool,length=length)
      return out

   def getlistfloat(self,key,length=None,min=None,max=None,option=None):
      """Return keyword value as a list of floats.  A value of None returns an
         empty list.
         
         key    = keyword given as a string
         length = int/list/tuple of allowed number of elements in list
         min    = check for minimum value 
         max    = check for maximum value
         option = list/tuple of allowed values"""

      out = self._getlistbase(key,type=float,length=length,min=min,max=max,
            option=option)
      return out
      
   def getlistint(self,key,length=None,min=None,max=None,option=None):
      """Return keyword value as a list of integers.  A value of None returns
         an empty list.
         
         key    = keyword given as a string
         length = int/list/tuple of allowed number of elements in list
         min    = check for minimum value 
         max    = check for maximum value
         option = list/tuple of allowed values"""

      out = self._getlistbase(key,type=int,length=length,min=min,max=max,
            option=option)
      return out
      
   def getliststr(self,key,comment='#',exist=None,length=None,option=None):
      """Return keyword value as a list of strings.  A value of None returns
         an empty list.

         key     = keyword given as a string
         comment = String character for comment lines to ignore in an @file
         exist   = Can check to make sure all all input files exist.  Default is
                   to not check.  Note, if you give an @file, then the @file
                   will always be checked for existance no matter what.
         length  = int/list/tuple of allowed number of elements in list
         option  = list/tuple of allowed values (for each element)"""
         
      out = self._getlistbase(key,type=str,comment=comment,exist=exist,
            length=length,option=option)
      return out
      
   def getstr(self,key,exist=None,option=None):
      """Return keyword value as a string.  A value of None returns None.

         key     = keyword given as a string
         exist   = Assume keyword references a filename, check for existance 
                   or not (boolean)
         option  = str/list/tuple of allowed values."""
      
      self._checkKey(key)
      value = self.args[key][0]
      if value == 'None':
         return None
      if exist is True: # filename must exist
         self._checkExist(value)
      elif exist is False: # filename must NOT exist
         self._checkNotExist(value)
      if option is not None:
         self._checkOption(key,value,option)
      return value
      
   def __str__(self):
      """Print out the current keywords, their values and a help message, if
         one is present."""

      key1 = [] # keys with missing required arguments
      key2 = [] # keys with optional/default arguments
      maxlength = 0
      for k,v in self.args.iteritems():
         n = len(k+v[0])
         if n > maxlength:
            maxlength = n
         if v[0] == '???':
            key1.append(k)
         else:
            key2.append(k)
      key1.sort()
      key2.sort()
      output = ""
      for line in self.head:
         output += "%s\n" %line
      output += "------------------------------------------------------------\n"
      for k in key1: # loop over required keywords
         junk = 3 + maxlength - len(k) - len(self.args[k][0])
         space = ' '*junk
         output += "%s=%s%s%s\n" %(k,self.args[k][0],space,self.args[k][1])
      for k in key2: # loop over remaining keywords
         junk = 3 + maxlength - len(k) - len(self.args[k][0])
         space = ' '*junk
         output += "%s=%s%s%s\n" %(k,self.args[k][0],space,self.args[k][1])
      output += "------------------------------------------------------------"
      return output

   def _atFile(self,filename,comment):
      """Tries to read an at-file, a file that contains keyword values.
         Specified by key=@filename.  It converts the file to a
         string of comma separated values.  Blank lines are skipped.

         filename - string name of file.  Assumes @ has been stripped off
         comment  - character to use on lines that should be ignored as comments"""

      self._checkExist(filename)
      fp = open(filename,'r')
      tmp  = [line.partition(comment)[0].strip() for line in fp] # no comments
      data = [a for a in tmp if len(a) > 0] # skip blank lines
      fp.close()
      return data

   def _checkExist(self,*files):
      """Given an input file name as a string or a list of filenames will check to
         make sure each file exists.  If not, a fatal error will occur using
         error()

         If filename is a dash or a period, does not check for existance.  This
         is because I allow dashes to be sys.stdin/sys.stdout, and period to 
         be /dev/null"""

      if len(files) == 0:
         self._error("IndexError: You must pass at least one argument to _checkExist()")
      for f in files:
         if isinstance(f,str): # check a single filename
            if f == '-': # give a pass since it is sys.stdin
               pass
            elif not os.path.exists(f):
               t = os.path.split(f)[1]
               self._error("IOError: Required file %s is missing" %t)
         elif isinstance(f,(list,tuple)): # a list or tuple
            for a in f:
               if a == '-': # give a pass since it is sys.stdin
                  pass
               elif not os.path.exists(a):
                  t = os.path.split(a)[1]
                  self._error("IOError: Required file %s is missing" %t)
         else:
            self._error("TypeError: _checkExist() can only check types str,list, and tuple")

   def _checkKey(self,key):
      """Check to see if key is part of self.validkeys."""
         
      if key in self.validkeys:
         pass
      else:
         self._error("KeyError: '%s' is not a valid keyword" %key)

   def _checkMinmax(self,key,value,minval=None,maxval=None):
      """Check to see if value is within bounds set by minval and maxval"""

      if minval is not None:
         if value < minval:
            self._error("ValueError: %s is < minimum value of %f" %(key,minval))
      if maxval is not None:
         if value > maxval:
            self._error("ValueError: %s is > maximum value of %f" %(key,maxval))

   def _checkNotExist(self,*files):
      """Given an input file list, will check to make sure each files does NOT
         exist.  If any one of the files exists, a fatal error will occur
         using error()

         If filename is a dash or a period, does not check for existance.  This
         is because I allow dashes to be sys.stdin/sys.stdout, and period to 
         be /dev/null"""

      if len(files) == 0:
         self._error("IndexError: You must pass at least one argument to _checkNotExist()")
      for f in files:
         if isinstance(f,str): # check a single filename
            if f in ('.','-'): # give these a pass as described in docstring
               pass
            elif os.path.exists(f):
               t = os.path.split(f)[1]
               self._error("IOError: File %s already exists" %t)
         elif isinstance(f,(list,tuple)): # a list
            for a in f:
               if a in ('.','-'): # give these a pass as described in docstring
                  pass
               elif os.path.exists(a):
                  t = os.path.split(a)[1]
                  self._error("IOError: File %s already exists" %t)
         else:
            self._error("TypeError: _checkNotExist can only check types str,list, and tuple")

   def _checkOption(self,key,value,option):
      """Check whether a value is among valid options"""

      if value in option:
         pass
      else:
         self._error("IndexError: Allowed options for key %s are %s" %(key,str(option)))

   def _checkRequired(self):
      """Checks to see that no blank values exist"""

      usage = "Usage: %s " %self.name
      missing   = 0 # number of missing keywords
      extraFlag = False # set to true if >= 1 keyword is not missing
      
      for k in self.validkeys:
         if self.args[k][0] == '???': # ??? means a required value
            usage = usage + "%s=??? " %k
            missing += 1
         else:
            extraFlag = True
      if missing > 0:
         if extraFlag is True:
            usage = usage + "..."
         self._error("KeyError: Missing Keywords: %s" %usage)

   def _convertBool(self,value):
      """Convert value to a Boolean.  Accepts True, False, 1,0, yes, no, and
         None.  A value of None returns None."""      
      
      if value == 'None':
         return None
      if value.lower() in ('1','yes','true','y'):
         return True
      elif value.lower() in ('0','no','false','n'):
         return False
      else:
         self._error("ValueError: '%s' is not a valid boolean" %value)

   def _convertValues(self,value,outlist,type,exist,min,max):
      """Helper function for getlist() to convert values in list to boolean,
         string, integer, or float"""
      itemlist = []
      if type is int:
         for s in outlist:
            try:
               temp = map(int,s.split('-')) # parse 1-4 as 1,2,3,4
            except ValueError:
               self._error("ValueError: %s is not a valid range of integers" %s)
            start = temp[0]
            stop  = temp[-1]
            if start > stop:
               self._error("ValueError: range minimum (%d) > maximum (%d)" %(start,stop))
            itemlist = itemlist + range(start,stop+1)
      elif type is float:
         try:
            itemlist = map(float,outlist)
         except ValueError:
            self._error("ValueError: %s is not a valid list of floats" %value)
      elif type is str:
         itemlist = outlist
         if exist is True: # make sure files exist in the list
            self._checkExist(outlist)
         elif exist is False: # make sure files don't exist in the list
            self._checkNotExist(outlist)
      elif type is bool:
         try:
            itemlist = map(self._convertBool,outlist)
         except ValueError:
            self._error("ValueError: %s is not a valid list of booleans" %value)
      else:
         self._error("TypeError: type for getlist() must be str,int, or float")
      if min is not None or max is not None:
         for tmp in itemlist:
            self._checkMinMax(value,tmp,min,max)
      return itemlist
   
   def _error(self,msg):
      """Print out an error message to screen and quit"""
      sys.stderr.write("### %s\n" %msg)
      sys.exit()

   def _getlistbase(self,key,type=str,comment='#',min=None,max=None,
      option=None,length=None,exist=None):
      """Return keyword value as a list.  A value of None returns an empty list.

         key     = keyword given as a string
         type    = Can be either bool, float, int, or str (for boolean,
                   float, integer, or string)
         comment = String character for comment lines to ignore in an @file
         min     = check for minimum value (for each element)
         max     = check for maximum value (for each element)
         option  = list/tuple of allowed values (for each element)
         length  = int/list/tuple of allowed number of elements in list
         exist   = Can check to make sure all all input files exist.  Default is
                   to not check.  Note, if you give an @file, then the @file
                   will always be checked for existance no matter what."""

      self._checkKey(key)
      value = self.args[key][0]
      outlist = []
      if value == 'None':
         return outlist
      for alist in value.split(';'):# split by semicolon for nested lists
         blah = []
         for junk in alist.split(','): # loop over comma-separated list
            if junk[0] == '@': # read from atfile
               temp = self._atFile(junk,comment)
               blah = blah + temp
            else: # try file globbing
               temp = glob.glob(junk)
               if len(temp) == 0: # try to expand ~
                  temp = os.path.expanduser(junk)
                  if temp == junk: # no match so add exact input
                     blah.append(junk)
                  else:
                     blah = blah + temp
               else:
                  blah = blah + temp
         blah = self._convertValues(value,blah,type,exist,min,max)
         if option is not None:
            for value in blah:
               self._checkOption(key,value,option)
         outlist.append(blah)
      if len(outlist) == 1: # only one nested list, so removing nesting
         outlist = outlist[0]
      if length is not None:
         nval = len(outlist)
         if isinstance(length,int):
            if nval != length:
               if nval == 1:
                  self._error("IndexError: key %s should have 1 element" %(key))
               else:
                  self._error("IndexError: key %s should have %d elements" %(key,length))
         elif isinstance(length,list) or isinstance(length,tuple):
            if nval not in length:
               self._error("IndexError: key %s should have %s elements" %(key,str(length)))
         else:
            self._error("IndexError: length parameter for key %s should be int/list/tuple" %key)
      return outlist
      
if __name__ == "__main__":
   spec = """
   # Compute polarization vectors from a sharp_combine map
      in     = ???   # Input combine.fits
      out    = ???   # Output file of vectors
      sigma  = 3     # p/dp cutoff for vectors
      skip   = 4     # Only plot every ith pixel (since we oversample 4x)
      offset = 0,0   # Offset in x,y for start of vectors
      debias = False # Debias Polarizations (Ricean correction)"""
   bob = ReadCmd(spec)
   inFile  = bob.getstr("in")
   outFile = bob.getstr("out")
   sigma   = bob.getfloat("sigma")
   skip    = bob.getint("skip")
   offset  = bob.getlistint("offset",length=2)
   debias  = bob.getbool("debias")
   print bob
   print bob.getkeys(format=True),
