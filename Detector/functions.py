
import cv2
import numpy as np
import constants
import math


#Julius
# def getPerpindicularDistanceToObject(a,d):
#     cameraMountAngle=1.134
#     angle=a-cameraMountAngle
#     b = 0-(d*math.sin(angle))
#     return b


# def getFullDistanceToObject(pDistance,angle):
#     pixelToDegree=0.000946
#     output=pDistance/math.cos(pixelToDegree*angle)
#     return output

# def getDirectDistanceToPixel(deltaPixelX,deltaPixelY,d):
#     xPixelToDegree = 0.000946
#     yPixelToDegree = 0.00103
#     pitch = deltaPixelY*yPixelToDegree
#     yaw = xPixelToDegree*deltaPixelX
#     pDist = getPerpindicularDistanceToObject(pitch,d)
#     distance = getFullDistanceToObject(pDist,yaw)
#     return distance




'''
get distance and angle relitive to the point on the ground wich is directly under the center of the camera.
'''
def get_distance_and_angle(height_of_cam,distance_to_cam,x_of_target,y_of_target):
    distance=(distance_to_cam**2 -height_of_cam**2)**(1/2)
    angle=math.degrees(math.asin(((distance_to_cam) * (math.sin((x_of_target-640)*((math.radians(constants.fov_x))/1280)))/distance)%1))
    #cv2.putText(frame,"distance to Bot"+str(distance)+'cm',(x_of_target,y_of_target+30),0,1,(0,0,255),2)
    #cv2.putText(frame,"angle to Bot"+str(angle)+'degree',(x_of_target,y_of_target+60),0,1,(0,0,255),2)
    distance=float(distance)
    angle=float(angle)
    return distance,angle
def getCorners(convexHull):
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




# def find_distance_to_the_point_on_the_target_wich_is_on_the_ground(contour,depth_frame):

#     points_array=contour.tolist()
#     points_tuple=[]#position of convex points
#     for i in points_array:
#         for c in i:
#             c=tuple(c)
#             points_tuple.append(c)
    
#     d=[]#matching positions of b on depth map
#     for i in points_tuple:
#         x,y=i
#         e=depth_frame[y,x]#first y then x
#         d.append(e)

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
# def maskGenerator1(img):
#     img==cv2.blur(img, (5,5)) 
#     b,g,r=cv2.split(img)     
#     diff = cv2.subtract(b,g)
#     ret, mask = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
#     kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
#     mask=cv2.erode(mask,kernel1,iterations=3)
#     mask=cv2.dilate(mask,kernel1,iterations=1) 
#     return mask


def maskGenerator(img,lower_color,higher_color):

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

        




