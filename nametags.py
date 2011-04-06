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
from reportlab.lib.colors import black
import StringIO
import moire

def drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, a, permuationClasses):
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
    animationImage = ImageReader("%s.PNG" % os.path.join(anidir, a["Attendee #"]))
    c.drawImage(animationImage, 0.0*cm, 0.0*cm)
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
    if "Twitter handle" in a:
        validtwitterhandleregex = re.compile( "^(?P<handleprefix>@)?(?P<handle>.+)" )
        teststr = a["Twitter handle"]
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
    c.drawString(8.5*cm, 6.3*cm, str(permuationClasses[a["Attendee #"]]))

def drawPageOfNameTags(c, SciBarCamb_logo, qrcodes, anidir, attendees, permuationClasses):
    """Draw four name tags on a page"""
    assert len(attendees) == 4, "more attendees than expected"
    
    # All translations will be cumulative relative to the standard coordinate system
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[0], permuationClasses)
    c.translate(10.0*cm, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[1], permuationClasses)
    c.translate(0.0, 15.0*cm)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[2], permuationClasses)
    c.translate(-10.0*cm, 0.0)
    drawNameTag(c, SciBarCamb_logo, qrcodes, anidir, attendees[3], permuationClasses)
    
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
#                   { "file": os.path.join(anidir,"pangena2.gif"),
#                    "source" : "http://upload.wikimedia.org/wikipedia/commons/8/8e/Pangea_animation_03.gif",
#                    "shortsource" : "" } ,
#                   { "file": Image.open(os.path.join(anidir,"Pangea_animation_03.gif")),
#                    "source" : "http://upload.wikimedia.org/wikipedia/commons/8/8e/Pangea_animation_03.gif",
#                    "shortsource" : "http://bit.ly/hqhfQn" } ]
# A useful tool for removing frames: http://www.blibs.com/editor/
# A useful tool for fixing animated gifs with transparency: http://www.online-image-editor.com/
# http://webpages.ursinus.edu/mtakats/gifcat/orbit.gif
    animations = [ { "file": os.path.join(anidir,"Vortex-street-animation.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif",
                    "shortsource" : "" } ,
                   { "file": os.path.join(anidir,"an_dna2.gif"),
                    "source" : "http://upload.wikimedia.org/wikipedia/commons/7/77/An_dna.gif",
                    "shortsource" : "" } ,
#                   { "file": os.path.join(anidir,"dna_overlay.gif"),
#                    "source" : "http://upload.wikimedia.org/wikipedia/commons/1/16/DNA_orbit_animated.gif",
#                    "shortsource" : "http://bit.ly/a5QbLl" } ,
                   { "file": os.path.join(anidir,"sn2_overlay.gif"),
                    "source" : "http://www.bluffton.edu/~bergerd/classes/cem221/sn-e/SN2.gif",
                    "shortsource" : "" } ,
                   { "file": os.path.join(anidir,"CO2.gif"),
                    "source" : "http://www2.ess.ucla.edu/~schauble/MoleculeHTML/CO2_html/CO2_PIu.gif",
                    "shortsource" : "" } ,
                   { "file": os.path.join(anidir,"mitosis-2.gif"),
                    "source" : "http://www.sci.sdsu.edu/multimedia/mitosis/mitosis.gif",
                    "shortsource" : "" } ]
                    
    # This generates the images and puts them on the filesystem :(
    permuationClasses = moire.get100images(attendeeList, animations, anidir)
    
    # Take items in fours and compile pages
    for i in range(0, len(attendeeList), 4):
        drawPageOfNameTags(c, ImageReader(os.path.join(logos, "SciBar_No shadow.jpg")),
                            qrcodes, anidir, attendeeList[i:i+4], permuationClasses)
        
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
