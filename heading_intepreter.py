import math


# Gets x pixel location and derives a horizontal polar heading to represent this point
# Built in 78 degree field of view
# (x/960)*39
def get_heading_x(x):
    return (x/960)*27.19

# Gets y pixel location and derives a vertical polar heading to represent this point
# Built in 58.5 degree field of view
# (x/960)*39
def get_heading_y(y):
    return (y/960)*27.19
