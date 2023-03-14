import cv2 as cv
from pupil_apriltags import Detector, Detection

cap = cv.VideoCapture(0)
TAG_FAMILY = "tag16h5"
DETECTOR = Detector(
    families=TAG_FAMILY,
    nthreads=1,
    quad_decimate=1,
    quad_sigma=0.1,
    refine_edges=0,
    decode_sharpening=0.25,
    debug=0
    )
while True:
    success, frame = cap.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    detections:list[Detection] = DETECTOR.detect(gray)
    if detections:
        for detection in detections:

            if detection.tag_id not in [1,2,3,4,5,6] and len(detection.corners) >= 4:
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



    cv.imshow("f",frame)

    cv.waitKey(1)