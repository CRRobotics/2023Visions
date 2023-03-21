import pyrealsense2 as rs
import cv2
import numpy as np
from dataclasses import dataclass
import functions as f
import constants
import sys

import time

@dataclass
class cconfig:
    width: int
    height: int
    fr: int         # framerate
    

colorcfg = cconfig(width = 1280, height = 720, fr = 10)
depthcfg = cconfig(width = 848, height = 480, fr = 10)
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, depthcfg.width, depthcfg.height, rs.format.z16, depthcfg.fr)
config.enable_stream(rs.stream.color, colorcfg.width, colorcfg.height, rs.format.bgr8, colorcfg.fr)

#below is used to try to boot up the camera if sth is wrong
##################
connected = False
tries_left = 180

while not connected and tries_left > 0:
    try:
        pipeline.start(config)
        connected = True
    except:
        print(f"Could not connect to camera. {tries_left-1} tries left.")
        tries_left -= 1
        time.sleep(1)

if not connected:
    print("Could not connect to camera after 10 tries. Exiting.")
    sys.exit()
################
align_to = rs.stream.color
align = rs.align(align_to)

#UNCOMMENT THIS FOR NETWORKTABLES
nt =f.networkConnect()


while True:
    # This call waits until a new coherent set of frames is available on a device
    frames = pipeline.wait_for_frames()
    
    #Aligning color frame to depth frame
    aligned_frames =  align.process(frames)
    depth_frame = f.fill_holes(aligned_frames.get_depth_frame())
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()

    if not depth_frame or not color_frame: continue
    color_image = np.asanyarray(color_frame.get_data())  
    color_image= cv2.rotate(color_image,cv2.ROTATE_90_COUNTERCLOCKWISE)


    '''
    Cube
    '''
    cubeX=[]
    cubeY=[]
    cubeZ=[]
    mask1 = f.maskGenerator1(color_image)
    contours1=f.findContours(mask1)
    has_contours_cube = f.have_countours(contours1)
    if has_contours_cube:
        for contour1 in contours1:
            contour1_big_enough = f.if_contour_big_enough(contour1)
            if contour1_big_enough:
                cube_ratio = f.find_contour_aspect_ratio(contour1,color_image)
                if cube_ratio > constants.cube_min_ratio: 
                    center1=f.find_contour_center(contour1)
                    point_x1,point_y1=center1
                    dx1,dy1,dz1 = f.getCordinatesOfTarget_Cam(point_x1,point_y1, depth_frame, color_frame)
                    if dz1 != 0:
                        cube_perimeter= f.find_contour_length(contour1, dz1)
                        if cube_perimeter >= constants.cube_min_parameter and cube_perimeter <= constants.cube_max_parameter:
                            cv2.drawContours(color_image,[contour1],0,(0,255,0),6)
                            cv2.circle(color_image, center1, 3, (0, 0, 255), -1)
                            x1,y1,z1=f.getCordinatesOfTarget_Bot(dx1,dy1,dz1,constants.cam_mount_angle, constants.cam_height)
                            cubeX.append(x1)
                            cubeY.append(y1)
                            cubeZ.append(z1)
                            x1_visualize = f.format_num(x1*100)
                            z1_visualize = f.format_num(z1_visualize*100)
                            f.putText(color_image,x1_visualize,(point_x1,point_y1+5),(0,0,255))
                            f.putText(color_image,z1_visualize,(point_x1,point_y1-5),(255,0,0))
    f.find_and_push_closest(nt, "Cube", cubeX, cubeY, cubeZ)

    
    '''
    Cone
    '''
    coneX=[]
    coneY=[]
    coneZ=[]
    mask2=f.maskGenerator2(color_image,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2)
    has_contours_cone = f.have_countours(contours2)
    if has_contours_cone:
        for contour2 in contours2:
            contour2_big_enough = f.if_contour_big_enough(contour2)
            if contour2_big_enough:
                cone_ratio = f.find_contour_aspect_ratio(contour2,color_image)
                if cone_ratio>constants.cone_min_ratio:
                    center2=f.find_contour_center(contour2)
                    point_x2,point_y2=center2
                    dx2,dy2,dz2 = f.getCordinatesOfTarget_Cam(point_x2,point_y2,depth_frame, color_frame)  
                    if dz2 != 0:
                        cone_perimeter = f.find_contour_length(contour2, dz2)
                        if cone_perimeter >=constants.cone_min_parameter and cone_perimeter <= constants.cone_max_parameter:
                            cv2.drawContours(color_image,[contour2],0,(0,255,0),6)
                            cv2.circle(color_image, center2, 3, (0, 0, 255), -1)
                            x2,y2,z2=f.getCordinatesOfTarget_Bot(dx2,dy2,dz2,constants.cam_mount_angle, constants.cam_height)
                            coneX.append(x2)
                            coneY.append(y2)
                            coneZ.append(z2)
                            x2_visualize = f.format_num(x2*100)
                            z2_visualize = f.format_num(z2_visualize*100)
                            f.putText(color_image,x2_visualize,(point_x2,point_y2+5),(0,0,255))
                            f.putText(color_image,z2_visualize,(point_x2,point_y2-5),(255,0,0))
    f.find_and_push_closest(nt, "Cone", coneX, coneY, coneZ)




    if not "-h" in sys.argv:
        f.show_image("color_image",color_image)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q') or key == 27:
        cv2.destroyAllWindows()
        break







"""
       %%%%
     % %  % %
     % ^  ^ %
  __ % \__/ %
    |   ||
    |___||___
       ||||  |
       ||||  |___
        ||
    ____][_____
    |         |
    |         |
   _|         |_
    
"""