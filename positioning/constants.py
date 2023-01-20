from pupil_apriltags import *
import json
import numpy as np
import math


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
        # "center":(7.243, -0.416, 0.463),   
        "center":(0,0,.45),  
    },
    7:{
        # "center":(7.243, 1.26, 0.463),   
        #"center":(0.52, 0, 2), 
                "center":(0, -0.52, 0.45), 

    },
    8:{
        # "center":(7.243, 2.9365, 0.463),   
        "center":(-2.43, 0, .2032),   

    }

}


CAMERA_CONSTANTS = {
    2:{
        "matrix":np.array([
            [718.02540665,   0, 306.29075167],
            [  0, 716.74383442, 278.79248039],
            [  0, 0, 1]]),
        "distortion":np.array([
            [ 0.07608043, -0.22768113, -0.00260825, -0.00425322,  0.49783845]
        ]),
        "yc": .09 * math.sin(math.radians(22.5)),
        "xc": -.05 - .09 * math.cos(math.radians(22.5)),
        "thetar": 22.5

    },
    0:{
        "matrix":np.array([
            [712.18698603790472, 0, 330.21795922692598], 
            [0, 712.18698603790472, 235.32274423954303], 
            [0, 0, 1]]),
        "distortion":np.array([
            [0.071468959300027085, -0.16401274740062791, 0, 0, 0.24746369126806475]
        ]),
        "yc": -.09 * math.sin(math.radians(22.5)),
        "xc": -.05 - .09 * math.cos(math.radians(22.5)),
        "thetar": -22.5
    }
}

GET_CORNERS_MAT = np.array(
    [[-0.0762, -0.0762, 0.0],
    [0.0762, -0.0762, 0.0],
    [0.0762, 0.0762, 0.0],
    [-0.0762, 0.0762, 0.0]]
)


GET_CORNERS_MAT_OTHER_WAY = np.array(
    [
    [0.0762, -0.0762, 0.0],
    [-0.0762, -0.0762, 0.0],
    [-0.0762, 0.0762, 0.0],
    [0.0762, 0.0762, 0.0],
    ]

)


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

SERVER = "10.6.39.2"