import libjevois as jevois # type: ignore
import cv2
from datetime import datetime
import math
import numpy as np
import re
lower_yellow=np.array([0,0,0])

higher_yellow=np.array([40,255,255])

SERVER="10.6.39.2"
from networktables import NetworkTables as nt
def pushval(networkinstance, tablename:str, valuename, value:float):
    table = networkinstance.getTable(tablename)
    table.putNumber(valuename, value)

def networkConnect() -> any:
    cond = threading.Condition()
    notified = [False]

    def connectionListener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()

    nt.initialize(server=SERVER)
    nt.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()
    return nt


def maskGenerator2(img,lower_color,higher_color):

    #bgr math
    img==cv2.blur(img, (5,5)) 
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(g, b)
    ret, maska = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    maska=cv2.erode(maska,kernel1,iterations=3)
    maska=cv2.dilate(maska,kernel1,iterations=1) 

    #hsv double check
    img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    maskb=cv2.inRange(img,lower_color,higher_color)    
    maskb=cv2.erode(maskb,kernel1,iterations=3)
    maskb=cv2.dilate(maskb,kernel1,iterations=1)
    maskab = cv2.bitwise_and(maska, maskb)
    return maskab

def findContours(mask):
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours=[cv2.convexHull(contour) for contour in contours]
    return contours


def find_biggest_contour(contours):
    sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
    biggest_contour=sortedContours[0]
    return biggest_contour

def find_center_and_draw_center_and_contour_of_target(frame,biggest_contour):
    cv2.drawContours(frame,[biggest_contour],0,(255,0,255),3)
    moments = cv2.moments(biggest_contour)
    if moments['m00'] !=0:
        center=((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
        cv2.circle(frame, center, 3, (0, 0, 255), -1)
        return center

class Orientation_of_Cone:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("processing timer", 100, jevois.LOG_INFO)
        self.pattern = re.compile('([0-9]*\.[0-9]+|[0-9]+) fps, ([0-9]*\.[0-9]+|[0-9]+)% CPU, ([0-9]*\.[0-9]+|[0-9]+)C,')
        # a simple frame counter used to demonstrate sendSerial():
        self.frame = 0
        self.framerate_fps = "0"
        self.CPULoad_pct = "0"
        self.CPUTemp_C = "0"
        self.pipelineDelay_us = "0"
        self.redBallAngle = -1
        self.redBallDistance = -1

        self.blueBallAngle = -1
        self.blueBallDistance = -1  
        jevois.sendSerial("Constructor called")
        jevois.LINFO("Constructor  logging info")


    # ###################################################################################################
    ## Process function with no USB output
    def processNoUSB(self, inframe):
        self.commonProcess(inframe=inframe)
        
    # ###################################################################################################
    ## Process function with USB output
    def process(self, inframe, outframe):
        self.commonProcess(inframe=inframe, outframe=outframe)

    def commonProcess(self, inframe, outframe = None):
        # jevois.LINFO("inframe type is "+str(type(inframe)))
        # Get the next camera image (may block until it is captured) and here convert it to OpenCV BGR. If you need a
        # grayscale image, just use getCvGRAY() instead of getCvBGR(). Also supported are getCvRGB() and getCvRGBA():
        frame = inframe.getCvBGR()
        # Start measuring image processing time (NOTE: does not account for input conversion time):
        self.timer.start()
        pipline_start_time = datetime.now()
        '''
        Vertical up is 0 degrees
        '''
        mask2=maskGenerator2(frame,lower_yellow,higher_yellow)
        contours2=findContours(mask2) 
        if len(contours2) >0:
            biggest_contour2=find_biggest_contour(contours2)
            area2=cv2.contourArea(biggest_contour2) 
            if area2 >= 1600:
                center2=find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
                point_x2,point_y2=center2
                #cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
                approx = cv2.approxPolyDP(biggest_contour2, 150, True)
                #  cv2.polylines(frame, [approx], True, (0, 255, 255), 2)
                # cv2.putText(frame,str(len(approx)),(point_x2,point_y2-40),0,1,(255,0,0),2)
                if len(approx)==3:
                    points_array=approx.tolist()
                    points_tuple=[]#position of the three major points
                    for i in points_array:
                        for c in i:
                            c=tuple(c)
                            points_tuple.append(c)
                    point_a=points_tuple[0]
                    xa,ya=point_a
                    point_b=points_tuple[1]
                    xb,yb=point_b
                    point_c=points_tuple[2]
                    xc,yc=point_c
                    ab=((yb-ya)**2+(xb-xa)**2)**(1/2)
                    ac=((yc-ya)**2+(xc-xa)**2)**(1/2)
                    bc=((yc-yb)**2+(xc-xb)**2)**(1/2)
                    angle_a=math.degrees(math.acos(((ab)**2+(ac)**2-(bc)**2)/(2*(ab)*(ac))))
                    angle_b=math.degrees(math.acos(((bc)**2+(ab)**2-(ac)**2)/(2*(bc)*(ab))))
                    angle_c=math.degrees(math.acos(((bc)**2+(ac)**2-(ab)**2)/(2*(bc)*(ac))))
                    lister=[]
                    lister.append(angle_a)
                    lister.append(angle_b)
                    lister.append(angle_c)
                    min=500
                    indexer=0
                    for i in range(3):
                        angle=lister[i]
                        if angle <= min:
                            min = angle
                            indexer=i
                    target_point=points_tuple[indexer]
                    cv2.arrowedLine(frame, center2, target_point,(0,255,0), 9) 
                    x_final,y_final=target_point#point_x2,point_y2=center2
                    #difine a lower point
                    dis_center_to_target=((point_x2-x_final)**2+(point_y2-y_final)**2)**(1/2)
                    lower_x=point_x2
                    lower_y=point_y2-dis_center_to_target
                    dis_target_to_lower=((lower_x-x_final)**2+(lower_y-y_final)**2)**(1/2)
                    angle_final=math.acos(((dis_center_to_target)**2+(dis_center_to_target)**2-(dis_target_to_lower)**2)/(2*(dis_center_to_target)*(dis_center_to_target)))
                    if x_final<point_x2:
                        angle_final=(-1)*angle_final
                    # cv2.arrowedLine(frame, center2, (lower_x,lower_y),(0,0,255), 9) 
                    cv2.putText(frame,str(math.degrees(angle_final)),(point_x2,point_y2-10),0,1,(255,0,0),2)
                    nt = networkConnect()
                    pushval(nt,'Internal' , "Orientation_of_Cone", angle_final)