import libjevois as jevois
import re
import cv2
import functions as f
class Orientation:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("processing timer", 100, jevois.LOG_INFO)
        self.CPULoad_pct = "0"
        self.CPUTemp_C = "0"
        self.pattern = re.compile('([0-9]*\.[0-9]+|[0-9]+) fps, ([0-9]*\.[0-9]+|[0-9]+)% CPU, ([0-9]*\.[0-9]+|[0-9]+)C,')
        self.frame = 0
        self.angle_final = 0



    # ###################################################################################################
    def processNoUSB(self, inframe):
        self.commonProcess(inframe=inframe)
        

    # ###################################################################################################
    ## Process function with USB output
    def process(self, inframe, outframe):
        _, outimg = self.commonProcess(inframe)
        outframe.sendCv(outimg)
       

   
        
    ## Process function with USB output
    def commonProcess(self, inframe):

        frame = inframe.getCvBGR()
        frame = f.circularmask(frame)
        # Start measuring image processing time (NOTE: does not account for input conversion time):
            
        self.timer.start()
        

        '''
        Start Processing
        returns the value of angle final to robot
        value of angle_final:
        100--->Cube on record player
        200--->nothing on record player
        -3.14~3.14--->Cone on the record player and where the tip of the cone is pointing at
        
        
        '''
        
        hascones,self.angle_final = f.find_cone(frame)
        if not hascones:
            hascubes,self.angle_final = f.find_cube(frame)
            if not hascubes:
                self.angle_final = 200
            
        
        outimg = frame
        # Write a title:
        cv2.putText(outimg, "JeVois Orientation", (3, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        
        # Write frames/s info from our timer into the edge map (NOTE: does not account for output conversion time):
        fps = self.timer.stop()
        height = outimg.shape[0]
        width = outimg.shape[1]
        cv2.putText(outimg, fps, (3, height - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        
        # Convert our output image to video output format and send to host over USB:
        results = self.pattern.match(self.timer.stop())
        if(results is not None):
            self.framerate_fps = results.group(1)
            self.CPULoad_pct = results.group(2)
            self.CPUTemp_C = results.group(3)

        
        serialstr = "{%d %.2f %s %s}"%(
            self.frame,
            self.angle_final,
            self.CPULoad_pct,
            self.CPUTemp_C
        )

        jevois.sendSerial(serialstr)

        self.frame += 1
        self.frame %= 999

        return self.angle_final, outimg
        
'''Pleaes send the value of angle_final to the bot'''
'''it is in degrees of where the tip of the cone is pointing twards'''
'''tip of cone pointing up is 0'''
'''CW is positive'''
'''CCW is negetive'''
