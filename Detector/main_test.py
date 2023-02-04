
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
    contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    if len(contours1) >0:
        biggest_contour1=f.find_biggest_contour(contours1)
        area1=cv2.contourArea(biggest_contour1) 
        if area1>=1600:
            center1=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour1)
            point_x1,point_y1=center1
            distance_cm1= depth_frame[point_y1,point_x1]/10#y,x
            distance1,angle1=f.get_distance_and_angle(constants.cam_height,distance_cm1,point_x1,point_y1)
            cv2.putText(frame,'distance'+str(distance1)+'cm',(point_x1,point_y1-10),0,1,(0,0,255),2)
            cv2.putText(frame,'angle'+str(math.degrees((angle1)))+'degree',(point_x1,point_y1+20),0,1,(0,0,255),2)   

            

        
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
      
            cv2.putText(frame,'distance'+str(distance2)+'cm',(point_x2,point_y2-10),0,1,(0,0,255),2)
            cv2.putText(frame,'angle'+str(math.degrees(angle2))+'degree',(point_x2,point_y2+20),0,1,(0,0,255),2)



          

            
    cv2.imshow('sdf',frame)
    cv2.waitKey(1)
   




