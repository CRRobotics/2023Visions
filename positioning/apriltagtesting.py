import cv2 as cv
import constants
from functions import *
import numpy as np
import threading
from time import time
print("We out")



def process_frame(cameraid:int, nt):
    # print("thread on")
    cap = cv.VideoCapture(cameraid)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    detector = getDetector()
    # global globalvecsdict

    cammat = constants.CAMERA_CONSTANTS[cameraid]["matrix"]
    distco = constants.CAMERA_CONSTANTS[cameraid]["distortion"]
    # ts = 0

    while cap.isOpened():
        # delta = time() - ts
        # if delta < 0.03:
        #     ts = time()
        #     cv.waitKey(1)
        #     continue

        success, frame1 = cap.read()

        if not success:
            print("failed to get image from camid ", cameraid)
            continue

        vecsdict = getVecs(frame1, cammat, distco, detector, cameraid)

        if vecsdict:
            robotheta = vecsdict["angle"]
            rx, ry, _ = vecsdict["pos"]
            # pushval(nt, f"{cameraid}", "Robotheta", robotheta)
            # pushval(nt, f"{cameraid}", "rx",rx )
            # pushval(nt, f"{cameraid}", "ry", ry)
            # pushval(nt, f"{cameraid}", "ntags", vecsdict["tags"])
            
            # globalvecsdict[cameraid] = {
            #     "gx": px[0][0],
            #     "gy": py[0][0],
            #     "theta":robotheta
            # }

        # if globalvecsdict[0] and globalvecsdict[2]:
        #     ...
        #     pos, rot = mergeCams(globalvecsdict)
        #     print("Pos: ", pos, "\nRot: ", rot)
        # print(globalvecsdict)
        cv.imshow(f"CAMID{cameraid}:", frame1)
        cv.waitKey(1)
        # ts = time()

if __name__ == "__main__":
    globalvecsdict = {
        0: {},
        2: {}
    }

    nt = 0#networkConnect()
    t1 = threading.Thread(target=process_frame, args=[0,nt])
    t2 = threading.Thread(target=process_frame, args=[2,nt])
    t3 = threading.Thread(target=process_frame, args=[4,nt])

    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    print("Done!")
