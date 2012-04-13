"""Tests the code that generates qrcode PNGs.
"""

from unittest import TestCase
from qrcodeGen import formatAsvCard

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
        pass