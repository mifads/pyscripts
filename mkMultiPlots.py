#!/usr/bin/env python3
# https://www.codeconvert.ai/perl-to-python-converter
import os
import glob
import sys
from optparse import OptionParser

usage = """

    Step 1 )
    mkp.multiplots {-f FMT}  pattern

    e.g. mkp.multiplots  "*.ps"  - gets all .ps files
     (can also use .jpg, .png, etc..)
    mkp.multiplots  "*IT*.*ps"  - gets all .ps or .eps file with IT string

    Step 2 )

    pdflatex plots.tex - will create plots.pdf

   Step (1) creates a latex "master" file plots.tex and an include file, PLOTS.inc -
    the latter has all the file names from the command line. Step (2) just creates
    the pdf from these latex files. If using postscript files, use latex plots.tex
    and not pdflatex.

    options;:
        -c Caption text
        -C Caption from file-names

        -f FMT where FMT can be just the bounding box, e.g.

          -f "50,60,500,200"

         which gives: bbllx=50,bblly=60,bburx=500,bbury=200

           or can include angle and (optional) width, e.g.

          -f "50,60,500,200,0,8"

        which gives bbllx=50,bblly=60,bburx=500,bbury=200,angle=0,width=8cm

        -s adds subfloat and captions

        -S adds filename as subcaption

        -t FMT where FMT gives trim params  can be just the bounding box, e.g.

          -t "0,7,0,6"
          gives: trim={0 7cm 0 6cm},clip

       -x NX
      -y NY

          where NX, NY give the number of plots in x and y directions

       -w Width, e.g. -w 12   gives 12cm

Creates Latex PLOTS.inc file for all files matching pattern in the
a  directory.  A basic latex file plots.tex is also created to allow
quick testing of PLOTS.inc. Just do "latex plots.tex"!
"""

parser = OptionParser(usage=usage)
parser.add_option("-c", dest="caption", type="string",default=None, help="caption text")
parser.add_option( "-C", dest="opt_C", action="store_true", default=False, help="caption from file names")
parser.add_option( "-s", dest="opt_s", action="store_true", default=False, help="adds subfloat and captions")
parser.add_option( "-S", dest="opt_S", action="store_true", default=False, help="adds filename as subfloat caption")
parser.add_option("-f", dest="opt_f", type="string")
parser.add_option("-t", dest="opt_t", type="string")
parser.add_option( "--th", dest="opt_th", action='store', nargs=1, help="give trim params and height, in cm, e.g. 0,0,2,0,4")
parser.add_option("-x", dest="opt_x", type="int", help="NX")
parser.add_option("-y", dest="opt_y", type="int", help="NY")
parser.add_option( "-w", dest="opt_w", type="int", help="-w 12 gives 12cm width")
parser.add_option( "-i", dest="opt_i", nargs=1, help="pattern")
parser.add_option( "-L", dest="legend", type="string", default=None, help="legend file")

(options, args) = parser.parse_args()

argnum = len(args)  # Check that a pattern was given

print(f"OPTIONS {options}")
print(f"ARGS    {args}")
print(f"IFILES {options.opt_i}")

patterns = options.opt_i.split()  #  args[0]
print(f"PATTERN is {patterns}")

plotfiles = []
for n, pattern in enumerate( patterns):
    plotfiles += sorted(glob.glob(pattern))
    print(f"PATTERN: {n} {pattern}")
    if n==1: print(f"GLOB: {sorted(glob.glob(pattern))}")

print(("FILES", plotfiles))

NXPLOT = 2  # Plots per page
NYPLOT = 3  # Plots per page
if options.opt_x: NXPLOT = options.opt_x
if options.opt_y: NYPLOT = options.opt_y
MAXNPLOT = NXPLOT * NYPLOT
print( f"XY is X{options.opt_x} Y{options.opt_y} NNS {NXPLOT} {NYPLOT} MAXNPLOT {MAXNPLOT}")

hdir = "."
assert os.path.isdir(hdir), f"HDIR ERROR{hdir}"

with open("plots.tex", "w") as ltx:
    ltx.write(
        r"""\documentclass[12pt]{article}
\usepackage[]{graphicx}
\usepackage[]{grffile} % Allows more flexible names, e.g. abc.def.png
\usepackage{lscape}
% Hints from http://tex.stackexchange.com/questions/57418/crop-an-inserted-image
% e.g. trim={0 0 3cm 0},clip,height=3cm   (left, bottom, right, top)
\usepackage[export]{adjustbox}
% Hints from https://www.baeldung.com/cs/latex-subfigures
\usepackage{subfig}  % easier than subcaption 
\pagestyle{empty}

\begin{document}
%\begin{landscape}

\input{PLOTS.inc}

%\end{landscape}
\end{document}
"""
    )

