import cv2  
vid = cv2.VideoCapture(0)


 
while(vid.isOpened()):    
    
    ret, img = vid.read()  
    #ret is a bool for whether frame is captured sussessfully
    # Display the resulting frame
    if ret == True:
        def binarizeSubt(img):
            blue, green, red = cv2.split(img)
            b=cv2.subtract(blue,green)
            b_minus_green_minus_green=cv2.subtract(b,green)                                                                                                                                                                                                                                                                                                                                                                     
        
            ret,binImage = cv2.threshold(b_minus_green_minus_green, 1, 255, cv2.THRESH_BINARY)
            return binImage
        mask=binarizeSubt(img)
        kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        mask=cv2.erode(mask,kernel,iterations=3)
        mask=cv2.dilate(mask,kernel,iterations=1)
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        def getCenters(img, contours):
            """_, contours, _ = cv2.findContours
            returns centers of all polygons"""
            centers = []
            for i in range(len(contours)):
                moments = cv2.moments(contours[i])
                centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
                cv2.circle(img, centers[-1], 3, (0, 0, 255), -1)
            return centers
        #contours is a tuple with multiple arrays
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            m=w/h#show how perfect the square is
            countourArea=cv2.contourArea(contour)
            ratio=countourArea/(w*h)
          
            if ratio < 0.6 or m >= 1.7 or m <= 1:
            
              
                continue
            
            

        
            
            cv2.drawContours(img,[contour],0,(255,0,255),3)
            #contours is a tuple of arrays
            centers=getCenters(img,contours)



            cv2.imshow("img",img)
            
        # the 'q' button is set for break
        if cv2.waitKey(55) & 0xFF == ord('q'):
            break
       
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()


