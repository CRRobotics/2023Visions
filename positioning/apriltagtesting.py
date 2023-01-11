from pupil_apriltags import Detector
import cv2 as cv
import constants
from functions import *
import numpy as np
print("We out")

cap = cv.VideoCapture(1)

while True:
    success, frame = cap.read()

    #UNCOMMENT THIS IF YOU WANT TO TEST ON AN IMG
    frame = cv.imread(r"ConePlacement\sample_images\Straight__Left_187in.png")

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    detections:list[Detection] = getDetections(grayframe=gray)


    if detections:
        for detection in detections:

            if detection.tag_id not in [1,2,3,4,5,6,7,8] and len(detection.corners) != 4:
                continue

            corner_counter = 1
            for x, y in detection.corners:
                corner = (int(x), int(y))
                cv.putText(frame, f"{corner_counter}", corner, cv.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0))
                cv.circle(frame, corner, 5, (255,0,0), -1)
                corner_counter += 1

            cx, cy = detection.center
            cv.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
            cv.putText(frame, f"id: {detection.tag_id}", (int(cx), int(cy) + 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255, 0))

            objectpoints = []

            objectpoints.append((-0.0762, 0.0762, 0.0))
            objectpoints.append((0.0762, 0.0762, 0.0))
            objectpoints.append((0.0762, -0.0762, 0.0))
            objectpoints.append((-0.0762, -0.0762, 0.0))

            objectpoints = np.array(objectpoints)



            mmat, tvec, rvec = cv.solvePnP(
                objectpoints, 
                detection.corners, 
                constants.CAMERA_MATRIX,
                constants.CAMERA_DIST, 
                )
            imgpts, jac = cv.projectPoints(objectpoints, rvec, tvec, constants.CAMERA_MATRIX, constants.CAMERA_DIST)

            frame = draw(frame, detection.corners, imgpts)

            print(tvec, rvec)



    else:
        print("NONE")
    cv.imshow("IMAGE", frame)


    cv.waitKey(1)