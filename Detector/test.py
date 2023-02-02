
from realsense_camera import *
import cv2
#load real sense camera

rs=RealsenseCamera()

while True:
    ret, frame, depth_frame = rs.get_frame_stream()
    cv2.imshow('sfd',frame)
    cv2.waitkey(1)
   





