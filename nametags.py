"""
Reads a CSV list of attendee, as provided by Eventbrite and gen

Uses the following library
http://www.reportlab.com/apis/reportlab/dev/

"""

import csv
import itertools
import re, sys, os
import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
#import moire

def drawNameTag():
    """Draws a single nametag, relative to the current coordinate transformation
    """
    pass

def drawPageOfNameTags():
    """Draw four name tags on a page"""
    pass

def processAttendees():
    """Takes the list of attendees, pads out to 100 as necessary, permutes the
    list and then groups into fours for compilation into a PDF.
    """
    # For testing just grab the first 5 attendees
    for a in itertools.islice(attendeeReader,5):
        print "Processing: %s %s" % (a["First Name"], a["Last Name"])
        
        # Create a new vCard based on these values
        j = vobject.vCard()
        j.add('n')
        j.n.value = vobject.vcard.Name( family=a["Last Name"], given=a["First Name"] )
        j.add('fn')
        j.fn.value ='%s %s' % (a["First Name"], a["Last Name"])
        j.add('email')
        j.email.value = a["Email"]
        j.add('title')
        j.email.value = a["Job Title"]
        j.add('org')
        j.email.value = a["Company"]
        j.add('url')
        j.email.value = a["Website"]
        j.add('x-kaddressbook-blogfeed')
        j.email.value = a["Blog"]
        # TODO: tidy up twitter handle to ensure it always has an @ prefix
        j.add('x-twitter')
        j.email.value = a["Twitter handle"]
        j.email.type_param = 'INTERNET'
        
        # Request a QRcode from the Google Charts API using the vCard data (Assume an encoding of UTF-8)
        url = "https://chart.googleapis.com/chart"
        values = {'cht' : 'qr',
                    'chs' : '%sx%s'%(qrcodeWidth,qrcodeHeight),
                    'chl' : j.serialize(),
                    'choe' : 'UTF-8' }
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        
        f = urllib2.urlopen(req)
        fcontents = f.read()
        
        # In order to turn this into an Image object we need to wrap the string
        # data into StringIO
        f2 = StringIO.StringIO(fcontents)
        
        # Read the file returned and parse as an image
        myImg = Image.open(f2)
        
        myImg.save("%s-%s.PNG" % (a["First Name"], a["Last Name"]))
        
        im = ImageReader("%s-%s.PNG" % (a["First Name"], a["Last Name"]))
        SciBarCamb_logo = ImageReader("SciBar_No shadow.jpg")
        aniIm = ImageReader("moire-1.PNG")
        
        c = canvas.Canvas("%s-%s.pdf" % (a["First Name"], a["Last Name"]))
        
        # The QRcode
        c.drawImage(im, 100, 100)
        # The SciBarCamb logo
        c.drawImage(SciBarCamb_logo, 100, 500)
        # Affiliation details
        c.drawCentredString(150, 250, '%s %s' % (a["First Name"], a["Last Name"]))
        c.drawCentredString(150, 225, a["Job Title"])
        c.drawCentredString(150, 200, a["Company"])
        c.drawCentredString(150, 175, a["Twitter handle"])
        # The animated image
        c.drawImage(aniIm, 100, 300)
        # A credit for the animated gif
        #c.drawCentredString(150, 200, "Source: http://bit.ly/foo")
        # A tick box for the barstaff to tick after providing a free drink ;) 
        c.rect(250, 225, 25, 25, stroke=1, fill=0)
        # A surround box to help with cutting it out
        #c.rect(200, 225, 25, 25, stroke=1, fill=0)
        
        
        c.showPage()
        c.save()

def main():
    
    exit(0)
    # When present get options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:q:o:", 
                      ["attendees=", "qrcodes=", "output="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(-1)
        
    # Define the dimensions of the QRcodes required (here we give defaults)
    (qrcodeWidth, qrcodeHeight) = (500,500)
    # The directory into which we store the QRcodes (again, the default)
    outdir = "nametags"
    # The name of the CSV file from Eventbrite contain the list of attendees
    attendeelist = None
    # Number of attendees to take from the list (for testing)
    takenum = None
    
    for o, a in opts:
        if o in ("-a", "--attendees"):
            attendeelist = a
        elif o in ("-o", "--output"):
            outdir = a
        elif o in ("-t", "--take"):
            takenum = a
        else:
            assert False, "unhandled option"
            
    
    # Open the CSV file
    attendeeReader = csv.DictReader(open(attendeelist, 'rb'))
    
    # Before running the process, ensure that the output directory exists
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    

if __name__ == "__main__" :
    main()
