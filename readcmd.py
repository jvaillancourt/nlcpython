#!/usr/bin/env python
"""Routine to make it easy to read command line arguments in a keyword=value
style format.  Also has support for --help, help=, -h.  Version keyword can
be printed with -v or --version.

lists can be given as e.g.: 1-3;5,6 which becomes: [[1,2,3],[5,6]]
File globbing and expansion of ~ is supported for strings
@filename will read filename and put each line as an element in a list

Available variables:
self.name        # name of calling program
self.validkeys   # list of allowed keywords given as strings
"""
#
#   15-mar-2003   Created as miriad.py                      PJT
#   16-apr-2003   added run,keyr,keyi,keya\n
#   05-mar-2004   Added help comments nemo style            NLC
#   16-may-2004   Deleted all the code we don't use for map2  NLC
#   19-feb-2008   Changed keya, keyi, and keyr to not use the
#                 keypresent function.  This allows the programmer to
#                 specify a default keyword value of nothing.  However,
#                 error checking was added to keyini so that if the user
#                 tries to input an empty keyword on the command line,
#                 than an error message will still occur.  Also, some cleanups
#                 to remove extraneous comments, combined the badkeyword
#                 function with keya, and added the keyf function which works
#                 the same as keyr.
#   07-may-2008   Cleanup and simplifying the code.  Also made a blank keyword
#                 value return None or False.  False is returned for keyb, all
#                 others return None
#   19-nov-2008   More code cleanup.  Also added the write_keyval function and
#                 added spacing so the help text lines up with show_keyval
#   09-dec-2008   Sort the keywords when printing them
#   04-aug-2010   Added checking for required number of arguments in keyl
#   04-oct-2010   Added the check_existance and check_nonexistance.  I may
#                 move these to optional keywords in keya()
#   20-oct-2010   check_existance and check_nonexistance can be called from
#                 keya() and keyl().  keyl() also has more smarts about ignoring
#                 comment lines and is more pythonic now.
#   8-may-2011    keyl() now accepts *,?, and [] shell-globbing now for input
#                 lists of files, and ~ for home directories.  You can also 
#                 make mixed lists of name, wildcards, tildes, and @files.
#   15-july-2011  keyl() will return a blank list instead of None.
#   18-july-2011  _at_file() will skip blank lines from input files
#   08-aug-2011   Just added some comments to various docstrings
#   26-sep-2011   Allow ranges to use dashes for keyl(val='i').
#   7-feb-2012    Two improvements.  First, keyl() now allows semicolons to 
#                 define nested lists.  Second, writekeys() can format the
#                 output to 80 characters per line.
#   24-april-2012 show_keyval() will sort output by listing required keywords
#                 first, then remaining keywords
#   26 April 2012 check_existance() and check_nonexistance() will now allow
#                 input filenames to be a - or . for sys.stdin/sys.stdout and
#                 /dev/null.  Also sort keywords in writekeys(), reorganized
#                 functions alphabetically, and deleted keyr().
#   16 Aug 2012   Added new arguments to check for min/max allowed values,
#                 and allowed options for keywords.  Also made error(),
#                 warning(), check_existance(), and check_nonexistance() 
#                 hidden functions.  Lastly, commented out dprintf() since
#                 it shouldn't be part of this module.  debug() statement
#                 might also disappear at a future date.
#   20 Aug 2012   Switch to raising errors rather than _error() function.
#                 Ditto for _warning().  Both have deprecation warnings 
#                 printed when used.
#   24 Aug 2012   Reimplemented code as readcmd.py.  Removed debug and dprintf,
#                 changed the way keywords specifications are done (see example
#                 in __main__).
#    6 Sep 2012   Fixed bug in getbool().  I forgot to return the value. Duh.
#   17 Sep 2012   Fixed bug with reading @files.  Also fixed typo in naming
#                 of _checkMinMax()
#    6 Nov 2012   Sort validkeys
#   20 Nov 2012   Allowed values to have spaces, which should have been
#                 obvious from the start.
#   18 Dec 2012   Changed so format keyword in getkeys() is a number for line
#                 length, not just true/false
#   01 Apr 2013   Added ignorecase option to getstr() and getliststr() methods.
#   03 Apr 2013   I think it is fixed now so that 1e4 can be interpreted as
#                 an integer
#   16 Jul 2013   Added option to print out current time in getkeys().  Useful
#                 for writing history to a FITS header
#   28 Aug 2013   Added ability for getstr() to check if string is a file or
#                 directory.  Haven't tested yet.  Need to add to getliststr().
#   02 Dec 2013   Added error() and warning() methods.  Since I seem to often
#                 import nlclib just for these two functions, why not have
#                 them here?  Plus, the built-in argparse module has similar
#                 functions.
#   17 Feb 2014   Added support in getliststr() for type checking.
#   02 Apr 2014   Added support for version keyword
import glob,os,re,sys
import time as timemodule

