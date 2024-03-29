"""Functions that help make the pipeline more readable"""



from apriltag import apriltag
import cv2 as cv
import numpy as np
import constants
from networktables import NetworkTables as nt
import threading
import math
from time import sleep
import csv
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation


##THIS FUNTION PREVENTs CLIPPING
def allGoodCorners(l:list, framewidth:int, frameheight:int, margin:int) -> bool:
    for corner in l:
        x, y = corner
        print(x, y)
        if x < margin or x > framewidth - margin or y < margin or y > frameheight - margin:
            return False
    return True


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
    aprilobj = apriltag(constants.TAG_FAMILY, maxhamming=0, blur = 0.1)
    return aprilobj


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

    h, w, _ = frame.shape

    toreturn = {
    }

    if detections:
        objectpoints = []
        cornerpoints = []
        tagcounter = 0
        margins = []

        for detection in detections:
            if detection["id"] in [1,2,3,4,5,6,7,8] and len(detection["lb-rb-rt-lt"]) == 4 and detection["margin"] > constants.MARGIN_THRESHOLD and allGoodCorners(detection["lb-rb-rt-lt"], w, h, constants.PIXEL_MARGIN):
                
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
                

                if detection["id"] in [5, 6, 7, 8]:
                    for coord in constants.CORNERS_AS_IN_FIELD_MAT_OTHER_WAY:
                        objectpoints.append(coord + constants.ID_POS_NEW[detection["id"]]["center"])
                else:
                    for coord in constants.CORNERS_AS_IN_FIELD:
                        objectpoints.append(coord + constants.ID_POS_NEW[detection["id"]]["center"])

                for corner in detection["lb-rb-rt-lt"]:
                    cornerpoints.append(corner)
                
                margins.append(detection["margin"])

        if objectpoints and cornerpoints:

            objectpoints = np.array(objectpoints)
            cornerpoints = np.array(cornerpoints)

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

            _, _, _, _, _, rmatZ, euler_angles_r = cv.decomposeProjectionMatrix(p)

            euler_angles_r = -euler_angles_r

            # Get coordinates of rotated point on unit sphere. We want to project it onto the x-y axis
            pointCoords = np.dot(rotationmatrix.T, np.array([[1],[0],[0]]))

            pointX, pointY = [pointCoords[0][0], pointCoords[1][0]]


            # Signs of x and y coordinates on unit circle
            sx = 1 if pointX <= 0 else -1
            sy = 1 if pointY <= 0 else -1
            # # Modify theta based on coordinate quadrant to compensate for arctan only going from -90 to 90
            ztheta = math.degrees(math.atan(pointCoords[1][0]/pointCoords[0][0])) + (180*sy)*(sx - 1)/(-2)
            ztheta -= 90
            if ztheta < 0: ztheta += 360


            ax, ay, az = euler_angles_r

            px, py, pz = final_coords

            robocoords, robotheta = getRobotVals(ztheta, cameraid, px, py)

            toreturn["pos"] = robocoords

            rx, ry, _ = robocoords

            toreturn["angle"] = robotheta
            toreturn["tags"] = tagcounter
            toreturn["margins"] = margins

            rvx, rvy, rvz = rvec

            rvx = math.degrees(rvx[0])
            rvy = math.degrees(rvy[0])
            rvz = math.degrees(rvz[0])

            cv.putText(frame, " PX: %.4f  PY: %.4f  PZ: %.4f"%(px, py, pz), (50, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            # cv.putText(frame, " AX: %.4f  AY: %.4f  AZ: %.4f"%(ax, ay, az), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 255))
            cv.putText(frame, " ZTHETA: %.4f"%(ztheta), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            cv.putText(frame, " RX: %.4f  RY: %.4f RTHETA: %.4f"%(rx, ry, math.degrees(robotheta)), (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            # cv.putText(frame, "RVX: %.4f RVY: %.4f RVZ: %.4f"%(rvx, rvy, rvz), (50, 150), cv.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 255))
            return toreturn
    return {
        "pos": (63900,63900,63900),
        "angle":63900,
        "tags":0,
        "margins":0
    }
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
    if robotheta > math.pi: robotheta -= math.tau
    xr = constants.CAMERA_CONSTANTS[cameraid]["xc"]
    yr = constants.CAMERA_CONSTANTS[cameraid]["yc"]

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

def waitForCam(path):
    while True:
        cap = cv.VideoCapture(path)
        cap:cv.VideoCapture
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv.CAP_PROP_FPS, 20)
        if cap.isOpened():
            print("open")
            return cap
        else:
            # print("not open")
            sleep(0.001)

def logStuff(camid, rx, ry, rt, time):
    with open("/home/crr/2023Visions/positioning/log.csv", "a+", newline="") as log:
        c = csv.writer(log)
        c.writerow(
            [camid, rx, ry, rt, time]
        )

def shrinkFrame(frame):
    kernel = np.ones((2,2),np.float32)/4
    dst = cv.filter2D(frame,-1,kernel)
    return dst[::2,::2]

# def graph():
#     if len(constants.RX_LOG) > 1000:
#         del constants.RX_LOG[0]
#         del constants.RY_LOG[0]
#         del constants.RT_LOG[0]

#     t = [i for i in range(len(constants.RX_LOG))]

#     plt.subplot(3, 1, 1)
#     plt.plot(t, constants.RX_LOG, label="rx")
#     plt.legend()
#     plt.subplot(3, 1, 2)
#     plt.plot(t, constants.RY_LOG, label="ry")
#     plt.legend()
#     plt.subplot(3, 1, 3)
#     plt.plot(t, constants.RT_LOG, label="rt")
#     plt.legend()

# def realtime_log():
#     ani = animation.FuncAnimation(constants.FIG, graph, save_count=0, cache_frame_data=False)
#     plt.show()