#!/usr/bin/env python
 
import cv2
import numpy as np
import os
from glob import glob
import json
from datetime import datetime
from sys import exit

"""
Simple script to facilitate calculating camera intrinsics and distortion.

When collecting with the camera, images are saved in ./calimg_<timestampstring>
Calibration json files are saved to ./cameraconfig/calibration_<timestampstring>.json

If a path to a folder is provided, app will load the files there and produce a calibration.

usage: calibrate.py [-h] [-c CAMERA] [--folder FOLDER] [--camwidth CAMWIDTH] [--camheight CAMHEIGHT] [-i IMAGECNT]
                    [--fixratio]

optional arguments:
  -h, --help            show this help message and exit
  -c CAMERA, --camera CAMERA
  --folder FOLDER
  --camwidth CAMWIDTH
  --camheight CAMHEIGHT
  -i IMAGECNT, --imagecnt IMAGECNT
  --fixratio

"""


def load_folder(objpoints, imgpoints, src, objp, criteria, CHECKERBOARD):
    for f in glob(os.path.join(src, "*")):
        img = cv2.imread(f)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        imgsz = gray.shape[::-1]

        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        
        if not ret:
            print(f"No checkerboard in {f}; skipping")
            continue
        print(f"loaded {f}")

        corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
        objpoints.append(objp)             
        imgpoints.append(corners2)

    return imgsz


def load_camera(camid, camwidth, camheight, objpoints, imgpoints, dst, objp, criteria, checkerboard,
                imagecnt):
    cap:cv2.VideoCapture = cv2.VideoCapture(camid)

    if not cap.isOpened():
        print(f"*** Could not open cameraid {camid}")
        exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camwidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camheight)

    cnt = 0
    print(f"Camera id {camid} opened.")

    break_f = False
    lastmsg = None

    while not break_f and cnt < imagecnt:
        success, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgsz = gray.shape[::-1]

        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(gray, checkerboard, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        

        if ret:
            # Draw and display the corners
            
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)

            img_marked = img.copy()
            cv2.drawChessboardCorners(img_marked, checkerboard, corners2, ret)
            cv2.imshow('img',img_marked)

            if lastmsg == None or lastmsg != "hint":
                print("Press S to save this image, Q to quit")
                lastmsg = "hint"

            keycode = cv2.waitKeyEx(100)
            if keycode != -1:
                key = chr(keycode)

                if key == 's':
                    objpoints.append(objp)             
                    imgpoints.append(corners2)
                    cv2.imwrite(os.path.join(dst, f"cal{cnt:02d}.jpeg"), img)
                    cnt +=1
                    print(f"saved image {cnt} togo {imagecnt-cnt}")
                    lastmsg = "saved"
                elif key == 'q':
                    break_f = True
        else:
            if lastmsg != "nochess":
                print("NO CHESSBOARD")
                lastmsg = "nochess"
     
    cv2.destroyAllWindows()
    return imgsz


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-c', '--camera', type=int, default=1) 
    parser.add_argument("--folder", type=str, default=None)
    parser.add_argument("--camwidth", type=int, default=1280)
    parser.add_argument("--camheight", type=int, default=720)
    parser.add_argument("-i", "--imagecnt", type=int, default=25)
    parser.add_argument("--fixratio", action="store_true", default=False)

    args = parser.parse_args()

    ts = datetime.now()
    ts_str = ts.strftime("%Y%m%d-%H%M")
    CHECKERBOARD = (6, 9)

    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

    # Defining the dimensions of checkerboard ##THE 30 IS FOR LENGTH OF SMALL SQUARE
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
     
    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 

    if args.folder:
        if not os.path.exists(args.folder):
            print(f"*** Cannot find source folder {args.folder}")
            exit()

        print(f"Sourcing reference images from {args.folder}")
        imgsize = load_folder(objpoints, imgpoints, args.folder, objp, criteria, CHECKERBOARD)
    else:
        dst = f"calimg_{ts_str}"
        print(f"Calibrating with camid {args.camera} saving images in {dst}")
        os.mkdir(dst)
        imgsize = load_camera(args.camera, args.camwidth, args.camheight,
                    objpoints, imgpoints, dst, objp, criteria, CHECKERBOARD, args.imagecnt)
     
     
    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """

    if len(objpoints) == 0:
        print("*** No objectpoints found; cannot calibrate.")
        exit()

    # input array with a fixed ratio between X and Y focal length
    # to allow the option of CALIB_FIX_ASPECT_RATIO
    cmtx_input = np.array( [[1,0,0], [0,1,0], [0,0,1]] )

    flags = cv2.CALIB_FIX_ASPECT_RATIO if args.fixratio else None
    print(f"Calibrating image size {imgsize}")
    rms, cmtx, distortion, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, imgsize,
        cmtx_input, None, flags=flags)
     
    print("Camera matrix :")
    print(cmtx)
    print("\nDistortion :")
    print(distortion)
    print(f"overall rms reprojection error: {rms:.3f}")

    if not os.path.exists("cameraconfig"):
        os.mkdir("cameraconfig")

    ##Save the params to json.
    data = dict()
    with open(os.path.join("cameraconfig", f"calibration_{ts_str}.json"), "w") as f:
        #data = json.load(f)
        data["matrix"] = cmtx.tolist()
        data["distortion"] = distortion[0,:].tolist()
        data["rms"] = rms
        #data["rvecs"] = rvecs
        #data["tvecs"] = tvecs
        json.dump(data, f, indent=1)

if __name__ == "__main__":
    main()