import cv2 as cv
import constants
from functions import *
import numpy as np
import threading
print("We out")



def process_frame(cameraid:int, cammat, distco, nt):
    cap = cv.VideoCapture(cameraid)
    detector = getDetector()
    global globalvecsdict

    while 1:
        success, frame1 = cap.read()

        #UNCOMMENT THIS IF YOU WANT TO TEST ON AN IMG
        # frame = cv.imread(r"ConePlacement/sample_images/Straight__Left_187in.png")

        vecsdict = getVecs(frame1, cammat, distco, detector)

        if vecsdict:
            anglez = vecsdict["angle"]
            ax, ay, az = anglez

            #UNCOMMENT FOR NETWORKTABLES
            """pushval(nt, "Position", "anglex", ax)
            pushval(nt, "Position", "angley", ay)
            pushval(nt, "Position", "anglez", az)"""
        globalvecsdict[cameraid] = vecsdict

        if globalvecsdict[0] and globalvecsdict[2]:
            pos, rot = mergeCams(globalvecsdict)
            print("Pos: ", pos, "\nRot: ", rot)
        
        cv.imshow(f"CAMID{cameraid}:", frame1)
        # print(f"CAMERAID: {cameraid}")
        # print(vecsdict)
        cv.waitKey(1)

if __name__ == "__main__":
    globalvecsdict = {
        0: {},
        2: {}
    }

    nt = 0#networkConnect()
    t1 = threading.Thread(target=process_frame, args=[0, constants.CAMERA_MATRIX1, constants.CAMERA_DIST1, nt])
    t2 = threading.Thread(target=process_frame, args=[2, constants.CAMERA_MATRIX2, constants.CAMERA_DIST2, nt])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Done!")
