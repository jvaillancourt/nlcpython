#!/usr/bin/env python

from readcmd import ReadCmd
import sys

spec = """# Quick and Dirty pywip plotting
          in     = ???       # Input file
          color  = k         # Color for each plot
          legend = 0.05,0.95 # Location of legend
          limits = None      # Limits given as xmin,xmax,ymin,ymax
          out    = 1.xs      # output plot
          style  = -         # Line Style/Symbol for each plot
          text   = None      # Labels for legend
          title  = None      # Title for plot
          width  = 1         # line thickness
          xcol   = 1         # X column number(s)
          dxcol  = None      # X error column number(s)
          xlabel = None      # X-axis label
          ycol   = 2         # Y column number(s)
          dycol  = None      # Y error column number(s)
          ylabel = None      # Y-axis label"""

def error(text):
   """Write out error message and quit"""
   sys.stderr.write("### Fatal Error! %s\n" %text)
   sys.exit()

arg = ReadCmd(spec)
infile   = arg.getstr('in',exist=True)
xcol     = arg.getlistint('xcol',min=1)
ycol     = arg.getlistint('ycol',min=1)
dxcol    = arg.getlistint('dxcol',min=1)
dycol    = arg.getlistint('dycol',min=1)
style    = arg.getliststr('style')
color    = arg.getliststr('color')
limits   = arg.getlistfloat('limits',length=4)
out      = arg.getstr('out')
xlab     = arg.getstr('xlabel')
ylab     = arg.getstr('ylabel')
mytext   = arg.getliststr('text')
mytitle  = arg.getstr('title')
mywidth  = arg.getliststr('width')
legloc   = arg.getlistfloat('legend',length=2)

nx       = len(xcol)
ny       = len(ycol)
ndx      = len(dxcol)
ndy      = len(dycol)
nstyle   = len(style)
ncolor   = len(color)
ntext    = len(mytext)
nwidth   = len(mywidth)
n        = max([nx,ny,ndx,ndy,nstyle,ncolor,ntext,nwidth])

if nx == 1:
   xcol = xcol*n
elif nx != n:
   error('Number of xcol must be 1 or %d' %n)

if ny == 1:
   ycol = ycol*n
elif ny != n:
   error('Number of ycol must be 1 or %d' %n)

if ndx == 0:
   pass
elif ndx == 1:
   dxcol = dxcol*n
elif ndx != n:
   error('Number of dxcol must be 0, 1 or %d' %n)

if ndy == 0:
   pass
elif ndy == 1:
   dycol = dycol*n
elif ndy != n:
   error('Number of dycol must be 0, 1 or %d' %n)

if nstyle == 1:
   style = style*n
elif nstyle != n:
   error('Number of styles must be 1 or %d' %n)

if ncolor == 1:
   color = color*n
elif ncolor != n:
   error('Number of colors must be 1 or %d' %n)

if ntext == 0:
   mytext = [None]*n
elif ntext == 1:
   mytext = mytext*n
elif ntext != n:
   error('Number of texts must be 0, 1 or %d' %n)

if nwidth == 1:
   mywidth = mywidth*n
elif nwidth != n:
   error('Number of widths must be 1 or %d' %n)

# Put None for 'None' and the like in text labels
for i in range(ntext):
   if mytext[i].lower() == 'none':
      mytext[i] = None

from pywip import *

winadj()
for i in range(n):
   if len(limits) != 0:
      plot(xcol[i],ycol[i],infile,style=style[i],color=color[i],
           limits=limits,text=mytext[i],width=mywidth[i])
   else:
      plot(xcol[i],ycol[i],infile,style=style[i],color=color[i],
           text=mytext[i],width=mywidth[i])
   if ndx != 0 and ndy != 0:
      errorbar(xcol[i],ycol[i],infile,color=color[i],width=mywidth[i],
         xerr=dxcol[i],yerr=dycol[i])
   elif ndx != 0:
      errorbar(xcol[i],ycol[i],infile,color=color[i],width=mywidth[i],
         xerr=dxcol[i])
   elif ndy != 0:
      errorbar(xcol[i],ycol[i],infile,color=color[i],width=mywidth[i],
         yerr=dycol[i])
   else: # no errorbar specified
      pass

axis()
if xlab is not None:
   xlabel(xlab)
if ylab is not None:
   ylabel(ylab)
if mytitle is not None:
   title(mytitle)
if ntext != 0:
   legend(legloc[0],legloc[1])
savefig(out)
