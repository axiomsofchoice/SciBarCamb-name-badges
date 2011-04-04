"""
Reads a CSV list of attendee, as provided by Eventbrite and gen

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
#import moire

def drawNameTag(c, SciBarCamb_logo, qrcodes, a, animationImage, animationCredit):
    """Draws a single nametag, relative to the current coordinate transformation
    """
    # The QRcode
    qrcodeImage = ImageReader("%s.PNG" % (os.path.join(qrcodes, a["Attendee #"])))
    c.drawImage(qrcodeImage, 100, 100)
    # The SciBarCamb logo
    c.drawImage(SciBarCamb_logo, 100, 500)
    # Affiliation details
    c.drawCentredString(150, 250, '%s %s' % (a["First Name"], a["Last Name"]))
    c.drawCentredString(150, 225, a["Job Title"])
    c.drawCentredString(150, 200, a["Company"])
    c.drawCentredString(150, 175, a["Twitter handle"])
    # The animated image
    c.drawImage(animationImage, 100, 300)
    # A credit for the animated gif
    c.drawCentredString(150, 200, "Source: %s" % animationCredit)
    # A tick box for the barstaff to tick after providing a free drink ;) 
    c.rect(250, 225, 25, 25, stroke=1, fill=0)
    # A surround box to help with cutting it out
    c.rect(200, 225, 25, 25, stroke=1, fill=0)

def drawPageOfNameTags(c, SciBarCamb_logo, qrcodeImages, attendees, animationImages, animationCredits):
    """Draw four name tags on a page"""
    assert len(attendees) == 4, "more attendees than expected"
    
    # All translations will be cumulative relative to the standard coordinate system
    drawNameTag(c, SciBarCamb_logo, qrcodes, attendees[0], animationImages[0], animationCredits[1])
    c.translate(1.5*inch, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, attendees[1], animationImages[1], animationCredits[1])
    c.translate(0.0, 2.4*inch)
    drawNameTag(c, SciBarCamb_logo, qrcodes, attendees[2], animationImages[2], animationCredits[2])
    c.translate(-1.5*inch, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, attendees[3], animationImages[3], animationCredits[3])
    
    # Complete the page, ready to move on to the next one
    c.showPage()

def processAttendees(attendeeReader,logos,qrcodes,outdir):
    """Takes the list of attendees, pads out to 100 as necessary, permutes the
    list and then groups into fours for compilation into a PDF.
    
    Also generates the moire images on the fly, for inclusion into the name tags
    """
    # TODO: First generate the 100 images
    animationImages = []
    
    # TODO: Pad out the list list of attendees to 100
    
    # TODO: Permute the list
    
    # TODO: Take items in fours and compile pages
    
    c = canvas.Canvas(os.path.join(outdir,"SciBarCamb-nametags.pdf"))
    
    for a in attendeeReader:
        print "Processing: %s %s" % (a["First Name"], a["Last Name"])
        
        aniIm = ImageReader("moire-1.PNG")
        
        SciBarCamb_logo = ImageReader(os.path.join(logos, "SciBar_No shadow.jpg"))
        
        drawPageOfNameTags(c, SciBarCamb_logo, qrcodes, attendees, animationImages, animationCredits)
        
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
    # The directory containing pre-generated QRcodes
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