class ReadCmd(object):
   def __init__(self,spec,head=None):
      """Create ReadCmd object to read commandline with validation
      
         spec = must be a multi-line string, list of strings, or a single 
                string specifying a filename.
         
         head = pass header as a string here.  Any string here will be 
                prepended to header parsed from spec."""
      pattern0 = r"#(.*)"          # full line comment
      pattern1 = r"(\w+)\s*=(.+)"  # key=value
      pattern2 = r"(\w+)=(.+)"     # key=value on command line
      helpFlag = False  # set to true if -h, --help, help=h on cmd line
      versionFlag = False # set to true if -v or --version on cmd line

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
      
      self.name = os.path.split(sys.argv[0])[1]
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
            if m is None: # didn't match
               self._error("SyntaxError: Cannot read '%s' from spec" %line)
            else:
               key    = m.group(1).strip()
               junk   = m.group(2).strip()
               idx = junk.find('#')
               if idx == -1: # no comment
                  value = junk
                  comment = ""
               else:
                  n = junk.count('#')
                  if n == 1:
                     tmp = junk[:idx].strip()
                     if len(tmp) == 0: # no default value given
                        self._error("SyntaxError: Cannot read '%s' from spec" %line)
                     value = tmp
                     comment = junk[idx+1:].strip()
                  else: # n > 1
                     tmp = junk[:idx].strip()
                     if len(tmp) == 0: # first # sign is the value
                        value = '#'
                     else:
                        value = tmp
                     comment = junk[idx+1:].strip()
            if self.args.has_key(key):
               self._error("KeyError: Duplicate keyword '%s' in spec" %key)
            self.args[key] = [value,comment]
      self.validkeys = self.args.keys() # valid keywords
      self.validkeys.sort()
      
      if len(sys.argv) > 1: # stuff given on command line
         junk = {} # will hold all keys read from command line
         
         # now loop over command line and parse key=value pairs   
         for tmp in sys.argv[1:]:
            if tmp in ['-h','--help','help=h']: # user wants help
               helpFlag = True
            elif tmp in ['-v','--version']: # user wants version number
               versionFlag = True
            else:
               m = re.match(pattern2,tmp)
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
      if helpFlag:
         print self,
         sys.exit()
      if versionFlag:
         if 'version' in self.validkeys:
            print(self.getstr('version'))
         sys.exit()
      self._checkRequired()
      
   def error(self,msg):
      """Print a message to screen as a fatal error and quit"""
      sys.stderr.write("### Fatal Error! %s\n" %msg)
      sys.exit()

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
            tmp = float(value)
            if tmp%1 != 0:
               raise ValueError
            else:
               tmp = int(tmp)
            if min is not None or max is not None:
               self._checkMinMax(key,tmp,min,max)
            if option is not None:
               self._checkOption(key,tmp,option)
            return tmp
         except ValueError:
            self._error("ValueError: %s is not a valid integer for keyword %s" %(value,key))
      
   def getkeys(self,comment='#',format=None,time=False):
      """Make a short string of all keyword=values.
      
         Can format for 80 chars per line and also add a comment symbol 
         at the beginning of each line
         
         comment = comment character or string for each line (can be None)
         format  = Can set to a number to limit line length to that no. of
                   chars
         time    = If set to true, include current time in returned string"""

      keys = self.validkeys
      if comment is None or comment == '':
         commentchar = ''
      else:
         commentchar = "%s " %comment
         
      outstr = ''
      if time is True:
         outstr += "%s%s\n" %(commentchar,timemodule.asctime())
      outstr += "%s%s " %(commentchar,self.name)
      if format is not None:
         maxlen = format
      else:
         maxlen = 1e6
      n = len(commentchar) + len(self.name) + 1 # don't count len(time)
      for k in keys:
         tmp = '%s=%s ' %(k,self.args[k][0])
         n += len(tmp)
         if format is not None and n > maxlen:
            outstr += "\n%s" %commentchar
            n = len(tmp) + len(commentchar)
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
      
   def getliststr(self,key,comment='#',exist=None,length=None,option=None,
                  ignorecase=False,type=None):
      """Return keyword value as a list of strings.  A value of None returns
         an empty list.

         key     = keyword given as a string
         comment = String character for comment lines to ignore in an @file
         exist   = Can check to make sure all all input files exist.  Default is
                   to not check.  Note, if you give an @file, then the @file
                   will always be checked for existance no matter what.
         length  = int/list/tuple of allowed number of elements in list
         option  = list/tuple of allowed values (for each element)
         ignorecase = boolean on whether to ignore differences between
                      upper/lower case when checking options
         type       = set to 'file' to check if input is a file, or set to 
                      'dir' to check if input is a directory.  Only applies when
                      exist is also True"""
         
      out = self._getlistbase(key,type=str,comment=comment,exist=exist,
            length=length,option=option,ignorecase=ignorecase)
      if exist is True: # filename must exist
         if type is not None:
            self._checkType(type,out)
      return out
      
   def getstr(self,key,exist=None,option=None,ignorecase=False,type=None):
      """Return keyword value as a string.  A value of None returns None.

         key        = keyword given as a string
         exist      = Assume keyword references a filename, check for existance 
                      or not (boolean)
         option     = str/list/tuple of allowed values.
         ignorecase = boolean on whether to ignore differences between
                      upper/lower case when checking options
         type       = set to 'file' to check if input is a file, or set to 
                      'dir' to check if input is a directory.  Only applies when
                      exist is also True"""
      
      self._checkKey(key)
      value = self.args[key][0]
      if value == 'None':
         return None
      if exist is True: # filename must exist
         self._checkExist(value)
         if type is not None:
            self._checkType(type,value)
      elif exist is False: # filename must NOT exist
         self._checkNotExist(value)
      if option is not None:
         self._checkOption(key,value,option,ignorecase)
      return value
      
   def warning(self,msg):
      """Print a string of text as a warning"""

      sys.stderr.write("### Warning! %s\n" %msg)

   def __str__(self):
      """Print out the current keywords, their values and a help message, if
         one is present."""

      key1 = [] # keys with missing required arguments
      key2 = [] # keys with optional/default arguments
      maxlength = 0
      for k,v in self.args.iteritems():
         if k == 'version': # skip version keyword
            continue
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
      #output += "------------------------------------------------------------\n"
      for k in key1: # loop over required keywords
         junk = 3 + maxlength - len(k) - len(self.args[k][0])
         space = ' '*junk
         output += "   %s=%s%s%s\n" %(k,self.args[k][0],space,self.args[k][1])
      for k in key2: # loop over remaining keywords
         junk = 3 + maxlength - len(k) - len(self.args[k][0])
         space = ' '*junk
         output += "   %s=%s%s%s\n" %(k,self.args[k][0],space,self.args[k][1])
      output = output[:-1] # strip off trailing \n
      #output += "------------------------------------------------------------"
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

   def _checkMinMax(self,key,value,minval=None,maxval=None):
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
               if os.path.isdir(f):
                  self._error("IOError: Directory '%s' already exists" %t)
               else:
                  self._error("IOError: File '%s' already exists" %t)
         elif isinstance(f,(list,tuple)): # a list
            for a in f:
               if a in ('.','-'): # give these a pass as described in docstring
                  pass
               elif os.path.exists(a):
                  t = os.path.split(a)[1]
                  if os.path.isdir(a):
                     self._error("IOError: Directory '%s' already exists" %t)
                  else:
                     self._error("IOError: File '%s' already exists" %t)
         else:
            self._error("TypeError: _checkNotExist can only check types str,list, and tuple")

   def _checkOption(self,key,value,option,ignorecase=False):
      """Check whether a value is among valid options"""

      if ignorecase is True:
         temp = [a.lower() for a in option]
         if value.lower() in temp:
            pass
         else:
            self._error("IndexError: Allowed options for key %s are %s" %(key,str(option)))
      else:               
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

   def _checkType(self,typestr,*files):
      """"Given an input name as a string or a list of strings, will check to
          make sure each is a directory using os.path.isdir() or regular
          file, using os.path.isfile().
          
          Assumes that names have already been checked by _checkExist.  If name
          is a dash or a period, does not check.  This is because I allow dashes
          to be sys.stdin/sys.stdout, and period to  be /dev/null"""

      if typestr not in ('file','dir'):
         self._error("TypeError: _checkType() only checks file and dir types")

      for f in files:
         if isinstance(f,str): # check a single name
            if f == '-' or f == '.':
               pass
            else:
               if typestr == 'file':
                  if not os.path.isfile(f):
                     t = os.path.split(f)[1]
                     self._error("IOError: %s is not a regular file" %t)
               elif typestr == 'dir':
                  if not os.path.isdir(f):
                     t = os.path.split(f)[1]
                     self._error("IOError: %s is not a directory" %t)
         elif isinstance(f,(list,tuple)):
            for a in f:
               if f == '-' or f == '.':
                  pass
               else:
                  if typestr == 'file':
                     if not os.path.isfile(a):
                        t = os.path.split(a)[1]
                        self._error("IOError: %s is not a regular file" %t)
                  elif typestr == 'dir':
                     if not os.path.isdir(a):
                        t = os.path.split(a)[1]
                        self._error("IOError: %s is not a directory" %t)
         else:
            self._error("TypeError: _checkType() can only check types str,list, and tuple")

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
      option=None,length=None,exist=None,ignorecase=False):
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
               temp = self._atFile(junk[1:],comment)
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
               self._checkOption(key,value,option,ignorecase)
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
   print bob.getkeys(format=80),
