#!/usr/bin/python3

import cv2

from picamera2 import *

# Grab images as numpy arrays and leave everything else to OpenCV.

cv2.startWindowThread()

picam2 = Picamera2()
picam2.start()

while True:
    im = picam2.capture_array()

    grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Camera", im)
