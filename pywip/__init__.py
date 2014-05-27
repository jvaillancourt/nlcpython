#!/usr/bin/env python
r'''Library functions for running WIP within python
Started 12 April 2007 - NLC
First used for a real plot on 19 April 2007
version 2.0 - 21 April 2009 - Lots of backend changes, switched to variable
   arguments in all function calls, made the uber-awesome legend command,
   and made the axis command user-friendly.  It is NOT backwards-compatible
   with the older version1, but it is easy to update your scripts.  Only a
   few of the commands have changed argument calls: axis, curve, legend, panel,
   wedge, and winadj.
version 3.0 
   split functions into separate files and made a pywip a proper package
   arc() can now specify fill color
   rudimentary compass() command
   stick() command has been subsumed into vector()
   officially added some random tools to the bin directory.

last updated: 9 July 2013 - NLC

            Colors                                Palettes
===============================     ===================================
|    key    | Description     |     |   key   |      Description      |
-------------------------------     -----------------------------------
|     w     | white           |     |  gray   | grayscale             |
|     k     | black (default) |     | rainbow | Rainbow scale         |
|     r     | red             |     |  heat   | Heat scale            |
|     g     | green           |     |  iraf   | IRAF scale            |
|     b     | blue            |     |  aips   | AIPS scale            |
|     c     | cyan            |     | pgplot  | PGPLOT scale          |
|     m     | magenta         |     |    a    | SAOimage A scale      |
|     y     | yellow          |     |   bb    | SAOimage BB scale     |
|     o     | orange          |     |   he    | SAOimage HE scale     |
|    gy     | green-yellow    |     |   i8    | SAOimage I8 scale     |
|    gc     | green-cyan      |     |   ds    | DS scale              |
|    bc     | blue-cyan       |     | cyclic  | Cyclic scale          |
|    bm     | blue-magenta    |     | filename| rgb lookup from a file|
|           | (i.e. purple)   |     -----------------------------------
|    rm     | red-magenta     |     * can prepend palette keywords with
|    dg     | dark gray       |       a minus sign to reverse the scale
|    lg     | light gray      |     
| gray1-100 | shades of gray  |
|   r,g,b   | rgb color as    |
|           | fractions from  |
|           | 0-1             |
-------------------------------

    Fill Styles                     Fonts
=======================   =========================
| key |  Description  |   | key |   Description   |
-----------------------   -------------------------
|  s  | solid         |   |  sf | sans-serif      |
|  h  | hollow        |   |  rm | roman (default) |
|  /  | hatched       |   |  it | italics         |
|  #  | cross-hatched |   |  cu | cursive         |
-----------------------   -------------------------

             Symbols                               Line Styles
=================================        ===========================
|  key  |       Description     |        | key  |    Description   |
---------------------------------        ---------------------------
|   s   | square                |        |   -  | solid (default)  |
|   .   | dot                   |        |  --  | dashed           |
|   +   | plus sign             |        |  .-  | dot-dashed       |
|   *   | asterisks             |        |   :  | dotted           |
|   o   | circle (default)      |        | -... | dash-dot-dot-dot |
|   x   | an x                  |        ---------------------------
|   ^   | triangle              |
| oplus | circle with plus sign |
| odot  | circle with a dot     |
|  ps   | pointed square        |
|   d   | diamond               |
|  st   | five-point star       |
|  o+   | open plus symbol      |
| david | star of david         |
| arrow | an arrow              |
---------------------------------
* Only the square, circle, triangle, and five-point star can be filled.

LaTeX is supported in text strings by default.  Note that unlike math mode in
LaTeX, the text is NOT italicized by  default.  LaTeX symbols supported: all
greek symbols, \times, \AA (for angstroms), \odot (for sun symbol),
\oplus (for earth symbol), \pm (for proper +-), \geq (for greater than or
equal to), \leq (for less than or equal to), \propto (for proportionality), 
^{} (for superscripts), \circ (for degrees symbol), _{} (for subscripts), 
\sf{} (for sans-serif font), \rm{} (for roman font), \it{} (for italics), 
\cu{} (for cursive)'''

__all__ = ['arc','arrow','axis','bar','beam','bin','blowup','compass','connect',
           'contour','curve','default','errorbar','halftone','inputwip',
           'legend','panel','plot','poly','rect','savefig','text',
           'title','tools','vector','viewport','winadj','wedge','xlabel','ylabel']

import header as _hd
_palettes = _hd._palettes
_colors   = _hd._colors
_fills    = _hd._fills
_fonts    = _hd._fonts
_lstyles  = _hd._lstyles
_symbols  = _hd._symbols

from arc import arc
from arrow import arrow
from axis import axis
from bar import bar
from beam import beam
from bin import bin
from blowup import blowup
from compass import compass
from connect import connect
from contour import contour
from curve import curve
from default import default
from errorbar import errorbar
from halftone import halftone
from inputwip import inputwip
from legend import legend
from panel import panel
from plot import plot
from poly import poly
from rect import rect
from savefig import savefig
from text import text
from title import title
import tools
from vector import vector
from viewport import viewport
from winadj import winadj
from wedge import wedge
from xlabel import xlabel
from ylabel import ylabel
