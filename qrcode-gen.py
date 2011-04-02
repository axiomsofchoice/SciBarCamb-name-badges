"""
This script will generate qrcodes for all attendees and place them into a
directory where they can be picked up by the PDF generating script. This has the
advantage of caching requests made to the Google Charts API service.

Reads a CSV list of attendees, as provided by Eventbrite and generates QRcodes

Uses the following library:
http://vobject.skyhouseconsulting.com/

Takes arguments:

    height, width  - the height and width of the QRcode image
    attendees      - the csv file from Eventbrite containing the list of
                     attendees
    output         - the directory into which the QRcode PNG image will go
    takenum        - the number of attendees to grab from the list (for testing)
    
The PNG image files will be given names according to the "Attendee #" field.
The images default to a size of 500x500 pixels.
"""

import csv
import itertools
import urllib
import urllib2
import re, sys, getopt, os, re
import vobject
import StringIO
import Image


def gen_qrcode(a, qrcodeHeight, qrcodeWidth, outdir):
    """
    """
    print "Processing: %s %s" % (a["First Name"], a["Last Name"])
    
    # Create a new vCard based on these values
    j = vobject.vCard()
    j.add('n')
    j.n.value = vobject.vcard.Name( family=a["Last Name"], given=a["First Name"] )
    j.add('fn')
    j.fn.value ='%s %s' % (a["First Name"], a["Last Name"])
    j.add('email')
    j.email.value = a["Email"]
    j.email.type_param = 'INTERNET'
    j.add('title')
    j.title.value = a["Job Title"]
    j.add('org')
    j.org.value = a["Company"]
    j.add('url')
    j.url.value = a["Website"]
    j.add('x-kaddressbook-blogfeed')
    j['x-kaddressbook-blogfeed'].value = a["Blog"]
    # Tidy up twitter handle to ensure it always has an @ prefix
    j.add('x-twitter')
    teststr = a["Twitter handle"]
    myreg = re.compile( "^@.*" )
    if myreg.match(teststr) is None:
        j['x-twitter'].value = "@%s" % teststr
    else:
        j['x-twitter'].value = teststr
    
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
    
    myImg.save("%s.PNG" % (os.path.join(outdir, a["Attendee #"])))

def main():
    
    # When present get options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:w:a:o:t:", 
                      ["height=", "width=", "attendees=", "output=", "take="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(-1)
        
    # Define the dimensions of the QRcodes required (here we give defaults)
    (qrcodeWidth, qrcodeHeight) = (500,500)
    # The directory into which we store the QRcodes (again, the default)
    outdir = "qrcodes"
    # The name of the CSV file from Eventbrite contain the list of attendees
    attendeelist = None
    # Number of attendees to take from the list (for testing)
    takenum = None
    
    for o, a in opts:
        if o == ("-h", "--height"):
            qrcodeHeight = a
        elif o in ("-w", "--width"):
            qrcodeWidth = a
        elif o in ("-a", "--attendees"):
            attendeelist = a
        elif o in ("-o", "--output"):
            outdir = a
        elif o in ("-t", "--take"):
            takenum = a
        else:
            assert False, "unhandled option"
            
    
    # Open the CSV file
    try:
        attendeeReader = csv.DictReader(open(attendeelist, 'rb'))
    except err:
        print str(err)
    
    # Before running the process, ensure that the output directory exists
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    # For testing just grab the first takenum attendees
    if takenum is not None:
        for a in itertools.islice(attendeeReader,int(takenum)):
            gen_qrcode(a,qrcodeHeight,qrcodeWidth,outdir)
    else:
        for a in attendeeReader:
            gen_qrcode(a,qrcodeHeight,qrcodeWidth,outdir)

if __name__ == "__main__" :
    main()
