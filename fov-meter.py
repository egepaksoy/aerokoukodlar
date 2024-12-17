import math

def fov_to_pos(fov, distance, ratio):
    x = math.sqrt(ratio[0]**2 + ratio[1]**2)

    fov_distance = distance * math.tan(math.radians(fov / 2)) * 2

    x_distance = x / fov_distance
    long_distance = ratio[0] / x_distance
    short_distance = ratio[1] / x_distance

    return long_distance, short_distance, math.sqrt((x_distance**2)*2)

print(fov_to_pos(80, 5, (640, 480)))