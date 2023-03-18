import cv2 as cv
from pupil_apriltags import Detector, Detection





def allGoodCorners(l:list, framewidth:int, frameheight:int, margin:int) -> bool:
    for corner in l:
        x, y = corner
        # print(x, y)
        if x < margin or x > framewidth - margin or y < margin or y > frameheight - margin:
            return False
    return True


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
    h, w, _  = frame.shape
    print(h, w)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    detections:list[Detection] = DETECTOR.detect(gray)
    if detections:
        for detection in detections:
            if detection.tag_id not in [1,2,3,4,5,6] or len(detection.corners) != 4 or detection.hamming > 0:
                continue
            if not allGoodCorners(detection.corners, w, h, 7):
                continue


            corner_counter = 1
            for x, y in detection.corners:
                corner = (int(x), int(y))
                cv.putText(frame, f"{corner}", corner, cv.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0))
                cv.circle(frame, corner, 5, (255,0,0), -1)
                corner_counter += 1
            cx, cy = detection.center
            margin = detection.decision_margin
            cv.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
            cv.putText(frame, f"id: {detection.tag_id}, margin:{margin}", (int(cx), int(cy) + 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255, 0))



    cv.imshow("f",frame)

    cv.waitKey(1)