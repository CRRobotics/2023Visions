import cv2
import numpy as np
import math

def getCenters(img, contours):
    """_, contours, _ = cv2.findContours
    returns centers of all polygons"""
    centers = []
    for i in range(len(contours)):
        moments = cv2.moments(contours[i])
        centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
        cv2.circle(img, centers[-1], 3, (0, 0, 255), -1)
    return centers

def filtercontours(contours):
    retained = []
    for i in range(len(contours)):
        x,y,w,h=cv2.boundingRect(contours[i])
        countourArea=cv2.contourArea(contours[i])
        ratio=countourArea/(w*h)
        
        if not (ratio >=0.6 or ratio <= 0.4 or countourArea <= 100):
            retained.append(contours[i])

    return retained



def binarizeSubt(img):
    blue, green, red = cv2.split(img)
    yellow=cv2.subtract(green,blue)
    ret,binImage = cv2.threshold(yellow, 40, 255, cv2.THRESH_BINARY)
    return binImage

class Line:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def length(self):
        return np.sqrt(pow(self.x2 - self.x1, 2) + pow(self.y2 - self.y1, 2))

    def angle(self):
        return math.degrees(math.atan2(self.y2 - self.y1, self.x2 - self.x1))

def find_lines(input):
    """Finds all line segments in an image.
    Args:
        input: A numpy.ndarray.
    Returns:
        A filtered list of Lines.
    """
    detector = cv2.createLineSegmentDetector()
    
    if (len(input.shape) == 2 or input.shape[2] == 1):
        lines = detector.detect(input)
    else:
        tmp = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
        lines = detector.detect(tmp)

    output = []

    if len(lines) != 0:
        for i in range(1, len(lines[0])):
            tmp = Line(int(lines[0][i, 0][0]), int(lines[0][i, 0][1]),
                            int(lines[0][i, 0][2]), int(lines[0][i, 0][3]))
            output.append(tmp)
    return output

def in_hull(hull, p):
    return cv2.pointPolygonTest(hull, p, measureDist=False) > 0