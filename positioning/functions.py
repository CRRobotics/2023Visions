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
        objectpoints = []
        cornerpoints = []

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


                for coord in constants.GET_CORNERS_MAT:
                    objectpoints.append(coord + constants.ID_POS[detection["id"]]["center"])

                for corner in detection["lb-rb-rt-lt"]:
                    cornerpoints.append(corner)

        if objectpoints and cornerpoints:

            objectpoints = np.array(objectpoints)
            cornerpoints = np.array(cornerpoints)

            # print("objectpoints:")
            # print(objectpoints)
            # print("cornerpoints:")       
            # print(cornerpoints)
            mmat, rvec, tvec = cv.solvePnP(
                objectpoints, 
                cornerpoints,
                cmtx,
                dist,  
                )

            tvec = (np.array(tvec))
            rvec = (np.array(rvec))   

            toreturn["tvecs"] = tvec
            toreturn["rvecs"] = rvec

            rotationmatrix, _ = cv.Rodrigues(rvec)

            final_coords = np.dot(-rotationmatrix.T, tvec)

            p = np.hstack((rotationmatrix, tvec))

            euler_angles_r = -cv.decomposeProjectionMatrix(p)[6]

            ax, ay, az = euler_angles_r

            px, py, pz = final_coords



            cv.putText(frame, "PX: %.4f PY: %.4f PZ: %.4f"%(px, py, pz), (50, 100), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
            cv.putText(frame, "AX: %.4f AY: %.4f AZ: %.4f"%(ax, ay, az), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))


    return toreturn


