"""Functions that help make the pipeline more readable"""



from pupil_apriltags import *
import cv2 as cv
import constants



def getDetections(grayframe) -> Detection:
    return constants.DETECTOR.detect(grayframe)