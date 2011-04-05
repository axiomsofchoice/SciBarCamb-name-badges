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
import StringIO
import moire

def drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, a):
    """Draws a single nametag, relative to the current coordinate transformation
    leaving blanks where appropriate.
    """
    if "First Name" in a and "Last Name" in a:
        print "Processing: %s %s" % (a["First Name"], a["Last Name"])
    else:
        print "Processing a blank attendee"
    
    # The QRcode
    if os.path.exists("%s.PNG" % (os.path.join(qrcodes, a["Attendee #"]))):
        qrcodeImage = ImageReader("%s.PNG" % (os.path.join(qrcodes, a["Attendee #"])))
        c.drawImage(qrcodeImage, 100, 100)
    # The SciBarCamb logo
    c.drawImage(SciBarCamb_logo, 100, 500)
    # Affiliation details
    if "First Name" in a and "Last Name" in a:
        c.drawCentredString(150, 250, '%s %s' % (a["First Name"], a["Last Name"]))
    if "Job Title" in a:
        c.drawCentredString(150, 225, a["Job Title"])
    if "Company" in a:
        c.drawCentredString(150, 200, a["Company"])
    if "Twitter handle" in a:
        c.drawCentredString(150, 175, a["Twitter handle"])
    # The animated image (a slight hack ;))
    animationImage = ImageReader("%s.PNG" % os.path.join(anidir, a["Attendee #"]))
    c.drawImage(animationImage, 100, 300)
    # A tick box for the barstaff to tick after providing a free drink ;) 
    c.rect(250, 225, 25, 25, stroke=1, fill=0)
    # A surround box to help with cutting it out
    c.rect(200, 225, 25, 25, stroke=1, fill=0)

def drawPageOfNameTags(c, SciBarCamb_logo, qrcodes, anidir, attendees):
    """Draw four name tags on a page"""
    assert len(attendees) == 4, "more attendees than expected"
    
    # All translations will be cumulative relative to the standard coordinate system
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[0])
    c.translate(1.5*inch, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[1])
    c.translate(0.0, 2.4*inch)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[2])
    c.translate(-1.5*inch, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[3])
    
    # Complete the page, ready to move on to the next one
    c.showPage()

def processAttendees(attendeeReader,logos,qrcodes,outdir):
    """Takes the list of attendees, pads out to 100 as necessary, permutes the
    list and then groups into fours for compilation into a PDF.
    
    Also generates the moire images on the fly, for inclusion into the name tags
    """
    # The PDF file we will output
    c = canvas.Canvas(os.path.join(outdir,"SciBarCamb-nametags.pdf"))
    
    # Pad out the list list of attendees to 100
    attendeeList = list(attendeeReader)
    if len(attendeeList) < 100:
        for i in range(100-len(attendeeList)):
            attendeeList.append(dict({"Attendee #": str(i)}))
    assert len(attendeeList) == 100, "expecting exactly 100 attendees"
    
    # Generate the 100 images, based on attendee number.
    # These are the animations, and the places the were obtained
    anidir = "animations"
#    animations = [ { "file": Image.open(os.path.join(anidir,"Vortex-street-animation.gif")),
#                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
#                    "shortsource" : "http://bit.ly/a5QbLl" } ,
#                   { "file": Image.open(os.path.join(anidir,"SN2.gif")),
#                    "source" : "http://www.bluffton.edu/~bergerd/classes/cem221/sn-e/SN2.gif",
#                    "shortsource" : "http://bit.ly/eLZYXJ" } ,
#                   { "file": Image.open(os.path.join(anidir,"ADN_animation.gif")),
#                    "source" : "http://upload.wikimedia.org/wikipedia/commons/8/81/ADN_animation.gif",
#                    "shortsource" : "http://bit.ly/3wx3wz" } ,
#                   { "file": Image.open(os.path.join(anidir,"mitosis.gif")),
#                    "source" : "http://www.sci.sdsu.edu/multimedia/mitosis/mitosis.gif",
#                    "shortsource" : "http://bit.ly/etm4Lg" } ,
#                   { "file": Image.open(os.path.join(anidir,"Pangea_animation_03.gif")),
#                    "source" : "http://i306.photobucket.com/albums/nn247/quantum_flux/Animations/Evolution%20and%20Cosmology/Pangea_animation_03.gif",
#                    "shortsource" : "http://bit.ly/hqhfQn" } ]
    animations = [ { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "http://bit.ly/a5QbLl" } ,
                   { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "http://bit.ly/a5QbLl" } ,
                   { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "http://bit.ly/a5QbLl" } ,
                   { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "http://bit.ly/a5QbLl" } ,
                   { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "http://bit.ly/a5QbLl" } ]
                    
    # This generates the images and puts them on the filesystem :(
    moire.get100images(attendeeList, animations, anidir)
    
    # Take items in fours and compile pages
    for i in range(0, len(attendeeList), 4):
        drawPageOfNameTags(c, ImageReader(os.path.join(logos, "SciBar_No shadow.jpg")),
                            qrcodes, anidir, attendeeList[i:i+4])
        
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
