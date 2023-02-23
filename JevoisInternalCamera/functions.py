import cv2
import numpy as np
import math
import re

lower_yellow=np.array([0,0,0])

higher_yellow=np.array([40,255,255])
def maskGenerator1(img):#for cube
    img=cv2.blur(img, (5,5)) 
    #img= cv2.GaussianBlur(img, (15, 15), 0)
    b,g,r =cv2.split(img)     
    diff = cv2.subtract(b,g)
    ret, mask = cv2.threshold(diff, 8, 255, cv2.THRESH_BINARY)
    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    mask=cv2.erode(mask,kernel1,iterations=3)
    mask=cv2.dilate(mask,kernel1,iterations=1) 
    '''
    Make a hsv double check for cubes
    '''
    return mask
def maskGenerator2(img,lower_color,higher_color):

    #bgr math
    # img==cv2.blur(img, (5,5)) 
    b,g,r=cv2.split(img)     
    diff = cv2.subtract(g, b)
    ret, maska = cv2.threshold(diff, 8, 255, cv2.THRESH_BINARY)

    kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))

    #ret,maska = cv2.threshold(maska, 28, 255, cv2.THRESH_BINARY)
    # maska=cv2.dilate(maska,kernel1,iterations=5) 
    
    maska=cv2.erode(maska,kernel1,iterations=5)
    # maska=cv2.dilate(maska,kernel1,iterations=1) 
    radius = 5
    ksize = 2 * radius + 1
    maska=cv2.GaussianBlur(maska, (radius, radius), radius) 
    # maska = cv2.Canny(maska,100,200)
    return maska
 
# def maskGenerator2(img,lower_color,higher_color):

#     #bgr math
#     # img==cv2.blur(img, (5,5)) 
#     b,g,r=cv2.split(img)     
#     diff = cv2.subtract(g, b)
#     ret, maska = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)

#     kernel1=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
#     # 
#     # maska=cv2.dilate(maska,kernel1,iterations=5) 
    
#     maska=cv2.erode(maska,kernel1,iterations=3)
#     maska=cv2.dilate(maska,kernel1,iterations=3) 
    

#     # hsv double check
#     img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#     maskb=cv2.inRange(img,lower_color,higher_color) 
#     # maskb=cv2.dilate(maskb,kernel1,iterations=1)
#     maskab = cv2.bitwise_and(maska, maskb)
#     return maskab
#     return maska

def circularmask(img):
    radius2 = 150
    ww, hh, _ = img.shape
    xc = hh // 2
    yc = ww // 2

    print(xc, yc)
    
    mask2 = np.zeros_like(img)
    mask = cv2.circle(mask2, (xc,yc), radius2, (255,255,255), -1)
    dst = cv2.bitwise_and(img, mask2)
    return dst



# def maskGenerator3(img):
#     img==cv2.blur(img, (5,5))
#     b,g,r=cv2.split(img)
#     _, maskr = cv2.threshold(r, 50, 255, cv2.THRESH_BINARY)
#     _, maskg = cv2.threshold(g, 50, 255, cv2.THRESH_BINARY)
#     masky = cv2.bitwise_and(maskr, maskg)
#     _, maskb = cv2.threshold(b, 50, 255, cv2.THRESH_BINARY)
#     maskb = cv2.bitwise_not(maskb)
#     mask = cv2.bitwise_and(masky, maskb)
#     return mask

def findContours(mask):
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours=[cv2.convexHull(contour) for contour in contours]
    return contours


def find_biggest_contour(contours):
    sortedContours = sorted(contours, key=lambda contour: -cv2.contourArea(contour))
    biggest_contour=sortedContours[0]
    return biggest_contour

