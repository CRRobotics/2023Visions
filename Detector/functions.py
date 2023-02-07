
import cv2
import numpy as np
import constants
import math
import threading

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

    nt.initialize(server=constants.SERVER)
    nt.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()
    return nt






def getTrigDistanceFromPixel(pixelX,pixelY,distance):
    degreesOverPixelsV = 42.5/720
    degreesOverPixelsH = 69.4/1280
    cameraOffset = 72
    angleY = math.radians(cameraOffset+(degreesOverPixelsV*pixelY))
    angleX = math.radians(degreesOverPixelsH*pixelX)
    return distance*math.sin(angleX)
    # return ((distance*math.sin(angleX))**2+(distance*math.sin(angleY))**2)**1/2
'''
get distance and angle relitive to the point on the ground wich is directly under the center of the camera.
'''
def get_distance_and_angle(height_of_cam,distance_to_cam,x_of_target,y_of_target):
    distance_to_bot=(distance_to_cam**2 -height_of_cam**2)**(1/2)
    # angle=math.degrees(math.asin(((distance_to_cam) * (math.sin((x_of_target-640)*((math.radians(constants.fov_x))/1280)))/distance)%1))
    angle_to_cam=(x_of_target-640)*((math.radians(constants.fov_x))/1280)
    x_dis_to_bot=distance_to_cam*math.sin(angle_to_cam)
    angle_to_bot=math.asin((x_dis_to_bot/distance_to_bot)%1)


    #cv2.putText(frame,"distance to Bot"+str(distance)+'cm',(x_of_target,y_of_target+30),0,1,(0,0,255),2)
    #cv2.putText(frame,"angle to Bot"+str(angle)+'degree',(x_of_target,y_of_target+60),0,1,(0,0,255),2)
   
    return distance_to_bot,angle_to_bot


def getCorners(convexHull):#second stage dirivitive of all points
    Array =convexHull
    a=Array.tolist()
    b=[]#position of points
    for i in a:
        for c in i:
            c=tuple(c)
            b.append(c)
    first_stage=[]

    for i in range(len(b)):
        xa,xb=b[i]


        if i !=len(b)-1:
            xc,xd=b[i+1]
        elif i == len(b)-1:
            xc,xd=b[0]

        if (xa-xc) !=0:
            element=abs((xb-xd)/(xa-xc))
        elif (xa-xc)==0:
            element=0


        first_stage.append(element)

    
    second_stage=[]
    for i in range(len(first_stage)):
        a=first_stage[i]

        if i!=len(first_stage)-1:
            b=first_stage[i+1]
        elif i == len(first_stage)-1:
            b=first_stage[0]

        if (b-a) !=0:
            element=abs(b-a)
        elif (b-a)==0:
            element=0
            
        second_stage.append(element)
    return second_stage




def find_distance_to_the_point_on_the_target_which_is_on_the_ground_relative_to_cam(contour):

    points_array=contour.tolist()
    points_tuple=[]#position of convex points
    for i in points_array:
        for c in i:
            c=tuple(c)
            points_tuple.append(c)

    # d=[]#matching positions of convex points  on depth map
    # for i in points_tuple:
    #     x,y=i
    #     e=depth_frame[y,x]#first y then x
    #     d.append(e)
    biggest_y=0
    indexer=0
    for i in range(len(points_tuple)):
        x,y=points_tuple[i]
        if y >= biggest_y:
            biggest_y=y
            indexer=i
    return points_tuple[indexer]#position of the point with the biggest y value.



'''
HSV MASK
'''
# def maskGenerator(img,lower_color,higher_color):
#     img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#     img_blur=cv2.blur(img, (5,5)) 
#     mask=cv2.inRange(img_blur,lower_color,higher_color)    
#     kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
#     mask=cv2.erode(mask,kernel1,iterations=3)
#     mask=cv2.dilate(mask,kernel1,iterations=1)       
#     return mask


'''
BGR MASK, 1 for cube, 2 for cone
'''



def maskGenerator1(img):
    img==cv2.blur(img, (5,5)) 
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(b,g)
    ret, mask = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask=cv2.erode(mask,kernel1,iterations=3)
    mask=cv2.dilate(mask,kernel1,iterations=1) 
    return mask


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
    
def maskGenerator3(img):

    #bgr math
    img==cv2.blur(img, (5,5)) 
    b,g,r=cv2.split(img)     
    diff = cv2.add(g, r)
    ret, maska = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    maska=cv2.erode(maska,kernel1,iterations=3)
    maska=cv2.dilate(maska,kernel1,iterations=1) 
    return maska




def findContours(mask):
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours=[cv2.convexHull(contour) for contour in contours]
    return contours
    #return contours



def filter_out_contours_that_doesnot_look_like_square(contours):  
    filteredContours=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        ratio1=cv2.contourArea(contour)/(w*h)
        ratio2=w/h

        #aware of sth infront of cube
        # if ratio1 >= 0.6 and ratio2 >= 0.8 and ratio2 <= 1.05:
        if ratio1 >= 0.5 and ratio2 >= 0.7 and ratio2 <= 1.1:
            filteredContours.append(contour)
    return filteredContours




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

        




