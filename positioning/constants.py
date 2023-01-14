from pupil_apriltags import *
import json
import numpy as np



TAG_FAMILY = "tag16h5"






with open("positioning/cameraconstants.json") as f:
    data = json.load(f)
    CAMERA_MATRIX1 = np.array(data["cam1"]["matrix"])
    CAMERA_DIST1 = np.array(data["cam1"]["distortion"])
    CAMERA_MATRIX2 = np.array(data["cam2"]["matrix"])
    CAMERA_DIST2 = np.array(data["cam2"]["distortion"])



ID_POS = {
    #Coordinates taken from field cad
    1:{
        "center":(-7.243, 2.9365, 0.463),
    },
    2:{
        # "center":(-7.243, 1.26, 0.463),   
        "center":(0, 0, 0),
    },
    3:{
        # "center":(-7.243, -0.416, 0.463),   
        "center":(1, 0, 0),

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

SERVER = "10.6.39.2"