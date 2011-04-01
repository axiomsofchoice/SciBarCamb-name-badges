import csv
import itertools
#import moire
import urllib
import urllib2
import re, sys
import vobject
import StringIO
import Image
#import  #PDF writer

# Reads a CSV list of attendee, as provided by Eventbrite and 

# TODO: Get attendees filename from command-line
#sys.argv[1]

# Open the CSV file
attendeeReader = csv.DictReader(open('Attendees-1371019757.csv', 'rb'))

# Get the 

## The fields of the csv file are
#"Attendee #","Date","Last Name","First Name","Email","QTY","Ticket Type",
#"Date Attending","Order #","Order Type","Amount (USD)","Fees Paid (USD)",
#"Attendee Status","Twitter handle",
#"If you have any dietary requirements or accessibility needs, please let us know here.",
#"Job Title","Company","Website","Blog"

QRcodes = []

(qrcodeWidth, qrcodeHeight) = (250,100)

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
    


# The SciBarCamb logo
#SciBarCamb_logo = "SciBar_No shadow.jpg"
