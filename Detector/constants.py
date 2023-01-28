#HSV values for yellow and purple
import numpy as np
lower_yellow=np.array([19,110,100])
higher_yellow=np.array([29,255,255])
lower_purple=np.array([111,47,101])
higher_purple=np.array([133,225,250])


#determin radians per pixle

horizontal_fov=1.5001               #in rad
vertical_fov=0.9948376736
horizontal_pixle_num=1280
vertical_pixle_num=720
horizontal_rad_per_pixle=0.00117264307
vertical_rad_per_pixle=0.00138171897
#height in CM
height = 96
cameraMountAngle = 65
focal_length=1080  # mm