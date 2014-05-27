#!/usr/bin/env python
#
# Routine to make it easy to read command line arguments in a keyword=value
# style format.  Also has support for --help, help=, -h, etc, and setting
# a debug level.  Finally, includes the warning, error, and dprintf functions
# which may also be useful in scripting.
#
#   15-mar-2003   Created                                   PJT\n
#   16-apr-2003   added run,keyr,keyi,keya\n
#   05-mar-2004   Added help comments nemo style            NLC\n
#   16-may-2004   Deleted all the code we don't use for map2  NLC\n
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
import sys,os,time,glob

#   some global variables (private to Miriad.py)
_version = "3.5 (20-august-2012)"
_mkeyval = {}
_help    = {}
_name    = sys.argv[0] # name of command that calls miriad.py
_maxlen  = 0 # maximum length of keyword+value in _mkeyval

def debug():
   '''Gets the current debug level and returns it'''
   return _mkeyval['debug']

def keyini(keyval):
   """Initialize the values of all keywords, and check to see that all required
      keywords are present.

      keyval - A dictionary of keywords and values"""

   global _mkeyval, _help, _maxlen

   _quit    = 0 # Will be set to 1 if code should exit
   _help    = keyval.copy()
   _mkeyval = keyval.copy()
   _mkeyval['debug'] = 0 # Set default debug level to 0
   _warning('miriad.py is obsolete.  Switch to readcmd.')
   for key in keyval.keys():  # Parse for help comments if any
      if key == '_msg_':
         del(_mkeyval[key])
         continue
      idx = keyval[key].find('\n')
      if idx >= 0: # Found help comment
         _help[key]    = _help[key][idx+1:].strip()
         _mkeyval[key] = _mkeyval[key][:idx].strip()
      else: # No help comment found for this keyword
         _help[key] = ""

   for arg in sys.argv[1:]: # parse command line for new keyword values
      i = arg.find("=")
      if arg in ["--help","-h","help"]:
         _quit = 1
      elif i > 0:
         key = arg[0:i]
         val = arg[i+1:]
         if key == 'help':
            _quit = 1
         elif len(val) == 0:
            raise ValueError('keyword %s cannot have a blank value!' %key)
         elif _mkeyval.has_key(key):
             _mkeyval[key] = val
         elif key == 'debug':
            try:
               _mkeyval['debug'] = int(val)
            except ValueError:
               print 'debug=%s must be an integer' %val
               raise
         else:
             raise KeyError("keyword %s does not exist, try --help or -h" % arg)
      else:
         sys.stderr.write("### Warning! argument %s not understood, try --help or -h" % arg)
         sys.stderr.write("### Warning! Skipping and continuing.\n")
   for k,v in _mkeyval.iteritems(): # Find maximum length, for use in show_keyval
      if k != 'debug':
         junk = len(k + v)
         if junk > _maxlen:
            _maxlen = junk
   if _quit:
      show_keyval()
   _check_required()

def keya(key,exist=None,option=None):
   """return keyword value as a string and will give an error message if they
      keyword does not exist.
      
      exist  = Assume keyword references a filename, check for existance or not
      option = str/list/tuple of allowed values
      
      If keyword value is blank, return empty string."""

   if _mkeyval.has_key(key):
      tmp = _mkeyval[key]
      if exist is True: # filename must exist
         _check_existance(tmp)
      elif exist is False: # filename must NOT exist
         _check_nonexistance(tmp)
      else: # exist is None
         pass
      if option is not None:
         _check_option(key,tmp,option)
      return tmp
   else:
      raise KeyError('Invalid keyword "%s"!' %key)

def keyb(key):
   """Return keyword value as a boolean True/False.

      Can understand True,False,1,0,yes, and no as all valid.  Any
      capitalization accepted.  A blank keyword value returns False"""

   temp = keya(key)
   if temp.lower() in ('1','yes','true','y'):
      return True
   elif temp.lower() in ('0','no','false','n',''):
      return False
   else:
      raise ValueError("%s is not a boolean value!" %temp)

def keyf(key,min=None,max=None,option=None):
   """return keyword value as a float

      min    = check for minimum value 
      max    = check for maximum value
      option = list/tuple of allowed values
      if keyword value is blank, returns None"""
   try:
      x = keya(key)
      if x == '':
         return None
      else:
         tmp = float(x)
         if min is not None or max is not None:
            _check_minmax(key,tmp,min,max)
         if option is not None:
            _check_option(key,tmp,option)
         return tmp
   except ValueError:
      print "%s is not a valid float for keyword %s!" %(keya(key),key)
      raise

def keyi(key,min=None,max=None,option=None):
   """return keyword value as integer

      min    = check for minimum value 
      max    = check for maximum value
      option = list/tuple of allowed values
      if keyword value is blank, returns None"""

   try:
      x = keya(key)
      if x == '':
         return None
      else:
         tmp = int(x)
         if min is not None or max is not None:
            _check_minmax(key,tmp,min,max)
         if option is not None:
            _check_option(key,tmp,option)
         return tmp
   except ValueError:
      print "%s is not a valid integer for keyword %s!" %(keya(key),key)
      raise

