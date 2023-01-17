
import cv2 
import numpy as np
import functions as f
import constants
vid = cv2.VideoCapture(0)
while(vid.isOpened()):    
    ret, frame = vid.read()  
    if ret == True:
        mask=f.maskGenerator(frame,constants.lower_yellow,constants.higher_yellow)
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours=f.convexHull(contours)    
        if len(contours) >0:#to make sure the porgram doesn't crash if camers sees no target.
            biggest_contour=f.find_biggest_contour(contours)
            center=f.find_and_draw_center_of_target(frame,biggest_contour)
        cv2.imshow("Camera Voew",frame)
        # the 'q' button is set for break
        if cv2.waitKey(55) & 0xFF == ord('q'):
            break
       
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()


