import csv
#import moire

# Reads a CSV list of attendee, as provided by Eventbrite and 

# Open the CSV file
attendeeReader = csv.DictReader(open('Attendees-1371019757.csv', 'rb'))

# Get the 

## The fields of the csv file are
#"Attendee #","Date","Last Name","First Name","Email","QTY","Ticket Type",
#"Date Attending","Order #","Order Type","Amount (USD)","Fees Paid (USD)",
#"Attendee Status","Twitter handle",
#"If you have any dietary requirements or accessibility needs, please let us know here.",
#"Job Title","Company","Website","Blog"

for a in attendeeReader:
    print a["First Name"]
    print a["Last Name"]
    print a["Website"]
    print a["Blog"]
    print a["Job Title"]
    print a["Company"]
    print a["Twitter handle"]

