from pupil_apriltags import Detector
import cv2
import numpy as np
import os, sys
import json
import constants
import math
from datetime import datetime
from csv import writer

"""
Hacked up script to replicate the AprilTag recognition and conversion.
Uses https://pypi.org/project/pupil-apriltags/ for recognition.
Note: You will need GNU pthreads dll installed to load the pupiltags dll.

Usage: python collect.py <calibrationfile>

Calibration files are found in ./cameraconfig.
Saves results in to ./log

"""

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


def getVecs(frame, cmtx, dist, tags):
    THECAMERA = 4
    toreturn = dict()

    objectpoints = []
    cornerpoints = []
    tagcounter = 0
    margins = []

    for detection in tags:
        if detection.tag_id in [1,2,3,4,5,6,7,8] and detection.decision_margin > MARGIN_THRESH:
            # TODO: more ways to filter out?
            print(f"DETECTED {detection.tag_id} margin {detection.decision_margin}")
            

            # cx, cy = detection.center

            if detection.tag_id in [5, 6, 7, 8]:
                for coord in constants.CORNERS_AS_IN_FIELD_MAT_OTHER_WAY:
                    objectpoints.append(coord + constants.ID_POS_NEW[detection.tag_id]["center"])
            else:
                for coord in constants.CORNERS_AS_IN_FIELD:
                    objectpoints.append(coord + constants.ID_POS_NEW[detection.tag_id]["center"])
                    
            for corner in detection.corners:
                cornerpoints.append(corner)
            
            margins.append(detection.decision_margin)
            
        else:
            print(f"junk tag_id {detection.tag_id} cornercnt {len(detection.corners)} margin {detection.decision_margin}")

    if objectpoints and cornerpoints:
        objectpoints = np.array(objectpoints)
        cornerpoints = np.array(cornerpoints)

        mmat, rvec, tvec = cv2.solvePnP(
            objectpoints, 
            cornerpoints,
            cmtx,
            dist,  
            )

        tvec = (np.array(tvec))
        rvec = (np.array(rvec))   

        rotationmatrix, _ = cv2.Rodrigues(rvec)

        final_coords = np.dot(-rotationmatrix.T, tvec)

        p = np.hstack((rotationmatrix, tvec))

        _, _, _, _, _, rmatZ, euler_angles_r = cv2.decomposeProjectionMatrix(p)

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

        robocoords, robotheta = getRobotVals(ztheta, THECAMERA, px, py)

        toreturn["pos"] = robocoords

        rx, ry, _ = robocoords

        toreturn["angle"] = robotheta
        toreturn["tags"] = tagcounter
        toreturn["margins"] = margins

        rvx, rvy, rvz = rvec

        rvx = math.degrees(rvx[0])
        rvy = math.degrees(rvy[0])
        rvz = math.degrees(rvz[0])

        cv2.putText(frame, " PX: %.4f  PY: %.4f  PZ: %.4f"%(px, py, pz), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
        # cv.putText(frame, " AX: %.4f  AY: %.4f  AZ: %.4f"%(ax, ay, az), (50, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 255))
        cv2.putText(frame, " ZTHETA: %.4f"%(ztheta), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
        cv2.putText(frame, " RX: %.4f  RY: %.4f RTHETA: %.4f"%(rx, ry, math.degrees(robotheta)), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
        # cv.putText(frame, "RVX: %.4f RVY: %.4f RVZ: %.4f"%(rvx, rvy, rvz), (50, 150), cv.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 255))

    return toreturn


def markup(img, tags):
    for tag in tags:
        if tag.tag_id != 5:
            continue

        for idx in range(len(tag.corners)):
            cv2.line(
                img,
                tuple(tag.corners[idx - 1, :].astype(int)),
                tuple(tag.corners[idx, :].astype(int)),
                (0, 255, 0),
            )

        cv2.putText(
            img,
            str(tag.tag_id),
            org=(
                tag.corners[0, 0].astype(int) + 10,
                tag.corners[0, 1].astype(int) + 10,
            ),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.8,
            color=(0, 0, 255),
        )
    return img


def process_frame(cap, at_detector, intrinsics, distortion, logf):
    #cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    success = True
    framecnt = 0
    while success:
        success, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tags = at_detector.detect(gray)

        markedup = markup(img, tags)

        if not success:
            print("failed to get image")
            cap.release()
            continue

        cv2.imshow("capture", markedup)

        if tags:
            vecsdict = getVecs(gray, intrinsics, distortion, tags)
            if vecsdict:
                # log the results
                logf.writerow([vecsdict["pos"][0][0][0], vecsdict["pos"][1][0][0], vecsdict["angle"]])

        """
        if vecsdict:
            robotheta = vecsdict["angle"]
            rx, ry, _ = vecsdict["pos"]
            logStuff(cameraid, rx, ry, robotheta, timezz)
            pushval(nt, f"{cameraid}", "theta", robotheta)
            pushval(nt, f"{cameraid}", "rx",rx )
            pushval(nt, f"{cameraid}", "ry", ry)
            pushval(nt, f"{cameraid}", "ntags", vecsdict["tags"])
            pushval(nt, f"{cameraid}", "time", timezz)
        if not headless: cv.imshow(f"CAMID{cameraid}:", shrinkFrame(frame1))
        cv.waitKey(1)

        # ts = time()
        """
        framecnt += 1
        print(f"Processed frame {framecnt} tagcnt {len(tags)}")
        keycode = cv2.waitKeyEx(100)
        if keycode != -1 and chr(keycode) == 'q':
            success = False


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('cameraconfig', type=str, help="Name of .json calibration file") 

    args = parser.parse_args()

    TAG_FAMILY = "tag16h5"
    CAMERAID = 1
    CONFIGDIR = "cameraconfig"
    CALIBRATION = args.cameraconfig

    try:
        configfn = os.path.join(CONFIGDIR, f"{CALIBRATION}.json") 
        with open(configfn, "r") as fp:
           cameraconfig = json.load(fp)
    except:
        print(f"*** Could not open config file {configfn}")

    print(f"Using config {CALIBRATION} cameraid {CAMERAID}, tag family {TAG_FAMILY}")
    cap:cv2.VideoCapture = cv2.VideoCapture(CAMERAID)

    if not cap.isOpened():
       print(f"*** Could not open cameraid {CAMERAID}")
       sys.exit()

    at_detector = Detector(
      families=TAG_FAMILY,
      nthreads=1,
      quad_decimate=1.0,
      quad_sigma=0.0,
      refine_edges=1,
      decode_sharpening=0.25,
      debug=0
    )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    intrinsics = np.array(cameraconfig["matrix"])
    distortion = np.array(cameraconfig["distortion"])

    timezz = datetime.now().timestamp()

    if not os.path.exists("logs"):
       os.mkdir("logs")
       
    with open(os.path.join("logs", f"taglog_{timezz}.csv"), "w", newline="") as log:
       logw = writer(log)
       logw.writerow(["robotx", "roboty", "theta"])
       status = True
       while status:
          status = process_frame(cap, at_detector, intrinsics, distortion, logw)

    #cv2.imshow('img',img)

    #print("Showing image")
    #keycode = cv2.waitKeyEx(0)
    #key = chr(keycode)

    cv2.destroyAllWindows()

if __name__ == "__main__":
   MARGIN_THRESH = 20
   main()