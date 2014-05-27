#!/usr/bin/env python

from Tkinter import *
from tkFileDialog import askopenfilename

import os,time

_THEME_COLOR = "moccasin"   # theme color for selection, highlights, etc.
                            # see full list in /usr/lib/X11/rgb.txt
_CHROME_COLOR= "grey95"     # color for backgrounds of objects
_HIGHLIGHT_COLOR = "blanchedalmond" # color for highlight, before widget is pressed
_BD = 1 # border distance (width) for GUI elements.  1 looks better

class genericDialog(Toplevel):
   """A generic dialog that can be inherited from and customized as needed."""
   def __init__(self, parent, title=None, b1="OK", b2="Cancel"):
      """The constructor function"""
      Toplevel.__init__(self, parent,background=_CHROME_COLOR)
      self.transient(parent)
      if title:
         self.title(title)
      self.b1 = b1 # button 1 text, default is OK
      self.b2 = b2 # button 2 text, default is Cancel
      self.parent = parent
      self.result = None
      body = Frame(self,background=_CHROME_COLOR)
      self.initial_focus = self.body(body)
      body.pack(padx=5, pady=5,fill=BOTH,expand=YES)
      self.buttonbox()
      self.grab_set()
      if not self.initial_focus:
         self.initial_focus = self
      self.protocol("WM_DELETE_WINDOW", self.cancel)
      #self.geometry("+%d+%d" % (parent.winfo_rootx(),
      #                          parent.winfo_rooty()))
      self.initial_focus.focus_set()
      self.wait_window(self)
   # construction hooks
   def body(self, master):
      """Put the contents of the dialog box in here by overriding"""
      pass
   def buttonbox(self):
      """Creates standard button box"""
      box = Frame(self,background=_CHROME_COLOR)
      w = Button(box, text=self.b1, width=10, command=self.ok, bd=_BD,
                 default=ACTIVE, highlightthickness=_BD,
                 activebackground=_HIGHLIGHT_COLOR,
                 highlightbackground=_THEME_COLOR,
                 background=_CHROME_COLOR)
      w.pack(side=LEFT, padx=5, pady=5)
      w = Button(box, text=self.b2, width=10, command=self.cancel,bd=_BD,
                 highlightthickness=_BD,activebackground=_HIGHLIGHT_COLOR,
                 background=_CHROME_COLOR)
      w.pack(side=LEFT, padx=5, pady=5)
      self.bind("<Return>", self.ok)
      self.bind("<Escape>", self.cancel)
      box.pack()
   # standard button semantics
   def ok(self, event=None):
      """Function called when button b1 (the default) is clicked. This is 
         typically 'OK'."""
      if not self.validate():
         self.initial_focus.focus_set() # put focus back
         return
      self.withdraw()
      self.update_idletasks()
      self.apply()
      self.cancel()

   def cancel(self, event=None):
      """Function called when button b2 is clicked ('cancel' by default)."""
      # put focus back to the parent window
      self.parent.focus_set()
      self.destroy()

   # command hooks
   def validate(self):
      """Secondary function called when button b1 is clicked.  This checks
         for some sort of validation condition to be met.  If it is met,
         then self.apply will be called by the ok function."""
      return 1 # override
   def apply(self):
      """Secondary function called when button b1 is clicked.

   	   The user should override this function when creating their
         own subclass.  This function will then assign variables or
         whatever is needed when the 'ok' (b1) is clicked."""
      pass # override

class inputFile(Frame):
   def __init__(self, master, lab='in:', name='???', width=15):
      Frame.__init__(self, master, background=_CHROME_COLOR)
      self.a = [("Data files","?*.dat"),("Data files","?*.tbl"),("All files","*")]
      self.dir  = StringVar()
      self.name = StringVar()
      self.master = master
      if name == '???':
         name = '%s/???' %os.getcwd()
      self.update(name)
      self.makeframe(lab,width)

   def makeframe(self,lab,width):
      """Create the GUI elements that go in the frame"""
      Label(self,text=lab,background=_CHROME_COLOR).pack(side=LEFT)
      Label(self,textvariable=self.name,width=width,bg="White").pack(side=LEFT,padx=2)
      Button(self,text="Browse",command=self.getname,bd=_BD,
         highlightthickness=0,activebackground=_HIGHLIGHT_COLOR).pack(side=LEFT)

   def getname(self,initdir=None):
      """Calls tkFileDialog to allow the user to browse for a file,
         and then assigns this name to self.name"""
      if not initdir:
         path = askopenfilename(title="Choose file to process:",filetypes=self.a,
            initialdir=self.dir.get())
      else:
         path = askopenfilename(title="Choose file to process:",filetypes=self.a,
            initialdir=initdir)
      if path:
         if self.validate():
            self.update(path)
            self.dostuff()

   def update(self,name):
      """Update the entry and internal variables"""
      junk1,junk2 = os.path.split(name)
      self.path = name
      self.dir.set(junk1)
      self.name.set(junk2)
      
   def validate(self):
      """Function called to check whether to call self.update and self.dostuff.
         This checks to make sure some sort of validation condition is met
         first before calling self.update and self.dostuff"""
         
      return 1
   def dostuff(self):
      """Hook function to do something after a file is input"""
      pass

