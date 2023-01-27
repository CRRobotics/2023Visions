import cv2
import numpy as np
import constants
class functions:
	#returns the height off the ground of the supplied pixel
    def heightFromDistance(pixelY, pixelDist):
        return height-pixelDist*math.cos((pixelDist*0.059)+constants.cameraMountAngle)

    def maskGenerator(self,img,lower_color,higher_color):
        img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        img=cv2.blur(img, (5,5)) 
        mask=cv2.inRange(img,lower_color,higher_color)    
        kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
        mask=cv2.erode(mask,kernel1,iterations=3)
        mask=cv2.dilate(mask,kernel1,iterations=1)       
        return mask


    def findContours(self,mask):
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        ConvexHull=[cv2.convexHull(contour) for contour in contours]
        return ConvexHull
        # return contours
    


    def filter_out_contours_that_doesnot_look_like_square(self,contours):  
        filteredContours=[]
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            m=w/h#show how perfect the square i
            if m <2 and m >=0.5 :
                filteredContours.append(contour)
        return filteredContours

   
   
   
    def find_biggest_contour(self,contours):
        sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
        biggest_contour=sortedContours[0]
        return biggest_contour

        
    def find_and_draw_center_of_target(self,frame,biggest_contour):
        x,y,w,h=cv2.boundingRect(biggest_contour)
        cv2.drawContours(frame,[biggest_contour],0,(255,0,255),3)
        moments = cv2.moments(biggest_contour)
        if moments['m00'] !=0:
            center=((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
            cv2.circle(frame, center, 3, (0, 0, 255), -1)
            return center



    def get_horizontal_angle(self,center_of_frame,center_of_target):#reletive to camera
        x_center_of_frame,   y_center_of_frame   = center_of_frame
        x_center_of_target,  y_center_of_target  = center_of_target
        angle_to_turn_horizontal = (x_center_of_target-x_center_of_frame)*constants.horizontal_rad_per_pixle
        return angle_to_turn_horizontal




    def get_vertical_angle(self,center_of_frame,center_of_target):#reletive to camera
        x_center_of_frame,   y_center_of_frame   = center_of_frame
        x_center_of_target,  y_center_of_target  = center_of_target
        angle_to_target_vertical = (y_center_of_target-y_center_of_frame)*constants.vertical_rad_per_pixle
        return angle_to_target_vertical



    def correct_horizontal_angle():
        pass

    
    def correct_vertical_angle():
        pass

    

    # def putCenterPixelIn(self,frame):
    #     h, w, c = frame.shape
    #     centerPixel = (int(w / 2), int(h / 2))
    #     cv2.circle(frame, centerPixel, 3, (255, 0, 255), -1)