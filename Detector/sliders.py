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
    

colorcfg = cconfig(width = 1280, height = 720, fr = 30)
depthcfg = cconfig(width = 848, height = 480, fr = 30)
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



#trackbar callback fucntion to update HSV value
def callback(x):
    global cube_low,cube_high,cone_low,cone_high
    #assign trackbar position value to H,S,V High and low variable
    cube_low = cv2.getTrackbarPos('cube_low','controls')
    cube_high = cv2.getTrackbarPos('cube_high','controls')
    cone_low = cv2.getTrackbarPos('cone_low','controls')
    cone_high = cv2.getTrackbarPos('cone_high','controls')



#create a seperate window named 'controls' for trackbar
cv2.namedWindow('controls',2)
cv2.resizeWindow("controls", 550,10)


#global variable
cube_low = 0
cube_high = 255
cone_low = 0
cone_high = 255

#create trackbars for high,low H,S,V 
cv2.createTrackbar('cube_low','controls',0,255,callback)
cv2.createTrackbar('cube_high','controls',0,255,callback)

cv2.createTrackbar('cone_low','controls',0,255,callback)
cv2.createTrackbar('cone_high','controls',0,255,callback)

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
    

    




    color_image=cv2.blur(color_image, (5,5)) 
    #color_image= cv2.GaussianBlur(color_image, (15, 15), 0)
    b,g,r=cv2.split(color_image)     
    diff1 = cv2.subtract(b,g)
    _, mask1 = cv2.threshold(diff1, cube_low, cube_high, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask1=cv2.erode(mask1,kernel1,iterations=3)
    mask1=cv2.dilate(mask1,kernel1,iterations=1) 


    diff2 = cv2.subtract(g, b)
    _, maska = cv2.threshold(diff2, cone_low, cone_high, cv2.THRESH_BINARY)

    maska=cv2.erode(maska,kernel1,iterations=3)
    maska=cv2.dilate(maska,kernel1,iterations=1) 

    #hsv double check
    color_image_hsv=cv2.cvtColor(color_image,cv2.COLOR_BGR2HSV)
    lower_color=np.array([0,0,0])
    higher_color=np.array([40,255,255])
    maskb=cv2.inRange(color_image_hsv,lower_color,higher_color)    
    maskb=cv2.erode(maskb,kernel1,iterations=3)
    maskb=cv2.dilate(maskb,kernel1,iterations=1)
    maskab = cv2.bitwise_and(maska, maskb)

    kernel2 = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]], np.uint8)
    maskab = cv2.dilate(maskab,kernel2, iterations = 3)
    mask2 = maskab

    




    

    


    #waitfor the user to press escape and break the while loop 
    f.show_image("color_image",color_image)
    f.show_image("cube",mask1)
    f.show_image("cone",mask2)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q') or key == 27:
        cv2.destroyAllWindows()
        break
        
#destroys all window
cv2.destroyAllWindows()