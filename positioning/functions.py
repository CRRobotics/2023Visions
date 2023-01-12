"""Functions that help make the pipeline more readable"""



from pupil_apriltags import *
import cv2 as cv
import numpy as np
import constants



def getDetections(grayframe) -> Detection:
    return constants.DETECTOR.detect(grayframe)


def draw(img, corners, imgpts):
    
    for i in range(len(corners)):
        corners[i] = (int(corners[i][0]), int(corners[i][1]), int(corners[i][2]))


    corner = tuple(corners[0].ravel())

    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 10)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 10)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 10)

    return img



def getVecs(frame, cmtx, dist):
    detections:list[Detection] = getDetections(grayframe=frame)

    toreturn = {
        "tvecs":[],
        "rvecs":[]
    }

    if detections:
        for detection in detections:

            if detection.tag_id in [1] and len(detection.corners) == 4:
                
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

                for coord in constants.GET_CORNERS_MAT:
                    objectpoints.append(coord + constants.ID_POS[detection.tag_id]["center"])


                objectpoints = np.array(objectpoints)



                mmat, tvec, rvec = cv.solvePnP(
                    objectpoints, 
                    detection.corners, 
                    cmtx,
                    dist,  
                    )
                # imgpts, jac = cv.projectPoints(objectpoints, rvec, tvec, constants.CAMERA_MATRIX, constants.CAMERA_DIST)

                # frame = draw(frame, detection.corners, imgpts)

                toreturn["tvecs"] = tvec
                toreturn["rvecs"] = rvec
    return toreturn


