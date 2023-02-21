import libjevois as jevois
import cv2
import numpy as np
import math
import re
## Tell Orientation of Cones
#
# Add some description of your module here.
#
# @author Rocky Shao
# ??????????????
# @videomapping YUYV 640 480 30 YUYV 640 480 30 Orientation Orientation
# @email rocky.shao@icsd.k12.ny.us
# @address 123 first street, Los Angeles CA 90012, USA
# @copyright Copyright (C) 2018 by Rocky Shao
# @mainurl https://www.ithacacityschools.org/
# @supporturl https://www.ithacacityschools.org/
# @otherurl https://www.ithacacityschools.org/
# @license license
# @distribution Unrestricted
# @restrictions None
# @ingroup modules
#save the test
lower_yellow=np.array([0,0,0])

higher_yellow=np.array([40,255,255])
def maskGenerator1(img):#for cube
    img=cv2.blur(img, (5,5)) 
    #img= cv2.GaussianBlur(img, (15, 15), 0)
    b,g,r =cv2.split(img)     
    diff = cv2.subtract(b,g)
    ret, mask = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask=cv2.erode(mask,kernel1,iterations=3)
    mask=cv2.dilate(mask,kernel1,iterations=1) 
    '''
    Make a hsv double check for cubes
    '''
    return mask
def maskGenerator2(img,lower_color,higher_color):

    #bgr math
    # img==cv2.blur(img, (5,5)) 
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(g, b)
    ret, maska = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)

    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    # 
    # maska=cv2.dilate(maska,kernel1,iterations=5) 
    
    maska=cv2.erode(maska,kernel1,iterations=3)
    maska=cv2.dilate(maska,kernel1,iterations=3) 
    return maska
 
# def maskGenerator2(img,lower_color,higher_color):

#     #bgr math
#     # img==cv2.blur(img, (5,5)) 
#     b,g,r=cv2.split(img)     
#     diff = cv2.subtract(g, b)
#     ret, maska = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)

#     kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
#     # 
#     # maska=cv2.dilate(maska,kernel1,iterations=5) 
    
#     maska=cv2.erode(maska,kernel1,iterations=3)
#     maska=cv2.dilate(maska,kernel1,iterations=3) 
    

#     # hsv double check
#     img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#     maskb=cv2.inRange(img,lower_color,higher_color) 
#     # maskb=cv2.dilate(maskb,kernel1,iterations=1)
#     maskab = cv2.bitwise_and(maska, maskb)
#     return maskab
#     return maska

def circularmask(img):
    radius2 = 175
    ww, hh, _ = img.shape
    xc = hh // 2
    yc = ww // 2

    print(xc, yc)
    
    mask2 = np.zeros_like(img)
    mask = cv2.circle(mask2, (xc,yc), radius2, (255,255,255), -1)
    dst = cv2.bitwise_and(img, mask2)
    return dst



# def maskGenerator3(img):
#     img==cv2.blur(img, (5,5))
#     b,g,r=cv2.split(img)
#     _, maskr = cv2.threshold(r, 50, 255, cv2.THRESH_BINARY)
#     _, maskg = cv2.threshold(g, 50, 255, cv2.THRESH_BINARY)
#     masky = cv2.bitwise_and(maskr, maskg)
#     _, maskb = cv2.threshold(b, 50, 255, cv2.THRESH_BINARY)
#     maskb = cv2.bitwise_not(maskb)
#     mask = cv2.bitwise_and(masky, maskb)
#     return mask

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
    
