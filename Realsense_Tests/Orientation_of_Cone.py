
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
   
    '''Cone'''
    mask2=f.maskGenerator2(frame,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2) 
    if len(contours2) >0:
        biggest_contour2=f.find_biggest_contour(contours2)
        area2=cv2.contourArea(biggest_contour2) 
        if area2 >= 1600:
            center2=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
            point_x2,point_y2=center2
            #cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
            epsilon = 0.1 * cv2.arcLength(biggest_contour2, True)
            approx = cv2.approxPolyDP(biggest_contour2, epsilon, True)
            cv2.polylines(frame, [approx], True, (0, 255, 0), 6)
            cv2.putText(frame,str(len(approx)),(point_x2,point_y2-40),0,1,(255,0,0),2)
        
            points_array=approx.tolist()
            points_tuple=[]#position of the three major points
            for i in points_array:
                for c in i:
                    c=tuple(c)
                    points_tuple.append(c)
            target_point = f.smallest_angle_vertex(points_tuple)
            cv2.arrowedLine(frame, center2, target_point,(255,0,0), 9) 
            x_final,y_final=target_point#point_x2,point_y2=center2
            #difine a lower point
            dis_center_to_target=((point_x2-x_final)**2+(point_y2-y_final)**2)**(1/2)
            lower_x=point_x2
            lower_y=point_y2-dis_center_to_target
            dis_target_to_lower=((lower_x-x_final)**2+(lower_y-y_final)**2)**(1/2)
            angle_final=math.acos(((dis_center_to_target)**2+(dis_center_to_target)**2-(dis_target_to_lower)**2)/(2*(dis_center_to_target)*(dis_center_to_target)))
            if x_final<point_x2:
                angle_final=(-1)*angle_final
            # cv2.arrowedLine(frame, center2, (lower_x,lower_y),(0,0,255), 9) 
            f.pushval(nt, 'Detector', "coneAngle", angle_final)
            cv2.putText(frame,str(math.degrees(angle_final)),(point_x2,point_y2-10),0,1,(255,0,0),2)
    cv2.imshow('cone',frame)
   
    cv2.waitKey(1)


                    



