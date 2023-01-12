import cv2  
vid = cv2.VideoCapture(0)


 
while(vid.isOpened()):    
    
    ret, img = vid.read()  
    #ret is a bool for whether frame is captured sussessfully
    img = cv2.imread(r"positioning/sample_images/162_36_Angle.png")
    # Display the resulting frame
    if ret == True:
        # After the loop release the cap object

        def binarizeSubt(img):
            blue, green, red = cv2.split(img)
            yellow=cv2.subtract(green,blue)
            ret,binImage = cv2.threshold(yellow, 40, 255, cv2.THRESH_BINARY)
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

        for i in range(len(contours)):
            x,y,w,h=cv2.boundingRect(contours[i])
            countourArea=cv2.contourArea(contours[i])
            ratio=countourArea/(w*h)
            
            if not (ratio >=0.6 or ratio <= 0.4 or countourArea <= 100):
                cv2.drawContours(img,[contours[i]],0,(255,0,255),3)
                centers=getCenters(img,contours)
        cv2.imshow('s',img)
    	
    # the 'q' button is set for break
        if cv2.waitKey(55) & 0xFF == ord('q'):
            break
    else:
        break
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()


