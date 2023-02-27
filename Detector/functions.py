
import cv2
import numpy as np
import constants
import math
import threading
import math
import pyrealsense2 as rs

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
    top_left_y = center_y -dimension
    list_of_x=[]
    list_of_z=[]
    list_of_y=[]

    list_of_x2=[]#used to remove 0
    list_of_z2=[]
    list_of_y2=[]
    #put in values
    for a in range(0,2*dimension+1):
        for b in range(0,2*dimension+1):
            dx,dy,dz = getCordinatesOfTarget_Cam(top_left_x+b,top_left_y+a, depth_frame, color_frame)
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
'''convert an np 2d array into a list of tuples, represent contour points'''
def convert_contours_to_points(contour): 
    points_array=contour.tolist()
    points_tuple=[]#position of convex points
    for i in points_array:
        for c in i:
            c=tuple(c)
            points_tuple.append(c)
    return points_tuple
'''get the point on the ground'''
def get_left_point(frame,contour):

    
    points_tuple=convert_contours_to_points(contour)#position of convex points
    
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

def get_right_point(frame,contour):

    points_tuple=convert_contours_to_points(contour)
    smallest_y=9999
    indexer=0
    for i in range(len(points_tuple)):
        x,y=points_tuple[i]
        if y <= smallest_y:
            smallest_y=y
            indexer=i
    point=points_tuple[indexer]
    cv2.circle(frame, point, 5, (0, 0, 255), -1)
    return point#position of the point with the biggest y value.

def get_top_point(frame,contour):
  
    points_tuple=convert_contours_to_points(contour)
    smallest_x=9999
    indexer=0
    for i in range(len(points_tuple)):
        x,y=points_tuple[i]
        if x <= smallest_x:
            smallest_x=x
            indexer=i
    point=points_tuple[indexer]
    cv2.circle(frame, point, 5, (0, 0, 255), -1)
    return point#position of the point with the biggest y value.
def get_ground_point(frame,contour):
  
    points_tuple=convert_contours_to_points(contour)
    biggest_x=0
    indexer=0
    for i in range(len(points_tuple)):
        x,y=points_tuple[i]
        if x >= biggest_x:
            biggest_x=x
            indexer=i
    point=points_tuple[indexer]
    cv2.circle(frame, point, 5, (255, 0, 0), -1)
    return point#position of the point with the biggest y value.

def find_target_size(contour,depth_frame,color_frame,color_image):
    up_point = get_top_point(color_image,contour)
    down_point= get_ground_point(color_image,contour)
    left_point = get_left_point(color_image,contour)
    right_point  =get_right_point(color_image,contour)
    x1,y1 = up_point 
    x2,y2 = down_point
    x3,y3 = left_point
    x4,y4 = right_point 
    def getCordinatesOfTarget_Cam_neglect_0(x, y, depth_frame, color_frame,a):
        #0,up; 1,down, 2,left, 3 right
        #top right is (0,0)
        #x, down, increase
        #y,left, increase
        cords = 0
        while True:
            cords_raw = getCordinatesOfTarget_Cam(x, y, depth_frame, color_frame)
            x_raw,y_raw,z_raw = cords_raw
            if z_raw == 0:
                if a == 0:
                    x+=1
                if a == 1:
                    x -=1
                if a == 2:
                    y -=1
                if a == 3:
                    y+=1
            else:
                cords = cords_raw
                break
       
        return cords


        
    x_up,y_up,z_up = getCordinatesOfTarget_Cam_neglect_0(x1, y1, depth_frame, color_frame,0)
    x_down,y_down,z_down = getCordinatesOfTarget_Cam_neglect_0(x2, y2, depth_frame, color_frame,1)
    x_left,y_left,z_left = getCordinatesOfTarget_Cam_neglect_0(x3, y3, depth_frame, color_frame,2)
    x_right,y_right,z_right = getCordinatesOfTarget_Cam_neglect_0(x4, y4, depth_frame, color_frame,3)
    
    up_down = (abs(y_up) + abs(y_down))*100
    left_right = (abs(x_right) + abs(x_left))*100
    return up_down,left_right
    