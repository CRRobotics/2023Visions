import pyrealsense2 as rs
import cv2
import numpy as np
import math
from dataclasses import dataclass
import functions as f
import constants

@dataclass
class cconfig:
    width: int
    height: int
    fr: int         # framerate
    
colorcfg = cconfig(width = 1280, height = 720, fr = 15)
depthcfg = cconfig(width = 848, height = 480, fr = 15)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, depthcfg.width, depthcfg.height, rs.format.z16, depthcfg.fr)
config.enable_stream(rs.stream.color, colorcfg.width, colorcfg.height, rs.format.bgr8, colorcfg.fr)
pipeline.start(config)

align_to = rs.stream.depth
align = rs.align(align_to)

# nt = f.networkConnect()
while True:
    # This call waits until a new coherent set of frames is available on a device
    frames = pipeline.wait_for_frames()
    
    #Aligning color frame to depth frame
    aligned_frames =  align.process(frames)
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not depth_frame or not color_frame: continue

    
    color_image = np.asanyarray(color_frame.get_data())
    

    
    '''
    Cube
    '''

    mask1 = f.maskGenerator1(color_image)
    contours1=f.findContours(mask1)    
    #contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    if len(contours1) >0:
        for contour1 in contours1:
            area1=cv2.contourArea(contour1) 
            if area1>=1600:
                center1=f.find_center_and_draw_center_and_contour_of_target(color_image,contour1)

                point_x1,point_y1=center1
            
                dx1,dy1,dz1 = f.getCordinatesOfTarget_Cam(point_x1,point_y1, depth_frame, color_frame)
                if dz1 != 0:
                    x1,y1,z1=f.getCordinatesOfTarget_Bot(dx1,dy1,dz1,constants.cam_mount_angle, constants.cam_height)
                    cv2.putText(color_image, str(int(x1*100))+'@'+str(int(z1*100)), (point_x1,point_y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
             


             
            
    '''
    Cone
    '''
    mask2=f.maskGenerator2(color_image,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2)    
    if len(contours2) >0:
        for contour2 in contours2:
            area2=cv2.contourArea(contour2) 
            if area2 >= 1600:
                center2=f.find_center_and_draw_center_and_contour_of_target(color_image,contour2)

                width, height = f.find_target_size(contour2,depth_frame,color_frame,color_image)
                point_x2,point_y2=center2
                cv2.putText(color_image, str(int(width))+'@'+str(int(height)), (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                dx2,dy2,dz2 = f.getCordinatesOfTarget_Cam(point_x2,point_y2, depth_frame, color_frame)
                #dx2,dy2,dz2 = f.get_average_cords(point_x2,point_y2,5,depth_frame, color_frame)

        
            
                    
                if dz2 != 0:
                    x2,y2,z2=f.getCordinatesOfTarget_Bot(dx2,dy2,dz2,constants.cam_mount_angle, constants.cam_height)
                    # cv2.putText(color_image, str(int(dx2*100))+'@'+str(int(dz2*100)), (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                


               
    b= cv2.rotate(color_image,cv2.ROTATE_90_CLOCKWISE)
   

    cv2.namedWindow("color_image", cv2.WINDOW_NORMAL)
    cv2.imshow("color_image", b)
    key = cv2.waitKey(1)
    # Press esc or 'q' to close the image window
    if key & 0xFF == ord('q') or key == 27:
        cv2.destroyAllWindows()
        break
pipeline.stop()






