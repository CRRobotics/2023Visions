import pyrealsense2 as rs
import cv2
import numpy as np
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

align_to = rs.stream.color
align = rs.align(align_to)

#UNCOMMENT THIS FOR NETWORKTABLES
# nt = f.networkConnect()
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
   
    '''
    Cube
    '''
    mask1 = f.maskGenerator1(color_image)
    contours1,hierarchy=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours1) >0:
        cubeX=[]
        cubeY=[]
        cubeAngle=[]
        for contour1 in contours1:
            if np.size(contour1) == 0: continue
            contour1 = cv2.convexHull(contour1)
            if cv2.contourArea(contour1) >= 1000:
                cube_ratio = f.find_target_size(contour1,color_image)
                if cube_ratio > constants.cube_min_ratio: #Change to check width/height
                    center1=f.find_center_and_draw_center_and_contour_of_target(color_image,contour1)
                    point_x1,point_y1=center1
                    
                    dx1,dy1,dz1 = f.getCordinatesOfTarget_Cam(point_x1,point_y1, depth_frame, color_frame)
                    if dz1 != 0:
                        cube_perimeter_x, cube_perimeter_y = f.find_contour_length(contour1, dz1)
                        if cube_perimeter_y >= constants.cube_min_parameter and cube_perimeter_y <= constants.cube_max_parameter:
                            cv2.drawContours(color_image,[contour1],0,(0,255,0),3)
                            x1,y1,z1=f.getCordinatesOfTarget_Bot(dx1,dy1,dz1,constants.cam_mount_angle, constants.cam_height)
                            # cv2.putText(color_image, str(int(cube_perimeter_x))+'/'+str(int(cube_perimeter_y)), (point_x1,point_y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            cv2.putText(color_image, str(int(x1*100))+'@'+str(int(z1*100)), (point_x1,point_y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)   
                            cubeX.append(x1)
                            cubeY.append(y1)   
                            cubeAngle.append(x1/z1)
        # f.pushval(nt,"Detector","cubeX",cubeX)
        # f.pushval(nt,"Detector","cubeY",cubeY)

    '''
    Cone
    '''
    coneX=[]
    coneY=[]
    mask2=f.maskGenerator2(color_image,constants.lower_yellow,constants.higher_yellow)
    contours2,hierarchy=cv2.findContours(mask2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours2) >0:
        for contour2 in contours2:
            if np.size(contour2) == 0: continue
            contour2 = cv2.convexHull(contour2)
            if cv2.contourArea(contour2) >= 1600:
                cone_ratio = f.find_target_size(contour2,color_image)
                if cone_ratio>constants.cone_min_ratio:
                    center2=f.find_center_and_draw_center_and_contour_of_target(color_image,contour2)
                    point_x2,point_y2=center2
                    # cv2.putText(color_image, str(int(cone_ratio)), (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)   
                    dx2,dy2,dz2 = f.getCordinatesOfTarget_Cam(point_x2,point_y2,depth_frame, color_frame)  
                    if dz2 != 0:
                        cone_perimeter_x, cone_perimeter_y = f.find_contour_length(contour2, dz2)
                        if cone_perimeter_y >=constants.cone_min_parameter and cone_perimeter_y <= constants.cone_max_parameter:
                            cv2.drawContours(color_image,[contour2],0,(0,255,0),3)
                            x2,y2,z2=f.getCordinatesOfTarget_Bot(dx2,dy2,dz2,constants.cam_mount_angle, constants.cam_height)
                            cv2.putText(color_image, "%.2f"%y2, (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            # cv2.putText(color_image, str(int(cone_perimeter_x))+'/'+str(int(cone_perimeter_y)), (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            cv2.putText(color_image, str(int(x2*100))+'@'+str(int(z2*100)), (point_x2,point_y2+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            coneX.append(x2)
                            coneY.append(y2)      
            # f.pushval(nt,"Detector","coneX",coneX)
            # f.pushval(nt,"Detector","coneY",coneY)

               
    b= cv2.rotate(color_image,cv2.ROTATE_90_CLOCKWISE)
   

    cv2.namedWindow("color_image", cv2.WINDOW_NORMAL)
    cv2.imshow("color_image", b)
    #set visualization frame rate
    key = cv2.waitKey(1)
    # Press esc or 'q' to close the image window
    if key & 0xFF == ord('q') or key == 27:
        cv2.destroyAllWindows()
        break
pipeline.stop()






"""
       %%%%
     % $  $ %
     % 0  0 %
  __   !__!
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