def find_center_and_draw_center_and_contour_of_target(frame,biggest_contour):
    cv2.drawContours(frame,[biggest_contour],0,(255,0,255),3)
    moments = cv2.moments(biggest_contour)
    if moments['m00'] !=0:
        center=((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
        cv2.circle(frame, center, 3, (0, 0, 255), -1)
        return center
    
'''prototype'''
def angle_between(p1, p2, p3):
    """Calculate the angle between three points in radians."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    a = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    b = math.sqrt((x2-x3)**2 + (y2-y3)**2)
    c = math.sqrt((x3-x1)**2 + (y3-y1)**2)
    return math.acos((a**2 + b**2 - c**2) / (2 * a * b))

def smallest_angle_vertex(vertices):
    """Find the vertex with the smallest angle in a polygon."""
    angles = []
    for i in range(len(vertices)):
        p1 = vertices[i-1]
        p2 = vertices[i]
        p3 = vertices[(i+1) % len(vertices)]
        angles.append(angle_between(p1, p2, p3))
    min_angle = min(angles)
    min_index = angles.index(min_angle)
    return vertices[min_index]
def polygon(center,biggest_contour,frame):

    '''prototype'''
    #_________
    box= cv2.minAreaRect(biggest_contour)
    points = cv2.boxPoints(box)
    cv2.polylines(frame, [points], True, (0, 0, 255), 6)
    c, dimensions, angle= cv2.minAreaRect(biggest_contour)
    width,height = dimensions
    #__________

    point_x2,point_y2=center
    epsilon = 0.07 * cv2.arcLength(biggest_contour, True)
    approx = cv2.approxPolyDP(biggest_contour, epsilon, True)
    cv2.polylines(frame, [approx], True, (0, 255, 0), 6)
    cv2.putText(frame,str(len(approx)),(point_x2,point_y2-40),0,1,(255,0,0),2)

    #______
    cv2.putText(frame,str(width/height),(point_x2,point_y2+40),0,1,(0,0,255),2)
    #______
    
    return approx

def find_angle(approx,frame,center):
    point_x2,point_y2 = center
    points_array=approx.tolist()
    points_tuple=[]#position of the three major points
    for i in points_array:
        for c in i:
            c=tuple(c)
            points_tuple.append(c)
    target_point = smallest_angle_vertex(points_tuple)
    cv2.arrowedLine(frame, center, target_point,(255,0,0), 9) 
    x_final,y_final=target_point#point_x2,point_y2=center2
    #difine a lower point
    dis_center_to_target=((point_x2-x_final)**2+(point_y2-y_final)**2)**(1/2)
    lower_x=point_x2
    lower_y=point_y2-dis_center_to_target
    dis_target_to_lower=((lower_x-x_final)**2+(lower_y-y_final)**2)**(1/2)
    angle_final=math.acos(((dis_center_to_target)**2+(dis_center_to_target)**2-(dis_target_to_lower)**2)/(2*(dis_center_to_target)*(dis_center_to_target)))
    if x_final<point_x2:
        angle_final=(-1)*angle_final
    # cv2.arrowedLine(frame, center2, (lower_x,lower_y),(0,0,255), 9) 
    cv2.putText(frame,str(angle_final),(point_x2,point_y2-10),0,1,(255,0,0),2)
    return angle_final

def find_cube(frame):
        angle_final = 200
        mask1 = maskGenerator1(frame)
        contours1=findContours(mask1)   
        #contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
        if len(contours1) >0:
            biggest_contour1=find_biggest_contour(contours1)
            center1=find_center_and_draw_center_and_contour_of_target(frame,biggest_contour1)
            area1=cv2.contourArea(biggest_contour1) 
            if area1 >= 1600:
                angle_final = 100
                return True,angle_final
        return False,angle_final

def find_cone(frame):
    angle_final = 200
    mask2=maskGenerator2(frame,lower_yellow,higher_yellow)
    contours2=findContours(mask2) 
    if len(contours2) >0:
        biggest_contour2=find_biggest_contour(contours2)
        area2=cv2.contourArea(biggest_contour2) 
        if area2 >= 1600:
            center2=find_center_and_draw_center_and_contour_of_target(frame,biggest_contour2)
            approx = polygon(center2,biggest_contour2,frame)
            angle_final=find_angle(approx,frame,center2)
            return True,angle_final
    return False,angle_final