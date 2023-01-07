from pupil_apriltags import Detector
import cv2 as cv

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

cap = cv.VideoCapture(0)


while True:
    success, frame = cap.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    detection = at_detector.detect(gray)


    if detection:
        print(detection[0].tag_id)
        for x, y in detection[0].corners:

            cv.circle(frame, (int(x), int(y)), 15, (255,0,0), -1)
            
    else:
        print("NONE")




    cv.imshow("IMAGE", frame)


    cv.waitKey(1)