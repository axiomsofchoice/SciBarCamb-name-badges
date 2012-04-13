"""Tests the code that generates qrcode PNGs.
"""

from unittest import TestCase
from qrcodeGen import formatAsvCard
import re

class QRCodesGenTests(TestCase):
    """Tests the code that generates qrcode PNGs.
    """
    
    def test_formatAsvCard(self):
        """Tests that a record is correctly formatted as a vCard.
        """
        # Choose a suitable test fixture :)
        a = {    "Attendee #": "87420915",
                 "Date": "Feb 8, 2012",
                 "Last Name": "Hagon",
                 "First Name": "Dan",
                 "Email": "axiomsofchoice@gmail.com",
                 "QTY": "1",
                 "Ticket Type": "Atom",
                 "Date Attending": "Apr 20, 2012",
                 #"": "",
                 "Order #": "68689395",
                 "Order Type": "Free Order",
                 "Total Paid (GBP)": "0.00",
                 "Fees Paid (GBP)": "0.00",
                 "Eventbrite Fees (GBP)": "0.0",
                 "CC Processing (GBP)": "0.00",
                 "Attendee Status": "Attending",
                 "Twitter": "@axiomsofchoice",
                 "Job Title": "",
                 "Company": "Digital Science",
                 "Blog": ""}
        vCardTest = formatAsvCard(a)
        vCardExpected = """BEGIN:VCARD
VERSION:3.0
EMAIL;TYPE=INTERNET:axiomsofchoice@gmail.com
FN:Dan Hagon
N:Hagon;Dan
ORG:Digital Science
X-TWITTER:@axiomsofchoice
END:VCARD
"""
        vCardExpected = re.sub(r'(\r\n|\r|\n)', '\r\n', vCardExpected)
        self.assertEqual(vCardTest, vCardExpected)