from pupil_apriltags import *



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