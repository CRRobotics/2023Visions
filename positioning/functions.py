"""Functions that help make the pipeline more readable"""



from apriltag import apriltag
import cv2 as cv
import numpy as np
import constants
from networktables import NetworkTables as nt
import threading

def networkConnect() -> any:
    cond = threading.Condition()
    notified = [False]

    def connectionListener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()

    nt.initialize(server=constants.SERVER)
    nt.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()
    return nt


def pushval(networkinstance, tablename:str, valuename, value:float):
    table = networkinstance.getTable(tablename)
    table.putNumber(valuename, value)

    

def getDetector():
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
        tagcounter = 0

        for detection in detections:
            if detection["id"] in [1,2,3,4,5,6,7,8] and len(detection["lb-rb-rt-lt"]) == 4:
                
                corner_counter = 1
                for x, y in detection["lb-rb-rt-lt"]:
                    corner = (int(x), int(y))
                    cv.putText(frame, f"{corner_counter}", corner, cv.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0))
                    cv.circle(frame, corner, 5, (255,0,0), -1)
                    corner_counter += 1

                cx, cy = detection["center"]
                tagcounter += 1
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

            rotationmatrix, _ = cv.Rodrigues(rvec)

            final_coords = np.dot(-rotationmatrix.T, tvec)

            p = np.hstack((rotationmatrix, tvec))

            euler_angles_r = -cv.decomposeProjectionMatrix(p)[6]

            ax, ay, az = euler_angles_r

            px, py, pz = final_coords

            toreturn["pos"] = final_coords
            toreturn["angle"] = euler_angles_r
            toreturn["tags"] = tagcounter


            cv.putText(frame, "PX: %.4f PY: %.4f PZ: %.4f"%(px, py, pz), (50, 100), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
            cv.putText(frame, "AX: %.4f AY: %.4f AZ: %.4f"%(ax, ay, az), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
            return toreturn

def mergeCams(vecsdicts):
    pos1 = vecsdicts[0]["pos"]
    pos2 = vecsdicts[2]["pos"]
    rot1 = vecsdicts[0]["angle"]
    rot2 = vecsdicts[2]["angle"]
    tags1 = vecsdicts[0]["tags"]
    tags2 = vecsdicts[2]["tags"]
    w1, w2 = 1, 1
    if tags1 >= tags2: w1 = tags1/tags2
    else: w2 = tags2/tags1
    finalpos = (pos1 * w1 + pos2 * w2)/(w1 + w2)
    finalrot = (rot1 * w1 + rot2 * w2)/(w1 + w2)
    return finalpos, finalrot