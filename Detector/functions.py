
import cv2
import numpy as np
import constants
import math
import threading
import math

from networktables import NetworkTables as nt
'''
def differentiateObject(depthMap,threshold,pixOffset):
    xRange=a.shape[0]
    yRange=a.shape[1]
    tempArr=np.array(shape=(xRange,yRange), dtype=bool)
    boundPix=False
    perimeter=0
    for x in range(0,xRange):
        for y in range(0,yRange):
            if depthMap[x,y]-depthMap[x,(y-pixOffset)]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[x,(y+pixOffset)]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[(x-pixOffset),y]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[(x+pixOffset),y]>threshold:
                boundPix=True
            if boundPix:
                tempArr[x,y] = True
                perimeter+=1
    return tempArr
    # return (perimeter>((xRange+yRange)))
'''     
def maskGenerator1(img):#for cube
    img=cv2.blur(img, (5,5)) 
    #img= cv2.GaussianBlur(img, (15, 15), 0)
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(b,g)
    ret, mask = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask=cv2.erode(mask,kernel1,iterations=3)
    mask=cv2.dilate(mask,kernel1,iterations=1) 
    '''
    Make a hsv double check for cubes
    '''
    return mask

def maskGenerator2(img,lower_color,higher_color):#for cone

    #bgr math
    img= cv2.GaussianBlur(img, (15, 15), 0) 
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

def getCordinatesOfTarget_Cam(x, y, depth_frame, color_frame):
    intrinsics = rs.video_stream_profile(color_frame.profile).get_intrinsics()
    point_2d = np.array([x, y]) # Example pixel position
    point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point_2d, depth_frame.get_distance(point_2d[0], point_2d[1]))
    dx,dy,dz = point_3d
    return -1*dy ,-1*dx, dz  # x is right, y is up, z is front.
    
    
def getCordinatesOfTarget_Bot(dx,dy,dz,mountAngle, camHeight):
    diagnal_dis=(dy**2+dz**2)**0.5
    small_angle=math.atan(abs(dy)/dz)
    mountAngle=math.radians(mountAngle)
    if dy <= 0:
        remain_angle=math.pi/2 - mountAngle - small_angle
    else:
        remain_angle=math.pi/2 - mountAngle + small_angle
    z = diagnal_dis * math.sin(remain_angle)
    y = camHeight - diagnal_dis * math.cos(remain_angle)
    x = dx
    return x,y,z
def correct_dis(cam_dis):
    real_dis = (1/0.359)*cam_dis - 69/0.359
    return real_dis

'''prototypes'''


'''get av coordinates of center of target, averaging the cords around it'''
def get_average_cords(center_x,center_y,dimension,depth_frame, color_frame):
    top_left_x = center_x -dimension
    top_left_y = center_x -dimension
    list_of_x=[]
    list_of_z=[]
    list_of_y=[]

    list_of_x2=[]#used to remove 0
    list_of_z2=[]
    list_of_y2=[]
    #put in values
    for a in range(0,2*dimension+1):
        for b in range(0,2*dimension+1):
            dx,dy,dz = getCordinatesOfTarget_Cam(b,a, depth_frame, color_frame)
            list_of_x.append(dx)
            list_of_z.append(dz)
            list_of_y.append(dy)

    #start remove all 0 in the list
    for i in list_of_x:
        if i != 0:
            list_of_x2.append(i)
    for i in list_of_z:
        if i !=0 :
            list_of_z2.append(i)
    for i in list_of_y:
        if i !=0 :
            list_of_y2.append(i)
    x_av = 0
    z_av =0
    y_av =0
    for i in list_of_x2:
        x_av+=i
    for i in list_of_z2:
        z_av+=i
    for i in list_of_y2:
        y_av+=i
    x_av/=len(list_of_x2)
    z_av/=len(list_of_z2)
    y_av/=len(list_of_y2)
    return x_av,y_av,z_av
'''get the point on the ground'''

def get_ground_point(frame,contour):
    cv2.drawContours(frame,[contour],0,(255,0,255),2)
    points_array=contour.tolist()
    points_tuple=[]#position of convex points
    for i in points_array:
        for c in i:
            c=tuple(c)
            points_tuple.append(c)
    biggest_y=0
    indexer=0
    for i in range(len(points_tuple)):
        x,y=points_tuple[i]
        if y >= biggest_y:
            biggest_y=y
            indexer=i
    point=points_tuple[indexer]
    cv2.circle(frame, point, 5, (0, 0, 255), -1)
    return point#position of the point with the biggest y value.
