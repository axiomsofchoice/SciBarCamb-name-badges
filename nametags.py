"""
Reads a CSV list of attendees, as provided by Eventbrite and generates nametags.

Uses the following library
http://www.reportlab.com/apis/reportlab/dev/

Takes arguments:

    attendees      - the csv file from Eventbrite containing the list of
                     attendees
    qrcodes        - the directory containing pre-generated QRcodes
    output         - the directory into which the PDF file will go
    logos          - the directory into which contains the SciBarCamb logos

The compiled name tags will be rendered four-up onto an A4 page, output as a PDF
"""

import csv
import itertools
import re, sys, os
import getopt
import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
import StringIO

def drawNameTag(c, SciBarCamb_logo, qrcodes, tickettypes, a):
    """Draws a single nametag, relative to the current coordinate transformation
    leaving blanks where appropriate.
    """
    if "First Name" in a and "Last Name" in a:
        print "Processing: %s %s" % (a["First Name"], a["Last Name"])
    else:
        print "Processing a blank attendee"
    
    # A surrounding box to help with cutting it out
    c.rect(1.5*cm, 2.0*cm, 8.0*cm, 11.0*cm, stroke=1, fill=0)
    # The SciBarCamb logo
    c.saveState()
    c.translate(1.75*cm, 11.0*cm)
    c.scale(0.12,0.12)
    c.drawImage(SciBarCamb_logo, 0.0*cm, 0.0*cm)
    c.restoreState()
    # A box around the composite image for registering it 
    c.saveState()
    c.setFillColor(black)
    c.rect(1.6*cm, 2.125*cm, 7.825*cm, 4.0*cm, stroke=1, fill=1)
    c.restoreState()
    c.saveState()
    c.translate(1.75*cm, 2.25*cm)
    c.scale(0.425,0.425)
    tickettypeImage = tickettypes[a["Ticket Type"]]["image"]
    c.drawImage(tickettypeImage, 0.0*cm, 0.0*cm)
    c.restoreState()
    # Affiliation details
    c.setFont("Courier-BoldOblique", 14)
    if "First Name" in a and "Last Name" in a:
        c.drawCentredString(5.5*cm, 10.0*cm, '%s %s' % (a["First Name"], a["Last Name"]))
    c.setFont("Courier-BoldOblique", 9)
    if "Job Title" in a:
        c.drawString(1.75*cm, 8.75*cm, a["Job Title"][:25])
        c.drawString(1.75*cm, 8.5*cm, a["Job Title"][25:50])
    if "Company" in a:
        c.drawString(1.75*cm, 7.75*cm, a["Company"][:25])
        c.drawString(1.75*cm, 7.5*cm, a["Company"][25:50])
    if "Twitter" in a:
        validtwitterhandleregex = re.compile( "^(?P<handleprefix>@)?(?P<handle>.+)" )
        teststr = a["Twitter"]
        if validtwitterhandleregex.match(teststr) is not None:
            if validtwitterhandleregex.match(teststr).group('handleprefix') is None:
                c.drawString(1.75*cm, 6.75*cm, "@%s" % teststr)
            else:
                c.drawString(1.75*cm, 6.75*cm, teststr)
    # The QRcode
    c.saveState()
    c.translate(6.5*cm, 6.5*cm)
    c.scale(0.15,0.15)
    if os.path.exists("%s.PNG" % (os.path.join(qrcodes, a["Attendee #"]))):
        qrcodeImage = ImageReader("%s.PNG" % (os.path.join(qrcodes, a["Attendee #"])))
        c.drawImage(qrcodeImage, 0.0*cm, 0.0*cm)
    c.restoreState()
    c.setFont("Courier-BoldOblique", 5)

def drawPageOfNameTags(c, SciBarCamb_logo, qrcodes, tickettypes, attendees):
    """Draw four name tags on a page"""
    
    # All translations will be cumulative relative to the standard coordinate system
    drawNameTag(c, SciBarCamb_logo, qrcodes, tickettypes, attendees[0])
    c.translate(10.0*cm, 0.0)
    if len(attendees) > 1:
        drawNameTag(c, SciBarCamb_logo, qrcodes, tickettypes, attendees[1])
        c.translate(0.0, 15.0*cm)
        if len(attendees) > 2:
            drawNameTag(c, SciBarCamb_logo, qrcodes, tickettypes, attendees[2])
            if len(attendees) > 3:
                c.translate(-10.0*cm, 0.0)
                drawNameTag(c, SciBarCamb_logo, qrcodes, tickettypes, attendees[3])
                if len(attendees) > 4:
                    raise Exception("more attendees than expected")
    
    # Complete the page, ready to move on to the next one
    c.showPage()

def processAttendees(attendeeReader,logos,qrcodes,outdir):
    """Takes the list of attendees and groups into fours for compilation into a
    PDF.
    """
    # The PDF file we will output
    c = canvas.Canvas(os.path.join(outdir,"SciBarCamb-nametags.pdf"))
    
    # Generate the 100 images, based on attendee number.
    # These are the ticket type logos, and the places where they were obtained
    ttdir = "tickettypes"
    tickettypes = { "Electron": { "image": ImageReader(os.path.join(ttdir,"500px-Electric_field_point_lines_equipotentials.svg.png")),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Electric_field_point_lines_equipotentials.svg/500px-Electric_field_point_lines_equipotentials.svg.png" } ,
                    "Atom" : { "image": ImageReader(os.path.join(ttdir,"Stylised_Lithium_Atom.png")),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/e/e2/Stylised_Lithium_Atom.png" } ,
                    "Molecule" : { "image": ImageReader(os.path.join(ttdir,"Caffeine_molecule.png")),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/6/65/Caffeine_molecule.png" } }
                    
    # Take items in fours and compile pages
    attendeeList = list(attendeeReader)
    for i in range(0, len(attendeeList), 4):
        drawPageOfNameTags(c, ImageReader(os.path.join(logos, "SciBar_No shadow.jpg")),
                            qrcodes, tickettypes, attendeeList[i:i+4])
        
    # Complete the PDF document and save it
    c.save()

def main():
    
    # When present get options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:q:o:l:", 
                      ["attendees=", "qrcodes=", "output=", "logos="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(-1)
        
    # The directory into which we store the QRcodes (again, the default)
    outdir = "nametags"
    # The name of the CSV file from Eventbrite contain the list of attendees
    attendeelist = None
    # The directory containing pre-generated QRcodes
    qrcodes = "qrcodes"
    # The directory containing SciBarCamb logos (not animations or ticket types)
    logos = "logos"
    
    for o, a in opts:
        if o in ("-a", "--attendees"):
            attendeelist = a
        elif o in ("-q", "--qrcodes"):
            qrcodes = a
        elif o in ("-o", "--output"):
            outdir = a
        elif o in ("-l", "--logos"):
            logos = a
        else:
            assert False, "unhandled option"
            
    
    # Open the CSV file
    attendeeReader = csv.DictReader(open(attendeelist, 'rb'))
    
    # Before running the process, ensure that the output directory exists
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    processAttendees(attendeeReader,logos,qrcodes,outdir)

if __name__ == "__main__" :
    main()
