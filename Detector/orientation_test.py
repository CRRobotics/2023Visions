
from realsense_camera import *
import cv2
#load real sense camera
rs=RealsenseCamera()
import functions as f
import constants
import math
while True:
    ret, frame, depth_frame = rs.get_frame_stream()
   
    mask2=f.maskGenerator2(frame,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2) 
       
    if len(contours2) >0:
        biggest_contour2=f.find_biggest_contour(contours2)
        area2=cv2.contourArea(biggest_contour2) 
        if area2 >= 1600:
            center2=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
            point_x2,point_y2=center2
            distance_cm2= depth_frame[point_y2,point_x2]/10#y,x
            #cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)
            approx = cv2.approxPolyDP(biggest_contour2, 300, True)
            #cv2.polylines(frame, [approx], True, (0, 255, 255), 2)

           # cv2.putText(frame,str(len(approx)),(point_x2,point_y2-40),0,1,(255,0,0),2)
            if len(approx)==3:
                points_array=approx.tolist()
                points_tuple=[]#position of the three major points
                for i in points_array:
                    for c in i:
                        c=tuple(c)
                        points_tuple.append(c)
                point_a=points_tuple[0]
                xa,ya=point_a
                point_b=points_tuple[1]
                xb,yb=point_b
                point_c=points_tuple[2]
                xc,yc=point_c
                ab=((yb-ya)**2+(xb-xa)**2)**(1/2)
                ac=((yc-ya)**2+(xc-xa)**2)**(1/2)
                bc=((yc-yb)**2+(xc-xb)**2)**(1/2)
                angle_a=math.degrees(math.acos(((ab)**2+(ac)**2-(bc)**2)/(2*(ab)*(ac))))
                angle_b=math.degrees(math.acos(((bc)**2+(ab)**2-(ac)**2)/(2*(bc)*(ab))))
                angle_c=math.degrees(math.acos(((bc)**2+(ac)**2-(ab)**2)/(2*(bc)*(ac))))
                lister=[]
                lister.append(angle_a)
                lister.append(angle_b)
                lister.append(angle_c)
                min=500
                indexer=0
                for i in range(3):
                    angle=lister[i]
                    if angle <= min:
                        min = angle
                        indexer=i
                target_point=points_tuple[indexer]
                cv2.arrowedLine(frame, center2, target_point,(0,255,0), 9) 
                x_final,y_final=target_point#point_x2,point_y2=center2
                #difine a lower point
                dis_center_to_target=((point_x2-x_final)**2+(point_y2-y_final)**2)**(1/2)
                lower_x=point_x2
                lower_y=point_y2-dis_center_to_target
                dis_target_to_lower=((lower_x-x_final)**2+(lower_y-y_final)**2)**(1/2)
                angle_final=math.degrees(math.acos(((dis_center_to_target)**2+(dis_center_to_target)**2-(dis_target_to_lower)**2)/(2*(dis_center_to_target)*(dis_center_to_target))))
                if x_final<point_x2:
                    angle_final=(-1)*angle_final
                # cv2.arrowedLine(frame, center2, (lower_x,lower_y),(0,0,255), 9) 
                cv2.putText(frame,str(angle_final),(point_x2,point_y2-10),0,1,(255,0,0),2)
    cv2.imshow('cone',frame)
   
    cv2.waitKey(1)


                    



