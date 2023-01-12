import cv2  
from functions import *
vid = cv2.VideoCapture(0)


 
while True:    
    
    success, img = vid.read()  
    #ret is a bool for whether frame is captured sussessfully
    img = cv2.imread(r"positioning/sample_images/162_36_Angle.png")
    # Display the resulting frame
    # After the loop release the cap object

    mask=binarizeSubt(img)
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    mask=cv2.erode(mask,kernel,iterations=3)
    mask=cv2.dilate(mask,kernel,iterations=1)

    contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    retained = filtercontours(contours)
    biggest = cv2.convexHull(max(retained, key=cv2.contourArea))
    cv2.drawContours(img,[biggest],0,(255,0,255),3)
    centers=getCenters(img,retained)


    lines:list[Line] = find_lines(img)

    for l in lines:
        p = (l.x1, l.y1)
        p2 = (l.x2, l.y2)

        if in_hull(biggest, p) and in_hull(biggest, p):
            cv2.circle(img, p, 2, (255, 255, 255), 3)
            cv2.circle(img, p2, 2, (255, 255, 255), 3)

            cv2.line(img, p, p2, (255, 0, 0), 2)
    cv2.imshow('s',img)

    cv2.waitKey(0)




