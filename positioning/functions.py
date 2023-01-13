"""Functions that help make the pipeline more readable"""



from apriltag import apriltag
import cv2 as cv
import numpy as np
import constants

def getDetector():
    # return apriltag(
    # families=constants.TAG_FAMILY,
    # nthreads=1,
    # quad_decimate=1.0,
    # quad_sigma=0.0,
    # refine_edges=1,
    # decode_sharpening=0.25,
    # debug=0
    # )
    return apriltag( constants.TAG_FAMILY)


def getDetections(detector, frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    return detector.detect(gray)


def draw(img, corners, imgpts):
    
    for i in range(len(corners)):
        corners[i] = (int(corners[i][0]), int(corners[i][1]), int(corners[i][2]))


    corner = tuple(corners[0].ravel())

    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 10)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 10)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 10)

    return img



def getVecs(frame, cmtx, dist, detector):
    detections = getDetections(detector,frame)

    toreturn = {
        "tvecs":[],
        "rvecs":[]
    }

    if detections:
        euclideanCoords = []
        for detection in detections:

            if detection["id"] in [1,2,3,4,5,6,7,8] and len(detection["lb-rb-rt-lt"]) == 4:
                
                corner_counter = 1
                for x, y in detection["lb-rb-rt-lt"]:
                    corner = (int(x), int(y))
                    cv.putText(frame, f"{corner_counter}", corner, cv.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0))
                    cv.circle(frame, corner, 5, (255,0,0), -1)
                    corner_counter += 1

                cx, cy = detection["center"]
                cv.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
                cv.putText(frame, "id: %s"%(detection["id"]), (int(cx), int(cy) + 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255, 0))

                objectpoints = []

                for coord in constants.GET_CORNERS_MAT:
                    objectpoints.append(coord + constants.ID_POS[detection["id"]]["center"])


                objectpoints = np.array(objectpoints)



                mmat, rvec, tvec = cv.solvePnP(
                    objectpoints, 
                    detection["lb-rb-rt-lt"], 
                    cmtx,
                    dist,  
                    )
                # imgpts, jac = cv.projectPoints(objectpoints, rvec, tvec, constants.CAMERA_MATRIX, constants.CAMERA_DIST)

                # frame = draw(frame, detection.corners, imgpts)
                tvec = (np.array(tvec))
                rvec = (np.array(rvec))   

                print(tvec)
                print(rvec)  

                toreturn["tvecs"] = tvec
                toreturn["rvecs"] = rvec

                x, y, z = tvec
                euclideanCoords.append((x, y,))

                rx, ry, rz = rvec

                w, h, _ = frame.shape


                rotationmatrix, _ = cv.Rodrigues(rvec)
                print(rotationmatrix)
                # print(toreturn)

                final_coords = np.dot(rotationmatrix.T, tvec)

                px, py, pz = final_coords


                cv.putText(frame, "TX: %.4f TY: %.4f TZ: %.4f"%(x, y, z), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
                cv.putText(frame, "RX: %.4f RY: %.4f RZ: %.4f"%(rx, ry, rz), (50, 70), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
                cv.putText(frame, "PX: %.4f PY: %.4f PZ: %.4f"%(px, py, pz), (50, 100), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))



    return toreturn


