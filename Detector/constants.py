
import numpy as np



lower_yellow=np.array([0,0,0])
higher_yellow=np.array([40,255,255])

SERVER = "10.6.39.2"

cam_height=1.3 # in meters
cam_mount_angle=30# in degrees

cone_min_ratio = 50
cube_min_ratio = 75

FoV_angle_deg_x = 69
FoV_width_pix_x = 1280
FoV_angle_deg_y = 42
FoV_width_pix_y = 720

cone_min_parameter=60
cone_max_parameter=105


cube_min_parameter = 60
cube_max_parameter = 85

#Use sliders.py to adjust these values based on lighting
cube_low = 20
cube_high = 255
cone_low = 80
cone_high = 255