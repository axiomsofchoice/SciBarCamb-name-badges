SciBarCamb Name Badges
======================

First export a list of attendees from Eventbright in CSV format.

Then generate a list of qrcodes for the attendees using qrcodeGen.py:

    $ python qrcodeGen.py --height=500 --width=500 --attendees='./attendees/Attendees-2883876753.csv' --output='./qrcodes/'

Finally run nametags.py to generate the nametags themselves:

    $ python nametags.py --logos='./logos/' --attendees='./attendees/Attendees-2883876753.csv' --qrcodes='./qrcodes/' --output='./nametags/'
