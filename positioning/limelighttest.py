import cv2 as cv


cap = cv.VideoCapture(0)

while True:
    success, frame = cap.read()




    cv.imshow("f",frame)

    cv.waitKey(1)