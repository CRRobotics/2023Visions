import pyrealsense2 as rs
import cv2
import numpy as np
import math
from dataclasses import dataclass
import functions as f
import constants
counter=0
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

while True:
    # This call waits until a new coherent set of frames is available on a device
    frames = pipeline.wait_for_frames()
    
    #Aligning color frame to depth frame
    aligned_frames =  align.process(frames)
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    # depth_frame=f.fill_holes(depth_frame)
    if not depth_frame or not color_frame: continue
    color_image = np.asanyarray(color_frame.get_data())  
    
  
    mask2=f.maskGenerator2(color_image,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2)    
    if len(contours2) >0:
        for contour2 in contours2:
            
       
            if cv2.contourArea(contour2) >= 1000:
                # cone_width, cone_height = f.find_target_size(contour2,depth_frame,color_frame,color_image)



                key = cv2.waitKey(1)
                # Press esc or 'q' to close the image window
                if key == ord('q'):
                    
                    imageName = 'image_' + str(counter) + '.jpg'
                    cv2.imwrite(imageName, color_image)
                    depth_frame = np.asanyarray(depth_frame.get_data())     
                    depth_frame_name = 'depth_frame'+str(counter)
                    np.save(depth_frame_name, depth_frame)
                    contourname='contour'+str(counter)
                    np.save(contourname,contour2)
                    counter+=1
                cv2.drawContours(color_image,[contour2],0,(255,0,255),3)



        
            # conex,coney,conew,coneh=cv2.boundingRect(contour2)
            # ratio2=float(coneh)/conew
            
            #judges the target's actuall size
            #if (width>= 10 and width <= 50 and height >=15 and height <= 30) : #or (width>= 20 and width <= 40 and height >=10 and height <= 30):
                #2 conditions for up and knocked down cone
                # center2=f.find_center_and_draw_center_and_contour_of_target(color_image,contour2)
                # point_x2,point_y2=center2
                # #cv2.putText(color_image, str(cone_width), (point_x2,point_y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)   
                # dx2,dy2,dz2 = f.get_average_cords(point_x2,point_y2,15,depth_frame, color_frame)  
                # if dz2 != 0:
                #     x2,y2,z2=f.getCordinatesOfTarget_Bot(dx2,dy2,dz2,constants.cam_mount_angle, constants.cam_height)
                #     cv2.putText(color_image, str(int(x2*100))+'@'+str(int(z2*100)), (point_x2,point_y2+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
       

               
    b= cv2.rotate(color_image,cv2.ROTATE_90_CLOCKWISE)
   

    # cv2.namedWindow("color_image", cv2.WINDOW_NORMAL)
    cv2.imshow("color_image", b)
    #set visualization frame rate








