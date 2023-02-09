



#     '''
#     color_stream = profile.get_stream(realsense.stream.color);
#     color_video_stream = rgb_stream .as('video_stream_profile');
#     color_intrinsic=depth_aligned_to_color_intrinsic = color_video_stream.get_intrinsic()
#     '''




#     '''import cv2
#     import numpy as np

#     def correct_distortion(img, camera_matrix, distortion_coeffs):
#         h, w = img.shape[:2]
#         new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w,h), 0, (w,h))
#         undistorted_img = cv2.undistort(img, camera_matrix, distortion_coeffs, None, new_camera_matrix)
#         return undistorted_img
#     '''

#     '''
#     To correct the measurement error in Intel RealSense D435's coordinates, you can try using the intrinsic parameters of the camera. 
#     The intrinsic parameters are a set of values that describe the camera's internal characteristics, 
#     including the focal length and the principal point.

#     Here is a sample Python code to correct the measurement error using the intrinsic parameters:


#     '''


#     '''
#     Using radial distortion correction:
#     less
#     Copy code
#     def correct_coordinates_radial(x, y, intrinsic_matrix, distortion_coefficients):
#         x = (x - intrinsic_matrix[0, 2]) / intrinsic_matrix[0, 0]
#         y = (y - intrinsic_matrix[1, 2]) / intrinsic_matrix[1, 1]
#         r2 = x**2 + y**2
#         x_corrected = x * (1 + distortion_coefficients[0] * r2 + 
#                         distortion_coefficients[1] * r2**2 + 
#                         distortion_coefficients[2] * r2**3)
#         y_corrected = y * (1 + distortion_coefficients[0] * r2 + 
#                         distortion_coefficients[1] * r2**2 + 
#                         distortion_coefficients[2] * r2**3)
#         return intrinsic_matrix[0, 0] * x_corrected + intrinsic_matrix[0, 2], \
#             intrinsic_matrix[1, 1] * y_corrected + intrinsic_matrix[1, 2]

#     # Example usage
#     intrinsic_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
#     distortion_coefficients = np.array([k1, k2, k3])
#     x = 100
#     y = 200
#     corrected_x, corrected_y = correct_coordinates_radial(x, y, intrinsic_matrix, distortion_coefficients)
#     Here, k1, k2, and k3 are the radial distortion coefficients. You can obtain these coefficients by calibrating the camera or using the default values provided by Intel.
#  


# def color_to_depth(color_frame, depth_frame, color_point):
#     """
#     Transform a point in the color frame to its matching point in the depth frame.

#     Parameters:
#     color_frame (ndarray): The color frame.
#     depth_frame (ndarray): The depth frame.
#     color_point (tuple): The point in the color frame, represented as (x, y).

#     Returns:
#     tuple: The matching point in the depth frame, represented as (x, y).
#     """
#     color_x, color_y = color_point
#     depth_x, depth_y = np.unravel_index(np.argmin(np.abs(depth_frame - color_frame[color_y, color_x])), depth_frame.shape)
#     return (depth_x, depth_y)
import pyrealsense2 as rs
import functions as f
import cv2

import constants
import numpy as np

def get_distance_at_point(depth_frame, x, y):

    
    
    distance = depth_frame.get_distance(x, y) 

    # Return the distance in meters
    return distance
# def get_correct_point(x,y):#get the corresponding point from the bgr frame to the depth frame.
#     #x,y is the position of the point on the color frame.
#     bgr_x_degree_pix=69/1920
#     bgr_y_degree_pix=42/1080
#     depth_x_degree_pix=87/1280
#     depth_y_degree_pix=58/720
#     x_angle=(x-960)*bgr_x_degree_pix
#     y_angle=(y-540)*bgr_y_degree_pix
#     # if x_angle >=-34 and x_angle <= 34 and y_angle >=-21 and y_angle <=21:
#     x_depth=int(((x_angle/depth_x_degree_pix)+640)//1)
#     y_depth=int(((y_angle/depth_y_degree_pix)+360)//1)
#     return x_depth,y_depth
'''
color_stream = profile.get_stream(realsense.stream.color);
color_video_stream = rgb_stream .as('video_stream_profile');
color_intrinsic=depth_aligned_to_color_intrinsic = color_video_stream.get_intrinsic()
'''
# def get_correct_point(pixelX, pixelY):
#     #D stands for depth, c for color, h for horizontal, v for verticle
#     fovDV=58 
#     fovDH=87
#     fovCV=42.5
#     fovCH=69.4
#     XdeltaFOV=fovCH-fovDH
#     YdeltaFOV=fovCV-fovDV
#     resDV=720
#     resDH=1280
#     resCV=1080
#     resCH=1920
#     XdeltaRES=resCH-resDH
#     YdeltaRES=resCV-resDV
#     dpiDV=fovDV/resDV
#     dpiDH=fovDH/resDH
#     dpiCV=fovCV/resCV
#     dpiCH=fovCH/resCH
#     fixedCRH=resCH-dpiCH*XdeltaRES
#     fixedCRV=resCV-dpiCV*YdeltaRES
#     if(abs(pixelX-resCH) > abs(resCH - XdeltaRES/2)):
#         #then the pixel needs to be cut
#         return 0,0
#     if(abs(pixelY-resCV) > abs(resCV - YdeltaRES/2)):
#         return 0,0
#     return int((fovCH/fixedCRH)*pixelX),int((fovCV/fixedCRV)*pixelY)
    
# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
#  color and depth streams
config = rs.config()
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)

config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# Start streaming
pipeline.start(config)


align_to_color = rs.stream.color
align = rs.align(align_to_color)
dists=[0,0,0,0,0]




import numpy as np

def get_correct_point(x, y, intrinsic_matrix):
    # Convert the input pixel coordinates to homogeneous coordinates
    homogeneous_coordinates = np.array([x, y, 1])
    # Multiply the homogeneous coordinates by the intrinsic matrix
    corrected_coordinates = np.dot(intrinsic_matrix, homogeneous_coordinates)
    # Normalize the corrected coordinates by the third component
    corrected_coordinates /= corrected_coordinates[2]
    return corrected_coordinates[:2]

# # Example usage
# intrinsic_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
# x = 100
# y = 200
# corrected_x, corrected_y = correct_coordinates(x, y, intrinsic_matrix)
#     Here, fx, fy, cx, and cy are the intrinsic parameters of the camera. You can obtain these parameters by calibrating the camera or using the default values provided by Intel.



while True:
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    # intr = rs.video_stream_profile(depth_frame.profile).get_intrinsics()
    
    # color_frame = frames.get_color_frame()
    # depth_frame = frames.get_depth_frame().as_depth_frame()
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    intr = rs.video_stream_profile(depth_frame.profile).get_intrinsics()
    print(intr)
    # #intr= np.array([[322.282410, 0, 320.828268], [0, 322.282410, 178.779297], [0, 0, 1]])
    # depth_intrinsics = frames.get_profile().as_video_stream_profile().get_intrinsics()

    # # Print the intrinsic parameters
    # print("fy", depth_intrinsics.fy)
    # print("(px): ", depth_intrinsics.ppx, depth_intrinsics.ppy)
    # print("Radial Distortion: ", depth_intrinsics.coeffs)
    intr = np.array([[ 639.4580688476562, 0, 643.4873046875], [0, 639.4580688476562, 359.3208923339844], [0, 0, 1]])

    


    width, height = depth_frame.get_width(), depth_frame.get_height()
   
    if not color_frame or not depth_frame:
        continue
    


    # Convert images to numpy arrays
    color_image = np.asanyarray(color_frame.get_data())#so raw  frame turns into colored pictures.
    depth_image = np.asanyarray(depth_frame.get_data())
    depth_colormap = np.asanyarray(cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.10), 2))
    
    
    # Get the distance at the center of the image

    # '''CUBE'''

    # mask1 = f.maskGenerator1(color_image)
    # contours1=f.findContours(mask1)    
    # #contours1=f.filter_out_contours_that_doesnot_look_like_square(contours1)
    # if len(contours1) >0:
    #     for contour1 in contours1:
        
        
    #         area1=cv2.contourArea(contour1) 
    #         if area1>=1600:
            
    #             center1=f.find_center_and_draw_center_and_contour_of_target(color_image,contour1)
    #             point_x1,point_y1=center1
    #             print(point_x1,point_y1)
    #             print('_________________________________________')
    #             point_x11,point_y11=get_correct_point(point_x1,point_y1)
    #             print(point_x11,point_y11)
                

                
    #            # if point_x11 > 0 and point_x11 <= width-1 and point_y11 > 0 and point_y11 <= height-1:
    
    #             distance_cm1 = get_distance_at_point(depth_frame, point_x11, point_y11)*100
                


    #             cv2.putText(color_image,f'{distance_cm1:.1f}cm',(point_x1,point_y1),0,1,(0,0,255),2)
    '''CONE'''
    mask2=f.maskGenerator2(color_image,constants.lower_yellow,constants.higher_yellow)
    contours2=f.findContours(mask2) 
    
    if len(contours2) >0:
        for contour2 in contours2:
    
            area2=cv2.contourArea(contour2) 
            if area2 >= 1600:
                center2=f.find_center_and_draw_center_and_contour_of_target(color_image,contour2)
            
                
               
               
               
                point_x2,point_y2=center2
                print('\n')
                print(point_x2,point_y2)
                print('_________________________________________')
                point_x22,point_y22=get_correct_point(point_x2,point_y2,intr)
                print(point_x22,point_y22)
                print('\n')
         
                
              
            
                #if point_x22 > 0 and point_x22 <= width-1 and point_y22 > 0 and point_y22 <= height-1:
                distance_cm2 = get_distance_at_point(depth_frame, point_x22, point_y22)*100

                cv2.putText(color_image,f'{distance_cm2:.1f}cm',(point_x2,point_y2),0,1,(0,0,255),2)

    

    # Show color and depth images
    # a=cv2.Canny(depth_colormap,100,200)
    # b=cv2.Canny(depth_image,100,200)
    cv2.imshow('Color',color_image)
    

    # Check if 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



