import qrcode
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

from pydmtx import DataMatrix
import dm

DM = dm.DM(10, 500)

pdf = ""

#Cards are 2.5" x 3.45"
margin = 0.25
cwidth = 2.5
cheight = 3.45

imgfile = "temp.png" # Temporary image file name.

pretext = ""
cnstart = 0
cnend = 8
posttext = ""
outputfile = ""

def displayHelp():
    print "Usage:"
    print "\tpython "+sys.argv[0]+" [OPTIONS] OUTPUTFILE.pdf"
    print "Example:"
    print "\tpython "+sys.argv[0]+" deck.pdf"
    print "OPTIONS:"
    print "\t--pre \"TEXT\"\t\ttext to add before the card number"
    print "\t--start [#]\t\tstarting card number (default: 00)"
    print "\t--end [#]\t\tending card number (default: 08)"
    print "\t--post \"TEXT\"\t\ttext to add after the card number"
    print ""


def drawTemplateLines():
    # 3x3 cards
    global inch, pdf
    pdf.setLineWidth(0.5)
    pdf.setDash([1,1], 0)
    pdf.setStrokeColorRGB(0.85,0.85,0.85)

    #Rows
    x1 = 0; y1 = margin*inch
    x2 = 8.5*inch; y2 = margin*inch
    pdf.line(x1,y1, x2,y2) #bottom edge
    y1 += cheight*inch
    y2 += cheight*inch
    pdf.line(x1,y1, x2,y2) #row border
    y1 += cheight*inch
    y2 += cheight*inch
    pdf.line(x1,y1, x2,y2) #row border
    y1 += cheight*inch
    y2 += cheight*inch
    pdf.line(x1,y1, x2,y2) #row border
    #Columns
    x1 = margin*inch; y1 = 0
    x2 = margin*inch; y2 = 11*inch
    pdf.line(x1,y1, x2,y2) #left edge
    x1 += cwidth*inch
    x2 += cwidth*inch
    pdf.line(x1,y1, x2,y2) #column border
    x1 += cwidth*inch
    x2 += cwidth*inch
    pdf.line(x1,y1, x2,y2) #column border
    x1 += cwidth*inch
    x2 += cwidth*inch
    pdf.line(x1,y1, x2,y2) #column border
    return


def drawCard(pos, text):
    x = pos[0]
    y = pos[1]
    pdf.drawInlineImage(imgfile, x-(0.23*inch), y+((cheight-cwidth)*inch)-(0.28*inch), width=3*inch, height=3*inch)
    pdf.setFillColorRGB(0.85,0.85,0.85)
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(x+(0.5*cwidth*inch),y+(0.0625*inch), text)
    return

#----------------------------
# Main Program Begins
#----------------------------

# Parse options and parameters.
for index, arg in enumerate(sys.argv):
    if arg == "--help":
        displayHelp()
        quit()

    elif arg == "--pre":
        pretext = sys.argv[index+1]

    elif arg == "--start":
        cnstart = int(sys.argv[index+1])

    elif arg == "--end":
        cnend = int(sys.argv[index+1])

    elif arg == "--post":
        posttest = sys.argv[index+1]

    elif os.path.splitext(arg)[1] == ".pdf":
        outputfile = arg

# Validate options and parameters or display help.
error = False
if outputfile == "":
    error = True

if error:
    displayHelp()
    quit()

pdf = canvas.Canvas(outputfile, pagesize=letter)

pagepos = 0
cardcount = 0

for cn in range(cnstart, cnend+1):
    dmtext = ""
    dmtext += pretext
    dmtext +=  str(cn).zfill(2)
    dmtext += posttext

    DM.write(dmtext, imgfile)

    # There seems to be a bug in reportlab.
    # Strings are drawn in the A4 template even though we've set the pagesize to letter.
    # Do text positioning based on A4.
    if pagepos == 0:
        pos = margin*inch, margin*inch
    elif pagepos == 1:
        pos = (margin+cwidth)*inch, margin*inch
    elif pagepos == 2:
        pos = (margin+cwidth*2)*inch, margin*inch
    elif pagepos == 3:
        pos = margin*inch, (margin+cheight)*inch
    elif pagepos == 4:
        pos = (margin+cwidth)*inch, (margin+cheight)*inch
    elif pagepos == 5:
        pos = (margin+cwidth*2)*inch, (margin+cheight)*inch
    elif pagepos == 6:
        pos = margin*inch, (margin+(2*cheight))*inch
    elif pagepos == 7:
        pos = (margin+cwidth)*inch, (margin+(2*cheight))*inch
    elif pagepos == 8:
        pos = (margin+cwidth*2)*inch, (margin+(2*cheight))*inch


    drawCard(pos, dmtext)

    if pagepos >= 8:
        drawTemplateLines()
        pdf.save()
        pagepos = -1

    pagepos += 1
    cardcount += 1



if pagepos != 0:
    drawTemplateLines()
    pdf.save()

#os.remove(imgfile)

print
print str(cardcount)+" cards created in "+outputfile
print

