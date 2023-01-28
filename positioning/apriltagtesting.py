import cv2 as cv
import constants
from functions import *
import numpy as np
import threading
from time import sleep
import sys
import os
print("We out")



def process_frame(cameraid, path, nt, headless = False):
    # cap = cv.VideoCapture(cameraid)
    cap = waitForCam(path)

    detector = getDetector()
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    cammat = constants.CAMERA_CONSTANTS[cameraid]["matrix"]
    distco = constants.CAMERA_CONSTANTS[cameraid]["distortion"]
    # ts = 0

    while True:

        success, frame1 = cap.read()

        if not success:
            print("failed to get image from camid ", cameraid)
            cap.release()
            cap = waitForCam(path)
            cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            continue

        vecsdict = getVecs(frame1, cammat, distco, detector, cameraid)

        if vecsdict:
            robotheta = vecsdict["angle"]
            rx, ry, _ = vecsdict["pos"]
            logStuff(cameraid, rx, ry, robotheta)
            # pushval(nt, f"{cameraid}", "theta", robotheta)
            # pushval(nt, f"{cameraid}", "rx",rx )
            # pushval(nt, f"{cameraid}", "ry", ry)
            # pushval(nt, f"{cameraid}", "ntags", vecsdict["tags"])
        if not headless: cv.imshow(f"CAMID{cameraid}:", frame1)
        cv.waitKey(1)
        # ts = time()
        

if __name__ == "__main__":

    headless = "-h" in sys.argv

    nt = 0#networkConnect()
    t1 = threading.Thread(target=process_frame, args=[0, os.path.realpath("/dev/v4l/by-path/pci-0000:06:00.3-usb-0:1.1:1.0-video-index0"),nt,headless])
    t2 = threading.Thread(target=process_frame, args=[2, os.path.realpath("/dev/v4l/by-path/pci-0000:06:00.3-usb-0:1.3:1.0-video-index0"),nt,headless])
    t3 = threading.Thread(target=process_frame, args=[4, os.path.realpath("/dev/v4l/by-path/pci-0000:06:00.3-usb-0:1.2:1.0-video-index0"),nt,headless])

    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    print("Done!")
