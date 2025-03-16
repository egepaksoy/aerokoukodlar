import math

def calc_location(current_loc, yaw_angle, abs_distance, servo_angles):
    # Calculate the new location of the gimbal
    # based on the distance from the current location
    # and the angles of the servos

    DEG = 0.00001172485

    servo_x_angle = servo_angles[0]
    servo_y_angle = servo_angles[1]

    current_x_loc = current_loc[0]
    current_y_loc = current_loc[1]

    distance = abs_distance * math.cos(math.radians(servo_y_angle))

    abs_angle = (yaw_angle + servo_x_angle + 360) % 360

    current_x_loc += (DEG * distance * math.cos(math.radians((abs_angle + 360) % 360)))
    current_y_loc += (DEG * distance * math.sin(math.radians((abs_angle + 360) % 360)))

    return current_x_loc, current_y_loc