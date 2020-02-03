#!/usr/bin/env python3
# Get image from clipboard and decode it.
# Requirements:
#   brew install zbar
#   pip install pillow pyzbar
from PIL import ImageGrab
from pyzbar.pyzbar import decode

img = ImageGrab.grabclipboard()
print(decode(img)[0].data)