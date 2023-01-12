from pupil_apriltags import Detector
import cv2 as cv
import constants
from functions import *
import numpy as np
print("We out")

cap = cv.VideoCapture(0)
cap2 = cv.VideoCapture(1)

while True:
    success, frame1 = cap.read()
    success2, frame2 = cap2.read()

    #UNCOMMENT THIS IF YOU WANT TO TEST ON AN IMG
    # frame = cv.imread(r"ConePlacement/sample_images/Straight__Left_187in.png")

    gray = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)

    vecsdict = getVecs(gray, constants.CAMERA_MATRIX1, constants.CAMERA_DIST1)
    print(vecsdict)
    cv.imshow("IMAGE", gray)


    cv.waitKey(1)
