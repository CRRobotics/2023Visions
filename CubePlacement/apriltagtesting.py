from pupil_apriltags import Detector
import cv2 as cv
import constants
from functions import *


cap = cv.VideoCapture(0)


while True:
    success, frame = cap.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    detection = getDetections(grayframe=gray)


    if detection:
        print(detection[0].tag_id)
        for x, y in detection[0].corners:

            cv.circle(frame, (int(x), int(y)), 10, (255,0,0), -1)

    else:
        print("NONE")




    cv.imshow("IMAGE", frame)


    cv.waitKey(1)