from pupil_apriltags import *
import json
import numpy as np



TAG_FAMILY = "tag16h5"


DETECTOR = Detector(
    families=TAG_FAMILY,
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
    )



with open("positioning/cameraconstants.json") as f:
    data = json.load(f)
    CAMERA_MATRIX = np.array(data["matrix"])
    CAMERA_DIST = np.array(data["distortion"])



ID_POS = {
    #Coordinates taken from field cad
    1:{
        # "center":(-7.243, 2.9365, 0.463),
        "center":(0, 0, 0),
    },
    2:{
        "center":(-7.243, 1.26, 0.463),   
    },
    3:{
        "center":(-7.243, -0.416, 0.463),   
    },
    4:{
        "center":(-7.908, -2.7415, 0.6955),   
    },
    5:{
        "center":(7.908, -2.7415, 0.6955),   
    },
    6:{
        "center":(7.243, -0.416, 0.463),   
    },
    7:{
        "center":(7.243, 1.26, 0.463),   
    },
    8:{
        "center":(7.243, 2.9365, 0.463),   
    }

}


GET_CORNERS_MAT = np.array(
    [[-0.0762, -0.0762, 0.0],
    [0.0762, -0.0762, 0.0],
    [0.0762, 0.0762, 0.0],
    [-0.0762, 0.0762, 0.0]]
)
