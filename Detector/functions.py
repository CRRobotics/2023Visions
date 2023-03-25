
import cv2
import numpy as np
import constants
import math
import threading
import math
import pyrealsense2 as rs
import csv

from networktables import NetworkTables as nt
def pushval(networkinstance, tablename:str, valuename, value):
    if networkinstance == None:
        # print(valuename, ": ", value)
        #UNCOMMENT WHEN USING MINI PC
        logStuff([valuename] + value)
        return
    table = networkinstance.getTable(tablename)
    table.putNumberArray(valuename, value)

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



def maskGenerator1(img):#for cube
    img=cv2.blur(img, (5,5)) 
    #img= cv2.GaussianBlur(img, (15, 15), 0)
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(b,g)
    _, mask = cv2.threshold(diff, constants.cube_low, constants.cube_high, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask=cv2.erode(mask,kernel1,iterations=3)
    mask=cv2.dilate(mask,kernel1,iterations=1) 
    return mask

def maskGenerator2(img,lower_color,higher_color):#for cone

    #bgr math
    img= cv2.GaussianBlur(img, (15, 15), 0) 
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(g, b)
    _, maska = cv2.threshold(diff, constants.cone_low, constants.cone_high, cv2.THRESH_BINARY)
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

def have_countours(contours):
    if len(contours) >0:
        return True
    return False

def findContours(mask):
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours=[cv2.convexHull(contour) for contour in contours]
    return contours

def if_contour_big_enough(contour):
    if cv2.contourArea(contour) >= 1600:
        return True
    return False


def find_biggest_contour(contours):
    sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
    biggest_contour=sortedContours[0]
    return biggest_contour

    
def find_contour_center(contour):
    #cv2.drawContours(frame,[biggest_contour],0,(0,255,0),3)
    moments = cv2.moments(contour)
    if moments['m00'] !=0:
        center=((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
        return center
    else:
        return (0,0)
def getCordinatesOfTarget_Cam(x, y, depth_frame, color_frame):
    intrinsics = rs.video_stream_profile(color_frame.profile).get_intrinsics()
    
    point_2d = np.array([x, y]) # Example pixel position
    depth_frame= depth_frame.as_depth_frame()
    distance =  depth_frame.get_distance(point_2d[0], point_2d[1])
    point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point_2d,distance)
    dx,dy,dz = point_3d

    #from camera perspective, dx points right, dy points down, dz points forward

    # return dy,dx,dz               # for vertical mount usb port pointing up
    # return -dy, -dx, dz         # for vertical mount usb port pointing down
    return dx,-dy,dz            # for horizontal mount, screw pointing down
    # return -dx,dy,dz            # for horizontal mount, screw pointing up
def correct_coordinate(input_coordinate):
    input_coordinate*=100
    real_coordinate = (input_coordinate+8.31)/1.0447
    return real_coordinate/100 
    
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
    x=correct_coordinate(x)
    y=correct_coordinate(y)
    z=correct_coordinate(z)
    return x,y,z


'''prototypes'''



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

def fill_holes(depth_frame):
    spatial_filter = rs.spatial_filter()
    spatial_filter.set_option(rs.option.filter_magnitude, 5) # set filter magnitude to maximum (5)
    spatial_filter.set_option(rs.option.filter_smooth_alpha, 1.0) # set smooth alpha to maximum (1.0)
    spatial_filter.set_option(rs.option.filter_smooth_delta, 10) # set smooth delta to maximum (1000)
    spatial_filter.set_option(rs.option.holes_fill, 1) # enable hole-filling
    depth_frame = spatial_filter.process(depth_frame)
    hole_filling = rs.hole_filling_filter()
    hole_filling.set_option(rs.option.holes_fill,2) # set hole-filling radius to maximum (2)
    depth_frame = hole_filling.process(depth_frame)
    return depth_frame

def find_contour_aspect_ratio(contour,color_image):
    
    box= cv2.minAreaRect(contour)
    points = cv2.boxPoints(box)
    asint = np.int0(points)
    
    if len(asint) > 0:
        # cv2.drawContours(color_image,[asint],0,(0,0,255),2)
        center, dimensions, angle= cv2.minAreaRect(contour)
        width,height = dimensions
        
        ratio = height/width
        if ratio > 1: ratio = width/height
        return ratio*100
    return 0

def find_contour_length(contour, distance):
    contour_length = cv2.arcLength(contour,True)

    # Assuming that the distance of the center pixel is the same as the pixels of the contour:
    # Get actual perimeter of contour based on angle per pixel in the x direction
    # rad_per_pix_x = math.radians(constants.FoV_angle_deg_x)/constants.FoV_width_pix_x
    # real_dist_pix_x = distance * math.sin(rad_per_pix_x)
    # real_length_x = real_dist_pix_x * contour_length

    # Same as above, but using y direction
    rad_per_pix_y = math.radians(constants.FoV_angle_deg_y)/constants.FoV_width_pix_y
    real_dist_pix_y = distance * math.sin(rad_per_pix_y)
    real_length_y = real_dist_pix_y * contour_length

    return real_length_y*100

def find_and_push_closest(nt, object_type, object_x, object_y, object_z):
    if len(object_z) == 0:
        pushval(nt, "Detector", object_type, [0.0, 0.0, 0.0, 0.0])
        return
    
    min_dist = 639
    min_index = 639
    for i in range(len(object_z)):
        x = object_x[i]
        y = object_y[i]
        z = object_z[i]
        dist = math.sqrt(x**2 + z**2)
        if dist < min_dist:
            min_dist = dist
            min_index = i
    
    pushval(nt, "Detector", object_type, [1, object_x[min_index], object_y[min_index], object_z[min_index]])

def logStuff(listToLog):
    with open("/home/crr/2023Visions/Detector/log.csv", "a+", newline="") as log:
        c = csv.writer(log)
        c.writerow(listToLog)

def show_image(window_name,img_to_show):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, img_to_show)

def format_num(num):
    formatted_num = "{:.1f}".format(num)
    return formatted_num  #returns a string

def putText(img,text,position,color):
    cv2.putText(img, text,position, cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)