def keyl(key,type=str,comment='#',min=None,max=None,option=None,length=None,
         exist=None):
   """return keyword value as a list.

      type    : Can be either str, int, or float (for string, integer, or
                float)
      comment : String character for comment lines to ignore in an @file
      length  : int/list/tuple of allowed number of elements in list
      exist   : Can check to make sure all all input files exist.  Default is
                to not check.  Note, if you give an @file, then the @file
                will always be checked for existance no matter what.
      min    = check for minimum value (for each element)
      max    = check for maximum value (for each element)
      option = list/tuple of allowed values (for each element)
      
      if keyword is blank, return an empty list."""

   outlist = []
   mykey = keya(key)
   if mykey == '':
      outlist = []
   else:
      tempkey = mykey.split(';') # split by semicolon for nested lists
      for alist in tempkey:
         blah = []
         junklist = alist.split(',')
         for junk in junklist:
            if junk[0] == '@':
               temp = _at_file(junk[1:],comment)
            else:
               temp = glob.glob(junk)
               if len(temp) == 0: # try to expand ~
                  temp = os.path.expanduser(junk)
                  if temp == junk:
                     temp = ''
                     #error('No files matched for %s' %junk)
            if len(temp) == 0: # didn't match a file, so add exact input
               blah.append(junk)
            else: # read from _at_file or glob
               blah = blah + temp
         blah = _convert_values(mykey,blah,type,exist,min,max)
         if option is not None:
            for value in blah:
               _check_option(key,value,option)
         outlist.append(blah)
      if len(outlist) == 1: # only one nested list, so removing nesting
         outlist = outlist[0]
      if length is not None:
         nval = len(outlist)
         if isinstance(length,int):
            if nval != length:
               if nval == 1:
                  raise IndexError("key %s should have 1 element!" %(key))
               else:
                  raise IndexError("key %s should have %d elements!" %(key,length))
         elif isinstance(length,list) or isinstance(length,tuple):
            if nval not in length:
               raise IndexError("key %s should have %s elements!" %(key,str(length)))
         else:
            raise IndexError("length parameter for key %s should be int/list/tuple!" %key)
   return outlist

def show_keyval(quit=True):
   """Print out the current keywords, their values and a help message, if
      one is present."""

   if _help.has_key('_msg_'):
      print _help['_msg_']
   key1 = [] # keys with missing required arguments
   key2 = [] # keys with optional/default arguments
   for k,v in _mkeyval.iteritems():
      if v == '???':
         key1.append(k)
      elif k != 'debug':
         key2.append(k)
   key1.sort()
   key2.sort()
   print "------------------------------------------------------------"
   for k in key1: # loop over required keywords
      junk = 2 + _maxlen - len(k) - len(_mkeyval[k])
      space = ' '*junk
      print "%s=%s%s%s" %(k,_mkeyval[k],space,_help[k])
   for k in key2: # loop over remaining keywords
      junk = 2 + _maxlen - len(k) - len(_mkeyval[k])
      space = ' '*junk
      print "%s=%s%s%s" %(k,_mkeyval[k],space,_help[k])
   print "------------------------------------------------------------"
   if quit:
      sys.exit()

def writekeys(filename, format=False):
   """Write out keyval as a string of keyword=value into a filename.
      filename can be a string, or the actual file pointer
      format - If set to True, make sure no more than 80 characters are
               written per line"""
      
   strFlag = False
   if isinstance(filename,str):
      fp = open(filename,'a')
      strFlag = True
   else:
      fp = filename
   try:
      keys = _mkeyval.keys()
      keys.sort()
      fp.write('# %s\n' %time.asctime())
      fp.write('#%s ' %_name)
      n = len(_name) + 2
      for k in keys:
         tmp = '%s=%s ' %(k,_mkeyval[k])
         if k != 'debug':
            n += len(tmp)
            if format is True and n > 80:
               fp.write("\n")
               fp.write("# ")
               n = len(tmp) + 2
            fp.write(tmp)
      fp.write('\n')
      if strFlag is True:
         fp.close()
   except:
      raise IOError("Cannot write to output file '%s'!" %filename)

def _at_file(filename,comment):
   """Tries to read an at-file, a file that contains keyword values.
      Specified by key=@filename.  It converts the file to a
      string of comma separated values.  Blank lines are skipped.

      filename - string name of file.  Assumes @ has been stripped off
      comment  - character to use on lines that should be ignored as comments"""

   _check_existance(filename)
   fp = open(filename,'r')
   tmp  = [line.partition(comment)[0].strip() for line in fp]
   data = [a for a in tmp if len(a) > 0]
   fp.close()
   return data

