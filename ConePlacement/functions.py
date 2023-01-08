"""HELPER FUNCTIONS FOR THE PIPELINES"""


import cv2 as cv
import numpy as np
import constants


def filter_retro(frame:cv.Mat) -> cv.Mat:
    as_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(as_hsv, (constants.HUE[0], constants.SAT[0], constants.VAL[0]), (constants.HUE[1], constants.SAT[1], constants.VAL[1]))
    return mask




def get_convex_hulls(frame:cv.Mat):
    """The frame must be binary or gray."""

    contours, hierarchy = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    convex_hulls = []
    for c in contours:
        x,y,w,h = cv.boundingRect(c)
        hull = cv.convexHull(c)
        contour_area = cv.contourArea(c)
        hull_area = cv.contourArea(hull)
        solid = 100 * contour_area / hull_area  ##divide the contourarea

        ##FILTERING FOR SOLIDITY
        if not (solid < constants.FILTER_CONTOUR_SOLIDITY[0] or solid > constants.FILTER_CONTOUR_SOLIDITY[1]):
            if w/h < constants.MAX_CONTOUR_RATIO:
                convex_hulls.append(hull)
    
    return convex_hulls


def blur(frame:cv.Mat) -> cv.Mat:
    ksize = int(6 * round(constants.BLUR_RADIUS) + 1)
    return cv.GaussianBlur(frame, (ksize, ksize), round(constants.BLUR_RADIUS))

