import cv2 as cv
import pyautogui
import numpy as np
from pynput.mouse import Listener
from PIL import Image
import time
import math
import os
import pytesseract as pya
import argparse
import time
import ctypes
from pynput.mouse import Button, Controller as MouseController


#################################################################################
#Start Citation

# Hodka
# May 5, 2014
# Simulate Python keypresses for controlling a game
# 1.0
# source code
# https://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

#End Citation
#################################################################################


#OCR Tesseract
def tesseract(frame):

    pya.pytesseract.tesseract_cmd = r"C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe"

    #first we need to convert the image from color to gray scale
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #fliping the white and black helps with OCR Tesseract to be cleaner
    frame = cv.bitwise_not(frame)
    #then we need to blur the image, using median blur was the best choice
    frame = cv.medianBlur(frame,5)

    filename = "{}.png".format(os.getpid())
    cv.imwrite(filename, frame)
    #converts the image into text
    text = pya.image_to_string(Image.open(filename), config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    os.remove(filename)
    # print(text)

    return text

#solution: mask the weapon or reduce size,
#
def nothing(x):
    pass

#move character ingame
def moveto_InGame(dx,dy):
    crossHairOffsetY = 0
    x, y = pyautogui.position()
    #because the actual cursor lies 30 pixels below the crosshair
    dx = dx*0.5
    dy = dy*0.5
    if  math.fabs(dx) < 5:
        dx = 0
    if math.fabs(dy) < 5:
        dy = 0
    pyautogui.moveTo(x+dx,y+dy)

#event handlers
def on_move(x, y):
    x1, y1 = pyautogui.position()
    dx = x1 - x
    dy = y1 - y
    return x, y

def on_click(x, y, button, pressed):
    global point, point_selected
    if pressed:
        print(button)
        point = (x,y)
        point_selected = True
    else:
        point_selected = False

def on_scroll(x, y, dx, dy):
    pass


#method gets mouse pos if neccessary
def getMousePos():
    #remember, x and y are of image screen coordinates
    x, y = pyautogui.position()
    return x, y

#absolute position of crosshair
def getCrossHair(x, y):
    # remember, x and y are of image screen coordinates, the crosshare coordinate are:
    crossHairOffsetY = 0
    return x, y-crossHairOffsetY

#best values, dont delete
#prev vals (15,51,19,92,255,255)
#(23,72,99,99,178,205)
#(102,0,0,255,255,147)

cv.namedWindow("TrackBars")
cv.createTrackbar("L-H", "TrackBars", 102, 120, nothing)
cv.createTrackbar("L-S", "TrackBars", 0, 20, nothing)
cv.createTrackbar("L-V", "TrackBars", 0, 20, nothing)
cv.createTrackbar("U-H", "TrackBars", 255, 255, nothing)
cv.createTrackbar("U-S", "TrackBars", 255, 255, nothing)
cv.createTrackbar("U-V", "TrackBars", 147, 155, nothing)


cv.namedWindow("parameter")
cv.createTrackbar("ls", "parameter", 0, 50000, nothing)
cv.createTrackbar("us", "parameter", 50000, 50000, nothing)
cv.createTrackbar("als", "parameter", 0, 50000, nothing)
cv.createTrackbar("aus", "parameter", 50000, 50000, nothing)

#mouse data from hevent handler
point = None
point_selected = False
#data for optical flow
old_points = np.array([[]])
selection = list()

# display screen resolution, get it from your OS settings
SCREEN_SIZE = (1920, 1080)

#time to get game started
time.sleep(5)

#set up for the optical flow algo, neccessary
#need an old frame
img = pyautogui.screenshot()
nframe = np.array(img)
height = 1080
width = 1920
old_gray = cv.cvtColor(nframe, cv.COLOR_BGR2GRAY)
old_gray = old_gray[0:height, 0:width]
#lucas-Kanade Params:
#first tuple parameter is the window size of the tracking point
#second parameter is the tracking level accuracy, putting the number up doesnt neccessarily make the accuracy better
lk_params = dict(winSize = (15,15),
                 maxLevel = 2,
                 criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))




#prev vals (15,51,19,92,255,255)
#(23,72,99,99,178,205)


