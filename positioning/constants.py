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



with open("positioning\cameraconstants.json") as f:
    data = json.load(f)
    CAMERA_MATRIX = np.array(data["matrix"])
    CAMERA_DIST = np.array(data["distortion"])

