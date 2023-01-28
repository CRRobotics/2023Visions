import cv2 as cv
from math import atan2, cos, sin, sqrt, pi
import numpy as np
from realsense_camera import *
import cv2
#load real sense camera
rs=RealsenseCamera()
import functions as f

import constants

 
def drawAxis(img, p_, q_, color, scale):
  p = list(p_)
  q = list(q_)
 
  ## [visualization1]
  angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
  hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
 
  # Here we lengthen the arrow by a factor of scale
  q[0] = p[0] - scale * hypotenuse * cos(angle)
  q[1] = p[1] - scale * hypotenuse * sin(angle)
  cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
 
  # create the arrow hooks
  p[0] = q[0] + 9 * cos(angle + pi / 4)
  p[1] = q[1] + 9 * sin(angle + pi / 4)
  cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
 
  p[0] = q[0] + 9 * cos(angle - pi / 4)
  p[1] = q[1] + 9 * sin(angle - pi / 4)
  cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
  ## [visualization1]
 
def getOrientation(pts, img):
  ## [pca]
  # Construct a buffer used by the pca analysis
  sz = len(pts)
  data_pts = np.empty((sz, 2), dtype=np.float64)
  for i in range(data_pts.shape[0]):
    data_pts[i,0] = pts[i,0,0]
    data_pts[i,1] = pts[i,0,1]
 
  # Perform PCA analysis
  mean = np.empty((0))
  mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, mean)
 
  # Store the center of the object
  cntr = (int(mean[0,0]), int(mean[0,1]))
  ## [pca]
 
  ## [visualization]
  # Draw the principal components
  cv.circle(img, cntr, 3, (255, 0, 255), 2)
  p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
  #p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
  drawAxis(img, cntr, p1, (255, 255, 0), 1)
  #drawAxis(img, cntr, p2, (0, 0, 255), 5)
 
  angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
  ## [visualization]
 
  # Label with the rotation angle
  '''changed the lable to add extra 180 degree'''
  # label = "  Rotation Angle: " + str(-int(np.rad2deg(angle)) - 90) + " degrees"
  label = "  Rotation Angle: " + str(-int(np.rad2deg(angle)) - 90+180) + " degrees"
  #textbox = cv.rectangle(img, (cntr[0], cntr[1]-25), (cntr[0] + 250, cntr[1] + 10), (255,255,255), -1)
  cv.putText(img, label, (cntr[0], cntr[1]), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv.LINE_AA)
 
  return angle

# Load the image
while True:
  ret, frame, depth_frame = rs.get_frame_stream()


  'CONE'
  if ret:
    mask2=f.maskGenerator2(frame)
    
    
    contours2=f.findContours(mask2)    
    if len(contours2) >0:
        biggest_contour2=f.find_biggest_contour(contours2)
        center2=f.find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
        point_x2,point_y2=center2
        distance_cm2= depth_frame[point_y2,point_x2]/10#y,x
        cv2.putText(frame,'{}cm,Cone'.format(distance_cm2),(point_x2,point_y2-10),0,1,(0,0,255),2)

#        #solidity test
#        x,y,w,h=cv2.boundingRect(biggest_contour2)
#        ratio=cv2.contourArea(biggest_contour2)/(w*h)
#        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),5)
#        cv2.putText(frame,str(ratio),(point_x2,point_y2+80),0,1,(0,0,0),2)
#         if ratio>=0.7:
#           orientation=0
#           cv2.putText(frame,'Rotation angle is 0 degrees',(point_x2,point_y2+100),0,1,(255,0,0),2)


# #get orientation
#         else:
#           orientation=getOrientation(biggest_contour2,frame)

        
        orientation=getOrientation(biggest_contour2,frame)
#play with depth map
        Array =biggest_contour2

    
        a=Array.tolist()
        b=[]#position of convex points
        for i in a:
            for c in i:
                c=tuple(c)
                b.append(c)
        
        d=[]#matching positions of b on depth map
        for i in b:
            x,y=i
            e=depth_frame[y,x]
            d.append(e)

        
        
        max=0
        position1=0#index in d
        for i in range(len(d)):
            if d[i]>=max:
                min=d[i]
                position1=i
        
        min=99999999999
        position2=0#index in d
        for i in range(len(d)):
            if d[i]<=min:
                min=d[i]
                position2=i
        close=b[position1]
        far=b[position2]
        
        #cv2.arrowedLine(frame, close, far, (255,0,0), 8, 8, 0, 0.1)
        if cv2.waitKey(1) & 0xFF == ord('w'):#if
            print(b)
    #cv2.imshow('mask2',mask2) 
      
    cv2.imshow('bgr',frame)
    if cv2.waitKey(2) & 0xFF == ord('q'):
      break





        


   
rs.release()
cv2.destroyAllWindows()
