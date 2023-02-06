
from realsense_camera import *
import cv2
#load real sense camera
rs=RealsenseCamera()
import functions as f
import constants
import math
nt = f.networkConnect()
while True:
    ret, frame, depth_frame = rs.get_frame_stream()
   

 
    'CUBE'
  
    mask1 = f.maskGenerator1(frame)
    contours1=f.findContours(mask1)    
    contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    if len(contours1) >0:
        biggest_contour1=f.find_biggest_contour(contours1)
        area1=cv2.contourArea(biggest_contour1) 
        if area1>=1600:
            center1=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour1)
            point_x1,point_y1=center1
            distance_cm1= depth_frame[point_y1,point_x1]/10#y,x
            distance1,angle1=f.get_distance_and_angle(constants.cam_height,distance_cm1,point_x1,point_y1)
            angle1=math.radians(angle1)


            f.pushval(nt,'Detector' , "cubeDiatance", distance1)
            f.pushval(nt,'Detector' , "cubeAngle", angle1)


            print('{}cm,Cube'.format(distance_cm1),'distance to bot:',distance1,'angle:',angle1)

        
    'CONE'
    mask2=f.maskGenerator2(frame,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2)     
    if len(contours2) >0:
        biggest_contour2=f.find_biggest_contour(contours2)
        area2=cv2.contourArea(biggest_contour2) 
        if area2>=1600:
            center2=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
            point_x2,point_y2=center2
            distance_cm2= depth_frame[point_y2,point_x2]/10#y,x
            distance2,angle2=f.get_distance_and_angle(constants.cam_height,distance_cm2,point_x2,point_y2)
            angle2=math.radians(angle2)
            trigDistance = getTrigDistanceFromPixel(360-point_y2,distance2)

            f.pushval(nt, 'Detector', "coneDistance", trigDistance)
            f.pushval(nt, 'Detector', "coneAngle", angle2)


            print('{}cm,Cone'.format(distance_cm2),'distance to bot:',distance2,'angle:',angle2)
    cv2.imshow('sdf',frame)
    cv2.waitKey(1)
   




