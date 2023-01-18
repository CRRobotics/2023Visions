"""Functions that help make the pipeline more readable"""



from apriltag import apriltag
import cv2 as cv
import numpy as np
import constants
from networktables import NetworkTables as nt
import threading
import math

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



def getVecs(frame, cmtx, dist, detector, cameraid):
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


                if detection["id"] in [8]:
                    for coord in constants.GET_CORNERS_MAT_OTHER_WAY:
                        objectpoints.append(coord + constants.ID_POS[detection["id"]]["center"])
                else:
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



            robocoords, robotheta = getRobotVals(ay, cameraid, pz, px)

            toreturn["pos"] = robocoords

            rx, ry, _ = robocoords

            toreturn["angle"] = robotheta
            toreturn["tags"] = tagcounter


            cv.putText(frame, "PX: %.4f PY: %.4f PZ: %.4f"%(px, py, pz), (50, 100), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
            cv.putText(frame, "AX: %.4f AY: %.4f AZ: %.4f"%(ax, ay, az), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))
            cv.putText(frame, "RX: %.4f RY: %.4f RTHETA: %.4f"%(rx, ry, robotheta), (50, 150), cv.FONT_HERSHEY_SIMPLEX, .5, (255,255, 0))

            return toreturn

def mergeCams(vecsdicts):
    # Get positions, rotations, and number of tags each one sees
    pos1 = vecsdicts[0]["pos"]
    pos2 = vecsdicts[2]["pos"]
    rot1 = vecsdicts[0]["angle"]
    rot2 = vecsdicts[2]["angle"]
    tags1 = vecsdicts[0]["tags"]
    tags2 = vecsdicts[2]["tags"]
    w = tags1/tags2 #Weight based on number of tags each one sees
    #Weighted average based on number of cameras
    finalpos = (pos1 * w + pos2)/(w + 1)
    finalrot = (rot1 * w + rot2)/(w + 1)
    return finalpos, finalrot




def getRobotVals(ay, cameraid, px, py):
    #print("ay %s, px, %s, py%s"%(ay, px, py))
    robotheta = math.radians(ay - constants.CAMERA_CONSTANTS[cameraid]["thetar"])
    xr = constants.CAMERA_CONSTANTS[cameraid]["xc"]
    yr = constants.CAMERA_CONSTANTS[cameraid]["yc"]

    #print("THETA:", robotheta)

    transformationmatrix = np.array(
        [
            [math.cos(math.radians(ay)), -math.sin(math.radians(ay)), px],
            [math.sin(math.radians(ay)), math.cos(math.radians(ay)), py],
            [0, 0, 1]
        ],
        dtype=object
    )

    #print("TRANSFORMATIOMATRIX:", transformationmatrix)

    robotcoordsRelativetocam = np.array(
        [
            [xr],
            [yr],
            [1]
        ],
        dtype=object
    )
    #print("robotcoordsRelativeToCam:", robotcoordsRelativetocam)

    robocoords = np.dot(transformationmatrix, robotcoordsRelativetocam)

    return robocoords, robotheta