def _check_existance(*files):
   """Given an input file name as a string or a list of filenames will check to
      make sure each file exists.  If not, a fatal error will occur using
      error()
      
      If filename is a dash or a period, does not check for existance.  This
      is because I allow dashes to be sys.stdin/sys.stdout, and period to 
      be /dev/null"""

   if len(files) == 0:
      raise IndexError('You must pass at least one argument to check_existance()!')
   for f in files:
      if isinstance(f,str): # check a single filename
         if f in ('.','-'): # give these a pass as described in docstring
            pass
         elif not os.path.exists(f):
            t = os.path.split(f)[1]
            raise IOError('Required file %s is missing!' %f)
      elif isinstance(f,(list,tuple)): # a list or tuple
         for a in f:
            if f in ('.','-'): # give these a pass as described in docstring
               pass
            elif not os.path.exists(a):
               t = os.path.split(a)[1]
               raise IOError('Required file %s is missing!' %t)
      else:
         raise TypeError('check_existance() can only check types str,list, and tuple!')

def _check_nonexistance(*files):
   """Given an input file list, will check to make sure each files does NOT
      exist.  If any one of the files exists, a fatal error will occur
      using error()

      If filename is a dash or a period, does not check for existance.  This
      is because I allow dashes to be sys.stdin/sys.stdout, and period to 
      be /dev/null"""

   if len(files) == 0:
      raise IndexError('You must pass at least one argument to check_existance()!')
   for f in files:
      if isinstance(f,str): # check a single filename
         if f in ('.','-'): # give these a pass as described in docstring
            pass
         elif os.path.exists(f):
            t = os.path.split(f)[1]
            raise IOError('File %s already exists!' %f)
      elif isinstance(f,(list,tuple)): # a list
         for a in f:
            if f in ('.','-'): # give these a pass as described in docstring
               pass
            elif os.path.exists(a):
               t = os.path.split(a)[1]
               raise IOError('File %s already exists!' %t)
      else:
         raise TypeError('check_nonexistance() can only check types str,list, and tuple!')

def _check_minmax(key,value,min,max):
   """Check to see if value is within bounds set by min and max"""
   
   if min is not None:
      if value < min:
         raise ValueError("%s is < minimum value of %f!" %(key,min))
   if max is not None:
      if tmp > max:
         raise ValueError("%s is > maximum value of %f!" %(key,max))

def _check_option(key,value,option):
   """Check whether a value is among valid options"""
   
   if value in option:
      pass
   else:
      raise IndexError("Allowed options for key %s are %s!" %(key,str(option)))

def _check_required():
   """Checks to see that required arguments (default values of ???) have
   been given new values"""

   usage="Usage: %s " %_name
   n = len(_mkeyval.keys()) - 1 # subtract 1 so we don't count debug keyword
   missing = 0

   if '???' in _mkeyval.values():
      print "### Fatal Error! Insufficient parameters.  Try --help or -h."
      for i in _mkeyval.keys():
         if _mkeyval[i] == '???':
            usage = usage + "%s=??? " %i
            missing = missing + 1
      if n > missing:
         usage = usage + "..."
      print usage
      sys.exit()

def _convert_values(mykey,outlist,val,exist,min,max):
   """Helper function for keyl() to convert values in list to ascii,
      integer, or float"""
   itemlist = []
   if val is int:
      for s in outlist:
         try:
            temp = map(int,s.split('-'))
         except ValueError:
            print "%s is not a valid range of integers!" %s
            raise
         start = temp[0]
         stop  = temp[-1]
         if start > stop:
            raise ValueError("range minimum (%d) > maximum (%d)!" %(start,stop))
         itemlist = itemlist + range(start,stop+1)
   elif val is float:
      try:
         itemlist = map(float,outlist)
      except ValueError:
         print "%s is not a valid list of floats!" %mykey
         raise
   elif val is str:
      itemlist = outlist
      if exist is True: # make sure files exist in the list
         _check_existance(outlist)
      elif exist is False: # make sure files don't exist in the list
         _check_nonexistance(outlist)
      else: # exist is None
         pass
   else:
      raise TypeError("value for kel() must be str,int, or float")
   if min is not None or max is not None:
      if value in itemlist:
         _check_minmax(mykey,value,min,max)
   return itemlist

def _error(text):
   """Print a string of text as a fatal error and quit"""
   sys.stderr.write("DeprecationWarning: Rewrite your code to not use miriad._error()\n")
   sys.stderr.write("### Fatal Error! %s\n" %text)
   sys.exit()

def _warning(text):
   """Print a string of text as a warning"""
   sys.stderr.write("DeprecationWarning: Rewrite your code to not use miriad._warning()\n")
   sys.stderr.write("### Warning! %s\n" %text)

#   If executed... probably they are in an interactive python shell
if __name__ == '__main__':
   print """This program provides commandline argument reading
   for the various python programs.  It is not intended to be
   used as a standalone program."""
