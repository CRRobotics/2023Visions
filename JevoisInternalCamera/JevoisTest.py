# ser =  serial.Serial('/dev/ttyUSB0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) #Tried with and without the last 3 parameters, and also at 1Mbps, same happens.

# ser.flushInput()
# ser.flushOutput()

import cv2 as cv2
import numpy as np
def circularmask(img):
    radius2 = 160
    ww, hh, _ = img.shape
    xc = hh // 2
    yc = ww // 2

    print(xc, yc)
    
    mask2 = np.zeros_like(img)
    mask = cv2.circle(mask2, (xc,yc), radius2, (255,255,255), -1)
    dst = cv2.bitwise_and(img, mask2)
    return dst

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
while True:
  s, f = cap.read()

  # f = circularmask(f)

  cv2.imshow("frame",f)


  cv2.waitKey(1)
  # data_raw = ser.read()
  # print(data_raw)
