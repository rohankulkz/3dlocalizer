import math
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,help="max buffer size")
args = vars(ap.parse_args())


greenLower = (28, 44, 135)
greenUpper = (62, 255, 255)

list = []

x_values = []
y_values = []


last_x = 0
last_y = 0
last_radius = 0

pts = deque(maxlen=args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src=1).start()
else:
    vs = cv2.VideoCapture(args["video"])
time.sleep(2.0)



while True:

    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame



    if frame is None:
        break

    frame = imutils.resize(frame, height=1080, width=1920)
    #frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA)

    blurred = cv2.GaussianBlur(frame, (11,11), 0)
    print("Height: ", frame.shape[0])
    print("Width: ", frame.shape[1])

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)

    #cv2.imshow("frame", mask)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    average = 0
    x_average = 0
    y_average = 0
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





            print("Circle size: ", (average*2), ", X value: ", x_average, " Y values: ", y_average)

            cv2.circle(frame, (int(x_average), int(y_average)), int(average),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            print("Circle size: ", ((sum(list)/len(list))*2) )

    pts.appendleft(center)
    for i in range(1, len(pts)):

        if pts[i - 1] is None or pts[i] is None:
            continue

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


    d = 280
    color = 10
    for alpha in range(-120, 120, 10):
        color = color + 50
        for beta in range(-120, 120, 10):
            alphaRad = alpha * math.pi/180
            betaRad = beta * math.pi / 180
            floor = d * math.cos(betaRad)
            z = d * math.sin(betaRad)
            x = floor * math.cos(alphaRad)
            y = floor * math.sin(alphaRad)

            y = y + 400
            z = -z + 300

            #image = cv2.circle(flipped, (int(y), int(z)), 5, (0, 255, color), 2)

    fontScale = 1
    thick = 2

    for xx in range (0, 1920, 100):
        frame = cv2.line(frame, (xx, 0), (xx, 1080), (0, 255, 255), 1)
        for yy in range (0, 1080, 100):
            frame = cv2.line(frame, (0, yy), (1920, yy), (0, 255, 255), 1)
            txt = "(" + str(xx) + ", " + str(yy) + ")"
            cv2.putText(img=frame, text=txt,
                        org=(xx, yy), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 255), fontScale=0.25, thickness=1)


    #cv2.imshow("Frame", cv2.flip(frame,1))

    if average > 5:
        frame = cv2.putText(img=frame, text="X:" + str(int(x_average)) + ", Y:" + str(int(y_average)) + ", Dia: " + str(int(average*2)) + ", Dist: " + str((142*16.5)/(average*2)) ,
                            org=(int(x_average-50), int(y_average-50)), fontScale=0.5, thickness=1, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0,0,255))

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
if not args.get("video", False):
    vs.stop()
else:
    vs.release()