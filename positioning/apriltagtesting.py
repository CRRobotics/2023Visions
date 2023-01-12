import cv2 as cv
import constants
from functions import *
import numpy as np
import threading
print("We out")



def process(cameraid:int):
    cap = cv.VideoCapture(cameraid)

    while 1:
        success, frame1 = cap.read()

        #UNCOMMENT THIS IF YOU WANT TO TEST ON AN IMG
        # frame = cv.imread(r"ConePlacement/sample_images/Straight__Left_187in.png")

        gray = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)

        vecsdict = getVecs(gray, constants.CAMERA_MATRIX1, constants.CAMERA_DIST1)
        #print(vecsdict)

        #success2, frame2 = cap2.read()
        #gray2 = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)

        #vecsdict2 = getVecs(gray2, constants.CAMERA_MATRIX2, constants.CAMERA_DIST2)
        #print(vecsdict2)

        cv.imshow(f"CAMID{cameraid}:", gray)

        cv.waitKey(10)

if __name__ == "__main__":
    t1 = threading.Thread(target=process, args=[0])
    t2 = threading.Thread(target=process, args=[2])
    t1.start()
    # starting thread 2
    t2.start()
 
    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()
 
    # both threads completely executed
    print("Done!")
