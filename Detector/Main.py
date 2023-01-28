
from realsense_camera import *
import cv2
#load real sense camera
rs=RealsenseCamera()
import functions as f
import constants
while True:
    ret, frame, depth_frame = rs.get_frame_stream()
   
    
    



 
    'CUBE'
    mask1 = f.maskGenerator1(frame, constants.lower_purple, constants.higher_purple)
    contours1=f.findContours(mask1)    
    contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    if len(contours1) >0:
        biggest_contour1=f.find_biggest_contour(contours1)
        center1=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour1)
        point_x1,point_y1=center1
        distance_cm1= depth_frame[point_y1,point_x1]/10#y,x
        cv2.putText(frame,'{}cm,Cube'.format(distance_cm1),(point_x1,point_y1-10),0,1,(0,0,255),2)

 
    'CONE'
    mask2=f.maskGenerator2(frame)
    contours2=f.findContours(mask2)     
    if len(contours2) >0:
        biggest_contour2=f.find_biggest_contour(contours2)
        center2=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
        point_x2,point_y2=center2
        distance_cm2= depth_frame[point_y2,point_x2]/10#y,x
        cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
        y=point_y2-360
        x=point_x2-720
        d=distance_cm2
        # f.heightFromDistance(frame,y,d)
        height=95
        # cameraMountAngle=1.134
        # pixleToDegree=0.00103
        # angle=pixleToDegree*y-cameraMountAngle
        
        b=f.getDirectDistanceToPixel(x,y,d)
        cv2.putText(frame,"distance to bot"+str(b)+'cm',(200,400),0,1,(0,0,255),2)
        # angleToTurn=(point_x2-720)*0.000946
        # cv2.putText(frame,'angle to turn'+str(angleToTurn*180/3.1415926)+'degrees',(200,600),0,1,(0,0,255),2)


        



    #cv2.imshow('BGr',mask2)
    cv2.imshow('BGr',frame)
    cv2.waitKey(1)
   
    #print depth_frame, it shows the depth of each pix in mm
# rs.release()
# cv2.destroyAllWindows()
