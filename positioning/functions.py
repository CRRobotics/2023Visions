"""Functions that help make the pipeline more readable"""



from pupil_apriltags import *
import cv2 as cv
import numpy as np
import constants



def getDetections(grayframe) -> Detection:
    return constants.DETECTOR.detect(grayframe)


def draw(img, corners, imgpts):
    
    for i in range(len(corners)):
        corners[i] = (int(corners[i][0]), int(corners[i][1]), int(corners[i][2]))


    corner = tuple(corners[0].ravel())

    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 10)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 10)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 10)

    return img