emep_pl = 0  # Set to one for emep.pl generated plots.
figfmt = r"\includegraphics*[width=8cm]"

if options.opt_f:
    parts = options.opt_f.split(',')
    llx, lly, urx, ury = parts[0], parts[1], parts[2], parts[3]
    rest = parts[4:]
    angle = -90
    if len(rest) > 0 and rest[0]:
        angle = rest[0]
    width = rest[1] if len(rest) > 1 and rest[1] else 6
    figfmt = f"\\includegraphics*[bbllx={llx},bblly={lly},bburx={urx},bbury={ury},angle={angle},width={width}cm]"

if options.opt_t:
    left, bot, right, top = options.opt_t.split(',')
    angle = -90
    figfmt = f"\\includegraphics*[width=16cm,trim={{{left}cm {bot}cm {right}cm {top}cm}},clip]"

if options.opt_th:
    left, bot, right, top, height = options.opt_th.split(',')
    figfmt = f"\\includegraphics*[trim={{{left}cm {bot}cm {right}cm {top}cm}},clip,height={height}cm]"

if options.opt_w:
    figfmt = f"\\includegraphics*[width={options.opt_w}cm]"

label = [ "(a)", "(b)", "(c)", "(d)", "(e)", "(f)",
          "(g)", "(h)", "(i)", "(j)", "(k)", "(l)", "(m)", "(n)" ]
site = None
caption = "Delta AOT40f"  # start of caption
fullcaption = ""
if options.caption is not None: fullcaption = options.caption
if options.opt_C: fullcaption = "File(s): "
print(f"CAPTION {fullcaption}  OPTS:{options.caption}")

nplots = len(plotfiles)
with open("PLOTS.inc", "w") as out:
    nplot_in_page = 0
    npage = 0
    for nplot, p in enumerate(plotfiles):
        #print(f"PLOTFILE {p}")
        lastplot = ( nplot == nplots-1 )
        lastplot_in_page = ( lastplot or nplot_in_page == (MAXNPLOT-1) )
        dir_part = os.path.dirname(p)
        p_basename = os.path.basename(p)
        dir_part = dir_part if dir_part else "."
        print(f"PP {p_basename} DIR {dir_part}")
        if nplot_in_page == 0:
            if options.opt_C: fullcaption = "File(s): "
            out.write("\\begin{figure}\n\\centering\n")
        if nplot_in_page < MAXNPLOT:
            eol = ""
            if (nplot_in_page % NXPLOT) < (NXPLOT - 1): eol = "%"
            figtxt = f"{figfmt}{{{dir_part}/{p_basename}}}"

            if options.opt_s: # Adds subfloats
                figtxt = ( f"\\subfloat[xxx]{{{figtxt}\\label{{fig:fig{nplot_in_page}}}}}")
            if options.opt_S: # Adds filenames as subcaptions
                tmpname = p_basename.replace('.png','')
                tmpname = tmpname.replace('_','\_')
                figtxt = ( f"\\subfloat[{tmpname}]{{{figtxt}\\label{{fig:fig{nplot_in_page}}}}}")

            if ( lastplot_in_page and options.legend is not None ):  # Tmp, assume just height for now:
                legfmt = f"\\includegraphics*[height={height}cm]"
                eol = f"%\n{legfmt}" + "{" + options.legend + "}"

            print('OUT ', nplot_in_page, npage, nplot, nplots,
               lastplot_in_page,lastplot, MAXNPLOT, f"EOL:{eol}XX", p_basename)
            out.write(f"{figtxt}{eol}\n")
            if (nplot_in_page % NXPLOT) == (NXPLOT - 1):
                out.write("\\\\\n")
            comma = ";"
            if nplot_in_page == MAXNPLOT - 1 or lastplot_in_page:
                comma = ""
            if options.opt_C:
                f_escaped = p_basename.replace("_", r"\_")
                fullcaption += f"{f_escaped}; "
            nplot_in_page += 1
        if lastplot or lastplot_in_page: # NEW page or legend
            if fullcaption: out.write(f"\\caption{{{fullcaption}}}\n")
            out.write("\\end{figure}\n\n\n")
            if not lastplot_in_page:
                out.write("\\clearpage\n")
            nplot_in_page = 0
            npage += 1
