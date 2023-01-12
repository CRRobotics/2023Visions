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


=======
    if ret == True:
        # After the loop release the cap object

        def binarizeSubt(img):
            blue, green, red = cv2.split(img)
            yellow=cv2.subtract(green,blue)
            ret,binImage = cv2.threshold(yellow, 40, 255, cv2.THRESH_BINARY)
            return binImage
        mask=binarizeSubt(img)

        kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        mask=cv2.erode(mask,kernel,iterations=10)
        mask=cv2.dilate(mask,kernel,iterations=10)
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours=[cv2.convexHull(contour) for contour in contours]


        min_size=0
        for contour in contours:
            contour_size=cv2.contourArea(contour)
            if contour_size>= min_size:
                min_size=contour_size
        
        filteredContours = []
        numContours = len(contours) 
        sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
        for i in range(numContours):
            area = cv2.contourArea(sortedContours[i])
            if area < min_size:
                break
            filteredContours.append(sortedContours[i])
        contours=filteredContours


        centers = []
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            countourArea=cv2.contourArea(contour)
            ratio=countourArea/(w*h)
            # if ratio >=0.6 or ratio <= 0.4:
            #     continue
            # if countourArea <=100: # and contourArea > maxArea:
            #     continue
            
            cv2.drawContours(img,[contour],0,(255,0,255),3)
            #contours is a tuple of arrays
            moments = cv2.moments(contour)
            centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
            for i in range(len(centers)):
                cv2.circle(img, centers[i], 3, (0, 0, 255), -1)
            # cv2.imshow("mask",mask)
      
    cv2.imshow('s',img)

    # the 'q' button is set for break
    if cv2.waitKey(555) & 0xFF == ord('q'):
        break
   
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
>>>>>>> Stashed changes