'''prototype'''
def angle_between(p1, p2, p3):
    """Calculate the angle between three points in radians."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    a = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    b = math.sqrt((x2-x3)**2 + (y2-y3)**2)
    c = math.sqrt((x3-x1)**2 + (y3-y1)**2)
    return math.acos((a**2 + b**2 - c**2) / (2 * a * b))

def smallest_angle_vertex(vertices):
    """Find the vertex with the smallest angle in a polygon."""
    angles = []
    for i in range(len(vertices)):
        p1 = vertices[i-1]
        p2 = vertices[i]
        p3 = vertices[(i+1) % len(vertices)]
        angles.append(angle_between(p1, p2, p3))
    min_angle = min(angles)
    min_index = angles.index(min_angle)
    return vertices[min_index]
class Orientation:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("processing timer", 100, jevois.LOG_INFO)
        self.CPULoad_pct = "0"
        self.CPUTemp_C = "0"
        self.pattern = re.compile('([0-9]*\.[0-9]+|[0-9]+) fps, ([0-9]*\.[0-9]+|[0-9]+)% CPU, ([0-9]*\.[0-9]+|[0-9]+)C,')
        self.frame = 0
        self.angle_final = 0

    def find_cube(self,frame):
            mask1 = maskGenerator1(frame)
            contours1=findContours(mask1)   
            cv2.drawContours() 
            #contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
            if len(contours1) >0:
                biggest_contour1=find_biggest_contour(contours1)
                center1=find_center_and_draw_center_and_contour_of_target(frame,biggest_contour1)
                area1=cv2.contourArea(biggest_contour1) 
                if area1 >= 1600:
                    self.angle_final = 100
    def find_cone(self,frame):
        mask2=maskGenerator2(frame,lower_yellow,higher_yellow)
        contours2=findContours(mask2) 
        if len(contours2) >0:
            biggest_contour2=find_biggest_contour(contours2)
            area2=cv2.contourArea(biggest_contour2) 
            if area2 >= 1600:
                center2=find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
                point_x2,point_y2=center2
                #cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
                epsilon = 0.05 * cv2.arcLength(biggest_contour2, True)
                approx = cv2.approxPolyDP(biggest_contour2, epsilon, True)
                cv2.polylines(frame, [approx], True, (0, 255, 0), 6)
                cv2.putText(frame,str(len(approx)),(point_x2,point_y2-40),0,1,(255,0,0),2)
            
                points_array=approx.tolist()
                points_tuple=[]#position of the three major points
                for i in points_array:
                    for c in i:
                        c=tuple(c)
                        points_tuple.append(c)
                target_point = smallest_angle_vertex(points_tuple)
                cv2.arrowedLine(frame, center2, target_point,(255,0,0), 9) 
                x_final,y_final=target_point#point_x2,point_y2=center2
                #difine a lower point
                dis_center_to_target=((point_x2-x_final)**2+(point_y2-y_final)**2)**(1/2)
                lower_x=point_x2
                lower_y=point_y2-dis_center_to_target
                dis_target_to_lower=((lower_x-x_final)**2+(lower_y-y_final)**2)**(1/2)
                self.angle_final=math.acos(((dis_center_to_target)**2+(dis_center_to_target)**2-(dis_target_to_lower)**2)/(2*(dis_center_to_target)*(dis_center_to_target)))
                if x_final<point_x2:
                    self.angle_final=(-1)*self.angle_final
                # cv2.arrowedLine(frame, center2, (lower_x,lower_y),(0,0,255), 9) 
                cv2.putText(frame,str(math.degrees(self.angle_final)),(point_x2,point_y2-10),0,1,(255,0,0),2)
    
    # ###################################################################################################
    def processNoUSB(self, inframe):
        self.commonProcess(inframe=inframe)
        

    # ###################################################################################################
    ## Process function with USB output
    def process(self, inframe, outframe):
        _, outimg = self.commonProcess(inframe, outframe)
        outframe.sendCv(outimg)

   
        
    ## Process function with USB output
    def commonProcess(self, inframe, outframe):

        frame = inframe.getCvBGR()
        frame = circularmask(frame)
        # Start measuring image processing time (NOTE: does not account for input conversion time):
            
        self.timer.start()
        

        '''
        Cube
        '''
        self.find_cube(frame = frame)
        if self.angle_final!= 100:
            self.find_cone(frame = frame)
        outimg = frame
        # Write a title:
        cv2.putText(outimg, "JeVois Orientation", (3, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        
        # Write frames/s info from our timer into the edge map (NOTE: does not account for output conversion time):
        fps = self.timer.stop()
        height = outimg.shape[0]
        width = outimg.shape[1]
        cv2.putText(outimg, fps, (3, height - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        
        # Convert our output image to video output format and send to host over USB:
        results = self.pattern.match(self.timer.stop())
        if(results is not None):
            self.framerate_fps = results.group(1)
            self.CPULoad_pct = results.group(2)
            self.CPUTemp_C = results.group(3)

        
        serialstr = "{%d %.2f %s %s}"%(
            self.frame,
            self.angle_final,
            self.CPULoad_pct,
            self.CPUTemp_C
        )

        jevois.sendSerial(serialstr)

        self.frame += 1
        self.frame %= 999

        return self.angle_final, outimg
        
'''Pleaes send the value of angle_final to the bot'''
'''it is in degrees of where the tip of the cone is pointing twards'''
'''tip of cone pointing up is 0'''
'''CW is positive'''
'''CCW is negetive'''
