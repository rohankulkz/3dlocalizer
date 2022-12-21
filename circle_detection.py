
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import depth_detector, heading_intepreter
from plotter import Plotter

import math

from mpl_toolkits import mplot3d


import matplotlib.pyplot as plt

fig = plt.figure()

ax = plt.axes(projection="3d")




ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())


greenLower = (25, 12, 98)
greenUpper = (83, 97, 255)

list = []

x_values = []
y_values = []


last_x = 0
last_y = 0
last_radius = 0

pts = deque(maxlen=args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src=0).start()
else:
    vs = cv2.VideoCapture(args["video"])
time.sleep(2.0)


#plot = Plotter()



while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    frame = imutils.resize(frame, width=1920, height=1080)
    blurred = cv2.GaussianBlur(frame, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    if len(cnts) > 0:

        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            smooth = 10


            coord_smooth = 3
            list.append(radius)
            x_values.append(x)
            y_values.append(y)

            if(len(list) > smooth):
                list.pop(0)

            if(len(x_values)>coord_smooth):
                x_values.pop(0)

            if(len(y_values)>coord_smooth):
                y_values.pop(0)

            average = (sum(list)/len(list))

            x_average = (sum(x_values)/len(x_values))
            y_average = (sum(y_values)/len(y_values))

            y_heading = heading_intepreter.get_heading_x(x_average-960)

            z_heading = heading_intepreter.get_heading_y(-(y_average-720))

            depth = depth_detector.getDepth((average*2),x_average-960,y_average-720)
            #
            # c_x = depth * math.sin(math.radians(x_heading)) * math.cos(math.radians(y_heading))
            #
            # c_z = -(depth * math.sin(math.radians(x_heading)) * math.sin(math.radians(y_heading)))
            #
            # c_y = depth * math.cos(math.radians(x_heading))


            c_x = depth * math.sin(math.radians(90-z_heading)) * math.cos(math.radians(y_heading))


            c_y = depth * math.sin(math.radians(y_heading)) * math.sin(math.radians(90-z_heading))


            c_z = depth * math.cos(math.radians(90-z_heading))

            #plot.plot(x=c_x, y=c_y, z=c_z)

            # z is depth

            # x is horizontal

            # y is vertical


            textData = "X: ", str(c_x), ", Y: ", str((c_y)),", Z: ", str((c_z))

            print(textData)
            #
            # ax.plot3D(c_x, c_y, c_z, 'green')
            #
            # ax.set_title('3D REPRESENTATION')
            # #plt.show()















            #print("Circle size: ", (average*2), ", X value: ", x_average, " Y values: ", y_average)

            cv2.circle(frame, (int(x_average), int(y_average)), int(average),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            if average > 5:
                # frame = cv2.putText(img=frame,
                #                     text=textData,
                #                     org=(int(x_average -200), int(y_average -120)), fontScale=0.75, thickness=2,
                # #                     fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 255))
                # frame = cv2.putText(img=frame,
                #                     text="X:" + str(int(x_average-960)) + ", Y:" + str(int(-(y_average-720))) + ", Dia: " + str(
                #                         int(average * 2)) + ", Dist: " + str(depth),
                #                     org=(int(x_average -200), int(y_average -50)), fontScale=0.75, thickness=2,
                #                     fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 255))
                frame = cv2.putText(img=frame,
                                    text="X:" + str(c_x) + ", Y:" + str(c_y) + ", Z: " + str(c_z),
                                    org=(int(x_average -200), int(y_average -50)), fontScale=0.75, thickness=2,
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 255))
                # frame = cv2.putText(img=frame,
                #                     text="X HEADING: " + str(y_heading) + " degrees, Y HEADING: "
                #                                                              + str(z_heading) + " degrees",
                #                     org=(int(x_average -200), int(y_average -120)), fontScale=0.75, thickness=2,
                #                     fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 255))



           # print("Circle size: ", ((sum(list)/len(list))*2) )

    pts.appendleft(center)
    for i in range(1, len(pts)):

        if pts[i - 1] is None or pts[i] is None:
            continue

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    grided = cv2.flip(cv2.flip(frame,1), 1)
    #
    # width = grided.get(cv2.CAP_PROP_FRAME_WIDTH)
    # height = grided.get(cv2.CAP_PROP_FRAME_HEIGHT)

    width = grided.shape[1]
    height = grided.shape[0]

    grid = 200
    #
    # for i in range (0, int(width/grid)):
    #     cv2.line(grided, (i*grid,0), (i*grid,height), (0,0,0), 1)
    #
    # for i in range(0, int(height / grid)):
    #     cv2.line(grided, (0, i*grid), (width, i*grid), (0, 0, 0), 1)

    cv2.line(grided, (0, int(height/2)), (width, int(height/2)), (0, 0, 0), 1)
    cv2.line(grided, (int(width/2), 0), (int(width/2), height), (0, 0, 0), 1)




    offset = 10

    for i in range(0, width):
        if((i-int(width/2))%grid==0):
            cv2.line(grided, (i , 0), (i , height), (0, 0, 0), 1)
            grided = cv2.putText(grided, str(i-960), org=(i,offset+30), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(0, 0, 0), thickness=1)

    for i in range(0, height):
        if((i-int(height/2))%grid==0):
            cv2.line(grided, (0 , i), (width , i), (0, 0, 0), 1)
            grided = cv2.putText(grided, str(-(i-720)), org=(offset,i), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(0, 0, 0), thickness=1)




    # print("Height: ", height)
    # print("Width: ", width)


    # for i in range (0, int(width/grid)):
    #     cv2.line(grided, (i*grid,0), (i*grid,height), (0,0,0), 1)
    #
    # for i in range(0, int(height / grid)):
    #     cv2.line(grided, (0, i*grid), (width, i*grid), (0, 0, 0), 1)

    cv2.imshow("Frame", grided)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
if not args.get("video", False):
    vs.stop()
else:
    vs.release()
cv2.destroyAllWindows()