class _setit:
    """Internal class. It wraps the command in the widget OptionMenu."""
    def __init__(self, parent,var, value, index,callback=None):
        self.__value = value
        self.__var = var
        self.__index = index
        self.__callback = callback
        self.parent = parent
    def __call__(self, *args):
        self.__var.set(self.__value)
        self.parent.index = self.__index
        if self.__callback:
            self.__callback(self.__value, *args)

class myOptionMenu(Menubutton):
    """Modified the builtin OptionMenu so it doesn't look like ass.  Also keeps
       track of the index of items on the menu and allows you to change the 
       menu on the fly."""
       
    def __init__(self, master, variable, value, *values, **kwargs):
        """Construct an optionmenu widget with the parent MASTER, with
        the resource textvariable set to VARIABLE, the initially selected
        value VALUE, the other menu values VALUES and an additional
        keyword argument command."""
        kw = {"borderwidth": 1, "textvariable": variable,
              "indicatoron": 1, "relief": RAISED, "anchor": "c",
              "highlightthickness": 1, 'direction' : 'below'}
        if kwargs.has_key('direction'):
         kw['direction'] = kwargs['direction']
        Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = Menu(self, name="menu", tearoff=0, borderwidth=_BD,
           activeborderwidth=1)
        self.menuname = menu._w
        # 'command' is the only supported keyword
        self.callback = kwargs.get('command')
        #if kwargs.has_key('command'):
        #    del kwargs['command']
        #if kwargs:
        #    raise TclError, 'unknown option -'+kwargs.keys()[0]
        self.index = -1
        self["menu"] = menu
        self.variable = variable
        self.setoptions([value]+list(values))

    def __getitem__(self, name):
        if name == 'menu':
            return self.__menu
        return Widget.__getitem__(self, name)

    def setoptions(self,options):
        """Set the options in the menu"""
        menu = self["menu"]
        menu.delete(0,END)
        for i,v in enumerate(options):
            menu.add_command(label=v,command=_setit(self,self.variable, v, i+1, self.callback))
        
    def destroy(self):
        """Destroy this widget and the associated menu."""
        Menubutton.destroy(self)
        self.__menu = None

class myaskopenfilename(genericDialog):
   """An altered askopenfilename that lets user put in file formats and not
      strings of text for extensions."""
      
   def __init__(self,master,title=None,initialdir=None,filetypes=None):
      """Constructor function"""
      if not initialdir:
         self.cwd = os.getcwd() # full path of current folder
      else:
         self.cwd = initialdir
      self.path = self.cwd.split('/')
      self.path[0] = '/'
      self.currentFolder = StringVar() # name of current folder
      self.currentFolder.set(self.path[-1])
      self.filetypes = filetypes
      self.currentType = StringVar() # name of current filetype
      self.currentType.set(self.filetypes[0])
      genericDialog.__init__(self,master,b1='Open',title=title)

   def body(self,master):
      """The body of the file browser"""
      
      f1 = Frame(master,background=_CHROME_COLOR)
      self.optionmenu = myOptionMenu(f1,self.currentFolder,command=self._changedir,
         direction='above',*self.path)
      self.optionmenu.pack(side=LEFT)
      Button(f1,text="Up",bd=_BD,highlightthickness=0,
         activebackground=_HIGHLIGHT_COLOR,command=self._goup).pack(side=LEFT)
      f1.pack()
      
      f2=Frame(master,background=_CHROME_COLOR)
      self.scrollbar = Scrollbar(f2,orient=VERTICAL,troughcolor="gray80",bd=_BD,
         activebackground=_THEME_COLOR,background=_CHROME_COLOR)
      self.listbox = Listbox(f2,width=30,height=15,bg="White",
         bd=_BD,yscrollcommand=self.scrollbar.set,selectbackground='White',
         selectborderwidth=0,background=_CHROME_COLOR)
      self.scrollbar.config(command=self.listbox.yview)
      self.scrollbar.pack(side=RIGHT,fill=Y)
      self.listbox.pack(fill=BOTH,expand=1)
      f2.pack(fill=BOTH,expand=1,anchor=N)
      
      f3 = Frame(master,background=_CHROME_COLOR)
      Label(f3,text='format:').pack(side=LEFT)
      myOptionMenu(f3,self.currentType,*self.filetypes).pack(side=LEFT)
      f3.pack()
      self._showdir()

   def apply(self):
      """Figure out full path of selected file and return it along with
         file format"""
      idx = self.listbox.curselection()
      filename = self.listbox.get(int(idx[0]))
      path = '/'.join(self.path)
      print path,filename
      return path

   def _showdir(self):
      """Fill the listbox with the files in the current directory"""

      filelist = os.listdir(self.cwd)
      self.listbox.delete(0,END)
      for line in filelist:
         if line[0] != '.':
            self.listbox.insert(END,line)

   def _changedir(self,event=None):
      """Change dir when user selects from optionmenu"""
      val = self.optionmenu.index
      self.cwd = '/' + '/'.join(self.path[1:val])
      print self.cwd
      self.path = self.path[:val]
      self.currentFolder.set(self.path[-1])
      self.optionmenu.setoptions(self.path)
      self._showdir()
      
   def _goup(self,event=None):
      """Go up 1 level"""
      if len(self.path) > 1:
         self._changedir()
