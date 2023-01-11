import cv2 as cv
import numpy as np
from functions import *
import constants

cap  = cv.VideoCapture(0)


while True:
    success, frame = cap.read()

    frame = cv.imread(r"C:\Users\labra\Coding Practice\testing playgroung\Test_AprilTag_0.jpg")

    blurred = blur(frame)
    mask = filter_retro(blurred)

    convexhulls = get_convex_hulls(mask)
    cv.drawContours(frame, convexhulls, -1, (255, 0, 255), 1)

    








    cv.imshow("Frame", frame)
    cv.waitKey(1)