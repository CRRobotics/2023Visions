from manim import *
import math


THETA_C_R = 35

class FieldReferenceFrame(Scene):
    def construct(self):
        field_rec = Rectangle(WHITE, 6, 12)
        f_ref_x = Arrow(ORIGIN, field_rec.get_left() + [1, 0, 0], buff=0)
        f_x_lbl = MathTex("X_g +", font_size = 35).move_to(f_ref_x.end + [-.3, 0, 0])
        f_ref_y = Arrow(ORIGIN, field_rec.get_bottom() + [0, 1, 0], buff=0)
        f_y_lbl = MathTex("Y_g +", font_size = 35).move_to(f_ref_y.end + [0, -.2, 0])

        field= VGroup(field_rec, f_ref_x, f_ref_y, f_x_lbl, f_y_lbl)

        apriltag_labels = [
            Tex("ID:3", color=YELLOW),
            Tex("ID:2", color=YELLOW),
            Tex("ID:1", color=YELLOW),
            Tex("ID:8", color=YELLOW),
            Tex("ID:7", color=YELLOW),
            Tex("ID:6", color=YELLOW),
        ]

        points = [
            field.get_corner(DR)+ [.5, 1, 0],
            field.get_corner(DR)+ [.5, 2, 0],
            field.get_corner(DR)+ [.5, 3, 0],
            field.get_corner(DL)+ [-.5, 1, 0],
            field.get_corner(DL)+ [-.5, 2, 0],
            field.get_corner(DL)+ [-.5, 3, 0]
        ]

        for label, point in list(zip(apriltag_labels, points)):
            label.move_to(point)
            self.add(label)
        robot_rect = Rectangle(RED, 1, 2).move_to([2, -1, 0])
        r_ref_x = Arrow(robot_rect.get_center(), robot_rect.get_left(), buff=0, color=RED)
        r_ref_y = Arrow(robot_rect.get_center(), robot_rect.get_bottom(), buff=0, color = RED)
        r_ref_y.stroke_width = r_ref_x.stroke_width
        r_ref_x.tip_length = r_ref_y.tip_length
        r_x_lbl = MathTex("X_r +", font_size = 25, color=RED).move_to(r_ref_x.get_top())
        r_y_lbl = MathTex("Y_r +", font_size = 25, color=RED).move_to(r_ref_y.get_left() + [-.2, 0, 0])

        robot_frame = VGroup(robot_rect, r_ref_x, r_ref_y, r_x_lbl, r_y_lbl)

        cam_vlength =1
        c0 = Dot(robot_frame.get_left()+[0, -.3, 0], color = GREEN)
        c0_ref_x = Arrow(c0.get_center(), 
            c0.get_center() + [-cam_vlength * math.cos(math.radians(THETA_C_R)), -cam_vlength * math.sin(math.radians(THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )
        c0_x_lbl = MathTex("X_c +", font_size = 25, color=GREEN).move_to(c0_ref_x.get_bottom() + [0, -.3, 0])

        c0_ref_y = Arrow(c0.get_center(), 
            c0.get_center() + [-cam_vlength * math.cos(math.radians(90 + THETA_C_R)), -cam_vlength * math.sin(math.radians(90 + THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )    
        c0_y_lbl = MathTex("Y_c +", font_size = 25, color=GREEN).move_to(c0_ref_y.end + [0, -.2, 0])
    
        camera0 = VGroup(c0, c0_ref_x, c0_x_lbl, c0_ref_y, c0_y_lbl)
        c2 = Dot(robot_frame.get_left()+[0, +.3, 0], color = GREEN)
        c2_ref_x = Arrow(c2.get_center(), 
            c2.get_center() + [-cam_vlength * math.cos(math.radians(THETA_C_R)), cam_vlength * math.sin(math.radians(THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )
        c2_x_lbl = MathTex("X_c +", font_size = 25, color=GREEN).move_to(c2_ref_x.end + [.2, .2, 0])

        c2_ref_y = Arrow(c2.get_center(), 
            c2.get_center() + [cam_vlength * math.cos(math.radians(THETA_C_R+90)), -cam_vlength * math.sin(math.radians(THETA_C_R + 90)), 0],
            buff=0, 
            color=GREEN
        )    
        c2_y_lbl = MathTex("Y_c +", font_size = 25, color=GREEN).move_to(c2_ref_y.get_left())
        
        camera2 = VGroup(c2, c2_ref_x, c2_x_lbl, c2_ref_y, c2_y_lbl)


        robot_full = VGroup(robot_frame, camera0, camera2)
        robot_full.rotate(-PI/6, about_point=robot_frame.get_center())

        self.add(field, robot_full)

class getting_rfromc(Scene):
    def construct(self):
        robot_rect = Rectangle(RED, 1, 2).move_to([2, 0, 0])
        r_ref_x = Arrow(robot_rect.get_center(), robot_rect.get_left(), buff=0, color=RED)
        r_ref_y = Arrow(robot_rect.get_center(), robot_rect.get_bottom(), buff=0, color = RED)
        r_ref_y.stroke_width = r_ref_x.stroke_width
        r_ref_x.tip_length = r_ref_y.tip_length
        r_x_lbl = MathTex("X_r +", font_size = 25, color=RED).move_to(r_ref_x.get_top())
        r_y_lbl = MathTex("Y_r +", font_size = 25, color=RED).move_to(r_ref_y.get_left() + [-.2, 0, 0])

        robot_frame = VGroup(robot_rect, r_ref_x, r_ref_y, r_x_lbl, r_y_lbl)

        cam_vlength =1
        c0 = Dot(robot_frame.get_left()+[0, -.3, 0], color = GREEN)
        c0_ref_x = Arrow(c0.get_center(), 
            c0.get_center() + [-cam_vlength * math.cos(math.radians(THETA_C_R)), -cam_vlength * math.sin(math.radians(THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )
        c0_x_lbl = MathTex("X_c +", font_size = 25, color=GREEN).move_to(c0_ref_x.get_bottom() + [0, -.3, 0])

        c0_ref_y = Arrow(c0.get_center(), 
            c0.get_center() + [-cam_vlength * math.cos(math.radians(90 + THETA_C_R)), -cam_vlength * math.sin(math.radians(90 + THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )    
        c0_y_lbl = MathTex("Y_c +", font_size = 25, color=GREEN).move_to(c0_ref_y.end + [0, -.2, 0])
    
        camera0 = VGroup(c0, c0_ref_x, c0_x_lbl, c0_ref_y, c0_y_lbl)
        c2 = Dot(robot_frame.get_left()+[0, +.3, 0], color = GREEN)
        c2_ref_x = Arrow(c2.get_center(), 
            c2.get_center() + [-cam_vlength * math.cos(math.radians(THETA_C_R)), cam_vlength * math.sin(math.radians(THETA_C_R)), 0], 
            buff=0, 
            color=GREEN
        )
        c2_x_lbl = MathTex("X_c +", font_size = 25, color=GREEN).move_to(c2_ref_x.end + [.2, .2, 0])

        c2_ref_y = Arrow(c2.get_center(), 
            c2.get_center() + [cam_vlength * math.cos(math.radians(THETA_C_R+90)), -cam_vlength * math.sin(math.radians(THETA_C_R + 90)), 0],
            buff=0, 
            color=GREEN
        )    
        c2_y_lbl = MathTex("Y_c +", font_size = 25, color=GREEN).move_to(c2_ref_y.get_left())
        
        camera2 = VGroup(c2, c2_ref_x, c2_x_lbl, c2_ref_y, c2_y_lbl)


        robot_full = VGroup(robot_frame, camera0, camera2)
        robot_full.scale(2.5)


        self.add(robot_full)
        self.wait(1)

        self.play(FadeOut(r_x_lbl, r_y_lbl), run_time = .5)

        line_for_x = DashedLine(c2_ref_y.get_right(), ORIGIN, 0)
        self.play(Create(line_for_x))