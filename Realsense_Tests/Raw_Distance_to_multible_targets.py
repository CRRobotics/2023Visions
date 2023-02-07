
from realsense_camera import *
import cv2
#load real sense camera
rs=RealsenseCamera()
import functions as f
import constants
import math
while True:
    ret, frame, depth_frame = rs.get_frame_stream()
   

 
    'CUBE'
  
    mask1 = f.maskGenerator1(frame)
    contours1=f.findContours(mask1)    
    #contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    if len(contours1) >0:
        for contour1 in contours1:
        
        
            area1=cv2.contourArea(contour1) 
            if area1>=1600:
            
                center1=f.find_center_and_draw_center_and_contour_of_target(frame,contour1)
                point_x1,point_y1=center1
                distance_cm1= depth_frame.get_distance(point_x1,point_y1)/10#y,x
                cv2.putText(frame,'{}cm,Cube'.format(distance_cm1),(point_x1,point_y1-10),0,1,(0,0,255),2)
            
    'CONE'
    mask2=f.maskGenerator2(frame,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2) 
       
    if len(contours2) >0:
        for contour2 in contours2:
       
            area2=cv2.contourArea(contour2) 
            if area2 >= 1600:
                center2=f.find_center_and_draw_center_and_contour_of_target(frame,contour2)
                point_x2,point_y2=center2
                distance_cm2= depth_frame.get_distance(point_x2,point_y2)/10#y,x
                cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
            
                
        


    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_frame, alpha=0.10), 2)
    cv2.imshow('cone',frame)
    #cv2.imshow('cone',depth_colormap) #this is the depth map colored
    cv2.waitKey(1)
   