# this pos is the actual detection and contour tracking system, modify at your own risk
def hsvContourDetection(frame):
    #the contour we are trying to find
    switchedOn = None
    #access to global functions if we need them
    global point, point_selected, old_points
    #tracker that is currently switched on
    #important for when tuning is neccessary
    frame = np.array(frame)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    l_h = cv.getTrackbarPos("L-H", "TrackBars")
    l_s = cv.getTrackbarPos("L-S", "TrackBars")
    l_v = cv.getTrackbarPos("L-V", "TrackBars")
    u_h = cv.getTrackbarPos("U-H", "TrackBars")
    u_s = cv.getTrackbarPos("U-S", "TrackBars")
    u_v = cv.getTrackbarPos("U-V", "TrackBars")
    lowersides = cv.getTrackbarPos("ls", "parameter")
    #uppersides = cv.getTrackbarPos("us", "parameter")
    lowerarea = cv.getTrackbarPos("als", "parameter")
    #upperarea = cv.getTrackbarPos("aus", "parameter")
    lower_red = np.array([l_h, l_s, l_v])
    upper_red = np.array([u_h, u_s, u_v])
    kernel = np.ones((5, 5), np.uint8)
    #image processing
    mask = cv.inRange(hsv, lower_red, upper_red)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    mask = cv.dilate(mask, kernel, iterations=6)
    mask = cv.erode(mask, kernel, iterations=4)
    flag = False
    px = 0
    py = 0

    #check if mouse is within bounds then check image***
    #check if inside teh active window, half rn
    xm, ym = getMousePos()
    if xm < 1920 and ym < 1080:
        if point_selected is True:
            crossHairOffsetY = 0
            px, py = point
            py = py - crossHairOffsetY
            #print(point, xm, ym)
            if px <= 1920 and py <= 1080:
                #cv.circle(frame, (px, py), 5, (0, 255, 0), -1)
                flag = True



    _, contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #have to try slicing contours threshold
    #try scaling the bounding rectangles

    for cnt in contours:
        approx = cv.approxPolyDP(cnt, 0.001 * cv.arcLength(cnt, True), True)
        (x, y, w, h) = cv.boundingRect(cnt)
        xw = x + w
        yh = y + h
        # ratio of width to height
        ratio = w / h
        al = len(approx)
        area = cv.contourArea(cnt)
        # print(area, ratio)
        # if flag is set true, the
        if area >= lowerarea:
            if al >= lowersides:
                # if xw >= px >= x:
                #     if yh >= py >= y:
                #check if mouse pointer is inside the bounding box
                # print((xw, yh), (px, py), (x, y))
                if (area >= 900) and ratio < 0.8 and flag:
                    switchedOn = cnt
                    if area > 5000:
                        # mask = cv.erode(mask, kernel, iterations=5)
                        pass
                    else:
                        # mask = cv.erode(mask, kernel, iterations=3)
                        pass
                    M = cv.moments(cnt)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"] - h // 4)
                    selection.clear()
                    selection.append((cX, cY))
                    cX, cY = selection[0]
                    # retrieve valid detections point
                    old_points = np.array([[cX, cY]], dtype=np.float32)
                    np.append(old_points, [[px, py]])
                    cv.drawContours(frame, [approx], 0, (255, 255, 255), 4)
                    # draw the contour and center of the shape on the image
                    cv.rectangle(frame, (x, y), (xw, yh), (255, 255, 255), 2)
                    cv.circle(frame, (cX, cY), 15, (0, 0, 255), 2)
                    # cv.circle(mask, (cX, cY), 20, (0, 0, 255), 2)
                    cv.putText(frame, "combine", (cX - 20, cY - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    # print((cX, cY), (px, py), "detected")


        if len(selection) == 1:
            ox, oy = selection[0]
            # print(old_points, "<-old points after selection",(xw, yh))
            if xw >= ox >= x:
                if yh >= oy >= y:
                    # print((xw, yh), (ox, oy), (x, y))
                    if (area >= 900) and ratio < 0.8:
                        switchedOn = cnt
                        M = cv.moments(cnt)
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"] - h//4)
                        selection.clear()
                        selection.append((cX, cY))
                        cX, cY = selection[0]
                        # retrieve valid detections point
                        old_points = np.array([[cX, cY]], dtype=np.float32)
                        np.append(old_points, [[px, py]])
                        # draw the contour and center of the shape on the image
                        cv.rectangle(frame, (x, y), (xw, yh), (255, 255, 255), 2)
                        cv.drawContours(frame, [approx], 0, (255, 255, 255), 4)
                        cv.circle(frame, (cX, cY), 15, (0, 0, 255), 2)
                        # cv.circle(mask, (cX, cY), 15, (0, 0, 255), 2)
                        cv.putText(frame, "combine", (cX - 20, cY - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),2)
                        # print((cX, cY), (ox, oy), "tracking")
    #debugging screens
    cv.imshow('frame', frame)
    # cv.imshow("Mask", mask)
    return frame

#controller for mouse
mouse = MouseController()

#mouse event listener context manager; encapsulates the original while loop so we can detect mouse events
with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    while True:
        #######
        #the tesseract algo is too slow so i commented out for now, if you can make it run fast that would be swell ;)
        ######
        # make a screenshot
        img = pyautogui.screenshot()
        # img = pyautogui.screenshot(region=(0, 0, 300, 400))
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # make a screenshot

        #screenshot the region with the health and ammo
        healthFrame = pyautogui.screenshot(region=(130, 975, 115, 75))
        ammoFrame = pyautogui.screenshot(region=(1660, 975, 115, 75))

        #convert screenshot into values
        healthFrame = np.array(healthFrame)
        ammoFrame = np.array(ammoFrame)

        #convert values into text
        healthText = tesseract(healthFrame)
        ammoText = tesseract(ammoFrame)

        dict  = {}
        dict["health"] = healthText
        dict["ammo"] = ammoText
        print(dict)

        ###############################
        if(healthText == ""):
            healthText = 0

        #to make character run backwards when health is lower than 40
        if(int(healthText) > 40 and healthText != ""):
            #shift
            ReleaseKey(0x2A)
            #'s'
            ReleaseKey(0x1F)
        if(int(healthText) < 40 and healthText != ""):
            PressKey(0x2A)
            PressKey(0x1F)
        ################################

        #to reload weapon when ammo hits 3 bullets
        if(ammoText == ""):
            ammoText = 0

        if(int(ammoText) > 3 and ammoText != ""):
            #'r'
            ReleaseKey(0x13)
        if(int(ammoText) < 3 and ammoText != "" and int(ammoText) != 0):
            PressKey(0x13)



        height = 1080
        width = 1920
        image = frame[0:height, 0:width]
        # works by reference to image
        det = hsvContourDetection(image)
        # modified image for use in the LK optical flow algo
        gray_frame = det
        # this part is the control algorithm for find the optical flow points and calculating new mouse distance
        if len(selection) == 1 and point is not None:
            #take mouse point from click
            px, py = point
            #target found, a list of target selections
            cX, cY = selection[0]
            cx, cy = getCrossHair(px, py)
            #change in mouse position neccessary to lock on to target
            dx = cX - cx
            dy = cY - cy

            # if(healthText < 40 and (abs(dx - dy) > 0) and (abs(dx - dy) < 10)):
            #     mouse.press(Button.left)

            print((dx, dy), (cX, cY), (cx, cy), (px, py))
            moveto_InGame(dx, dy)
            #print("selected!", selection)
            new_points, status, error = cv.calcOpticalFlowPyrLK(old_gray, gray_frame, old_points, None, **lk_params)
            #print(new_points)
            selection.clear()
            nx, ny = (new_points[0][0], new_points[0][1])
            ox,oy = old_points.ravel()
            old_points = new_points
            np.append(old_points, [[cX, cY]])
            np.append(old_points, [[ox, oy]])
            x, y = new_points.ravel()
            #mark the tracking points for proper tracking
            cv.circle(det, (x, y), 5, (255, 0, 0), -1)
            cv.circle(det, (ox, oy), 5, (255, 0, 0), -1)

        old_gray = gray_frame.copy()
        #display everything
        cv.imshow("screen", det)
        # if the user clicks q, it exits
        if cv.waitKey(1) == ord("q"):
            #never change
            listener.stop()
            break
    #never change
    listener.join()






# make sure everything is closed when exited
cv.destroyAllWindows()
out.release()
