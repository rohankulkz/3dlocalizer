
import math



def getDepth(diameter, positionx, positiony):

    # calculate the radial distance from dynamic point (0,0)
    #   -Requires data to be converted to dynamic point system centered at (0,0) for proper functionality

    radial_distance = math.sqrt((positionx)*(positionx)+(positiony)*(positiony))

    # Calibration Constants and coefficients for digital offset calculation established
    #   -Derived from a Regression model trained with high radial camera disruption and distortion data

    a = float(1.1692 * pow(10,-12))

    d = 2.23769

    b = 0.00631924

    c = -0.016775

    correction = (a*pow(radial_distance, (2*d)))+(b*radial_distance)+c

    #print("Correction: ", str(correction))


    d_a=0.20784
    d_b=732.53
    d_c=18.7552

    p = -1.4

    depth = (d_b)/(d_a*(((diameter-correction)+p)+d_c))


    return depth




