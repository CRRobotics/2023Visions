import cv2
import numpy as np
import math



def maskGenerator(img,lower_color,higher_color):
    mask=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mask=cv2.blur(mask,(5,5))
    mask=cv2.inRange(mask,lower_color,higher_color)    
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    mask=cv2.erode(mask,kernel,iterations=10)
    mask=cv2.dilate(mask,kernel,iterations=10)                                                                                                                                                                                                                                                                                                                                                            
    return mask


def convexHull(contours):
    ConvexHull=[cv2.convexHull(contour) for contour in contours]
    return ConvexHull


def filter_out_contours_that_doesnot_look_like_square(contours):
    filteredContours=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        m=w/h#show how perfect the square i
        if m <1.3 and m >=1 :  
            filteredContours.append(contour)
    return filteredContours


def find_biggest_contour(contours):
    sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
    if len(sortedContours)>0:
        biggest_contour=sortedContours[-1]
        return biggest_contour
    
    
def find_and_draw_center_of_target(frame,biggest_contour): 
    x,y,w,h=cv2.boundingRect(biggest_contour)
    cv2.drawContours(frame,[biggest_contour],0,(255,0,255),3)
    moments = cv2.moments(biggest_contour)
    center=((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
    cv2.circle(frame, center, 3, (0, 0, 255), -1)
    return center


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