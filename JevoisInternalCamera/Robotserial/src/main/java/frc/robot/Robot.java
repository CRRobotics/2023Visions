// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

package frc.robot;

import edu.wpi.first.cameraserver.CameraServer;
import edu.wpi.first.wpilibj.TimedRobot;

import edu.wpi.first.cscore.CvSink;
import edu.wpi.first.cscore.CvSource;
import edu.wpi.first.cscore.MjpegServer;
import edu.wpi.first.cscore.UsbCamera;
import edu.wpi.first.cscore.VideoMode.PixelFormat;


  // Color sensor testing: REMOVE
  import edu.wpi.first.wpilibj.I2C;
  import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
  import edu.wpi.first.wpilibj.util.Color;  
  import com.revrobotics.ColorSensorV3;
  import com.revrobotics.ColorMatchResult;
  import com.revrobotics.ColorMatch;

/**
 * Uses the CameraServer class to automatically capture video from a USB webcam and send it to the
 * FRC dashboard without doing any vision processing. This is the easiest way to get camera images
 * to the dashboard. Just add this to the robotInit() method in your program.
 */
public class Robot extends TimedRobot {
  JeVoisInterface testCam;
  private final I2C.Port i2cPort = I2C.Port.kOnboard;
  private final ColorSensorV3 m_colorSensor = new ColorSensorV3(i2cPort);
  private final ColorMatch m_colorMatcher = new ColorMatch(); 

  @Override
  public void robotInit() {
    testCam = new JeVoisInterface(false);

    System.out.print("Hello, World!\n");

    //private final Color kBlueTarget = ColorMatch.makeColor(0.143, 0.427, 0.429);
    //private final Color kGreenTarget = ColorMatch.makeColor(0.197, 0.561, 0.240);
    //private final Color kRedTarget = ColorMatch.makeColor(0.561, 0.232, 0.114);
    //private final Color kYellowTarget = ColorMatch.makeColor(0.361, 0.524, 0.113);

    /*
    m_colorMatcher.addColorMatch(kBlueTarget);
    m_colorMatcher.addColorMatch(kGreenTarget);w
    m_colorMatcher.addColorMatch(kRedTarget);
    m_colorMatcher.addColorMatch(kYellowTarget); 
    */
    
    
    /*
    // Creates UsbCamera and MjpegServer [1] and connects them
    UsbCamera usbCamera = new UsbCamera("USB Camera 0", 0);
    MjpegServer mjpegServer1 = new MjpegServer("serve_USB Camera 0", 1181);
    mjpegServer1.setSource(usbCamera);
    // Creates the CvSink and connects it to the UsbCamera
    CvSink cvSink = new CvSink("opencv_USB Camera 0");
    cvSink.setSource(usbCamera);
    // Creates the CvSource and MjpegServer [2] and connects them
    CvSource outputStream = new CvSource("Blur", PixelFormat.kMJPEG, 320, 240, 30);
    MjpegServer mjpegServer2 = new MjpegServer("serve_Blur", 1182);
    mjpegServer2.setSource(outputStream);
    */



  }

 /**
     * This function is called at the start of disabled
     */
    @Override
    public void disabledInit() {

    }
    
    /**
     * This function is called periodically during disabled mode
     */
    @Override
    public void disabledPeriodic() {
        //System.out.println(testCam.getPacketRxRate_PPS());
    }
    
    
    /**
     * This function is called at the start of autonomous
     */
    @Override
    public void autonomousInit() {

    }

    /**
     * This function is called periodically during autonomous
     */
    @Override
    public void autonomousPeriodic() {
        
    }
    
    /**
     * This function is called at the start of teleop
     */
    @Override
    public void teleopInit() {
      System.out.println("Teleop Init.");
      testCam.start();
    }

    @Override
    public void teleopExit() {
      System.out.println("Exiting Exit.");
      testCam.stop();
    }



    
    /**
     * This function is called periodically during operator control
     */
    private Boolean seenCamera = false;

    @Override
    public void teleopPeriodic() {
        //int reply = testCam.sendCmd("ping");
        //if (reply != 5) {
        //  System.out.println("sendCmd odd reply " + reply);
        //}

        //System.out.println("Vision Online:" + testCam.isVisionOnline());
        //System.out.print("Target Visible: ");
        //System.out.println(testCam.isTgtVisible());
        //System.out.print("Target Angle: ");
        //System.out.println(testCam.getTgtAngle_Deg());
        //System.out.print("Target Range:");
        //System.out.println(testCam.getTgtRange_in());
        //System.out.print("Serial Packet RX Rate: ");
        //System.out.println(testCam.getPacketRxRate_PPS());
        //System.out.print("JeVois Framerate: ");
        //System.out.println(testCam.getJeVoisFramerate_FPS());
        //System.out.print("JeVois CPU Load: ");
        //System.out.println(testCam.getJeVoisCpuLoad_pct());
        //System.out.println("===============================\n\n\n");
        
    }

    /**
     * This function is called periodically during test mode
     */
    @Override
    public void testPeriodic() {
    } 

    @Override
    public void robotPeriodic() {
    }

  }
