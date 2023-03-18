from pupil_apriltags import *
import json
import numpy as np
import math
#import matplotlib.pyplot as plt

TAG_FAMILY = "tag16h5"
MARGIN_THRESHOLD = 60
PIXEL_MARGIN = 7




ID_POS_NEW = {
    #Coordinates taken from FRC game manual
    1:{
        "center":(15.513558, 1.071626, 0.463),
    },
    2:{
        "center":(15.513558, 2.748026, 0.463),   
        # "center":(0, 0, 0),
    },
    3:{
        "center":(15.513558, 4.424426, 0.463),   
        # "center":(.5, 0, 0),

    },
    4:{
        "center":(16.178784, 6.7491796, 0.6955),   
        # "center":(-.45, 0, 0)
    },
    5:{
        "center":(0.36195, 6.7491796, 0.6955),   
        
    },
    6:{
         "center":(1.02743, 4.424426, 0.463),   
        #"center":(0,0,.505),  
    },
    7:{
        "center":(1.02743, 2.748026, 0.463),   
        #"center":(0.52, 0, 2), 
        #        "center":(0, -0.52, 0.605), 

    },
    8:{
        # "center":(7.243, 2.9365, 0.463),   
        "center":(-1.02743, 1.071626, .45),   

    }

}

# No longer used; assume origin in field center
ID_POS = {
    #Coordinates taken from field cad
    1:{
        "center":(-7.243, 2.9365, 0.463),
    },
    2:{
        "center":(-7.243, 1.26, 0.463),   
        "center":(0, 0, 0),
    },
    3:{
        "center":(-7.243, -0.416, 0.463),   
        "center":(.5, 0, 0),

    },
    4:{
        "center":(-7.908, -2.7415, 0.6955),   
        # "center":(-.45, 0, 0)
    },
    5:{
        "center":(7.908, -2.7415, 0.6955),   
        
    },
    6:{
         "center":(7.243, -0.416, 0.463),   
        #"center":(0,0,.505),  
    },
    7:{
        "center":(7.243, 1.26, 0.463),   
        #"center":(0.52, 0, 2), 
        #        "center":(0, -0.52, 0.605), 

    },
    8:{
        # "center":(7.243, 2.9365, 0.463),   
        "center":(-2.286, 0, .45),   

    }

}


CAMERA_CONSTANTS = {
    2:{
        "matrix":np.array([
  [
   1097.3387663520302,
   0.0,
   614.1053531279227
  ],
  [
   0.0,
   1090.798847106442,
   429.49732257606695
  ],
  [
   0.0,
   0.0,
   1.0
  ]
 ]),
        "distortion":np.array([
            [
  0.11689586201295843,
  -0.5199784733199033,
  -0.0004565757059130622,
  -0.008706649747024026,
  1.0476502704411934
 ]
        ]),
       "yc": 0.04445, #.34 for kitbot, .9 for duckbot
        "xc": -0.2667,
        "thetar": 57

    },
    0:{
        "matrix":np.array([
  [
   1083.4477620094715,
   0.0,
   596.9965250314739
  ],
  [
   0.0,
   1075.8310384988097,
   375.5977587966367
  ],
  [
   0.0,
   0.0,
   1.0
  ]
 ]),
        "distortion":np.array([
            [  0.08179461182110684, -0.10840459949147022, 0.006845689130575109, -0.017401488019492567, 0.04539104217020666]
        ]),
       "yc": -0.04445,
        "xc": -0.2667,
        "thetar": -57
    },
    4:{
        "matrix":np.array([
  [
   850.1221797947615,
   0.0,
   622.2669226954358
  ],
  [
   0.0,
   847.7951726554022,
   419.00219595660406
  ],
  [
   0.0,
   0.0,
   1.0
  ]
 ]),
        "distortion":np.array([
            [
  -0.37687332840173615,
  0.19130262760331465,
  -0.002466252816929792,
  -0.0010478623272106558,
  -0.05808206518422606
 ]
        ]),
        "yc": 0.3175,
        "xc": .2667, #.145 for kitbot, -.105 for duckbot
        "thetar": 0
    }
}

# GET_CORNERS_MAT = np.array(
#     [[-0.0762, -0.0762, 0.0],
#     [0.0762, -0.0762, 0.0],
#     [0.0762, 0.0762, 0.0],
#     [-0.0762, 0.0762, 0.0]]
# )


# GET_CORNERS_MAT_OTHER_WAY = np.array(
#     [
#     [0.0762, -0.0762, 0.0],
#     [-0.0762, -0.0762, 0.0],
#     [-0.0762, 0.0762, 0.0],
#     [0.0762, 0.0762, 0.0],
#     ]

# )


CORNERS_AS_IN_FIELD = np.array(
    [[0.0, 0.0762, -0.0762],
    [0.0, -0.0762, -0.0762],
    [0.0, -0.0762, 0.0762],
    [0.0, 0.0762, 0.0762]]
)

CORNERS_AS_IN_FIELD_MAT_OTHER_WAY = np.array(
    [
    [0.0, -0.0762, -0.0762],
    [0.0, 0.0762, -0.0762],
    [0.0, 0.0762, 0.0762],
    [0.0, -0.0762, 0.0762],
    ]

)

# FIG = plt.figure(figsize=(30,8))
# RX_LOG = []
# RY_LOG = []
# RT_LOG = []

SERVER = "10.6.39.2"
