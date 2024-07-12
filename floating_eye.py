#!/usr/bin/python

from picamera import PiCamera
import numpy as np
import cv2 
import pigpio
from time import time, sleep

#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
#face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

WIDTH =  640
HEIGHT = 480

PIGPIO = pigpio.pi()

camera = PiCamera()
camera.resolution = (WIDTH, HEIGHT)

class Point:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "X:{} Y:{}".format(self.X, self.Y)

class Rect:
    def __init__(self, x, y, w, h):
        self.X = x
        self.Y = y
        self.W = w
        self.H = h

    def __str__(self):
        return "X:{} Y:{} W:{} H:{}".format(self.X, self.Y, self.W, self.H)

class Servo:
    def __init__(self, pin, home, min, max, range):
        self.Pin = int(pin)
        self.Home= int(home)
        self.Min = int(min)
        self.Max = int(max)
        self.Range = int(range)
        PIGPIO.set_mode(self.Pin, pigpio.OUTPUT)
        PIGPIO.set_PWM_frequency(self.Pin, 50)

    def turnOff(self):
        PIGPIO.set_servo_pulsewidth(self.Pin, 0)

    def goHome(self):
        PIGPIO.set_servo_pulsewidth(self.Pin, self.Home)
        sleep(1)
        self.turnOff()


    def goTo(self, v):
        p = self.Min+((int(v)*(self.Max-self.Min))//self.Range)
        PIGPIO.set_servo_pulsewidth(self.Pin, p)


RL = Servo(13, 1500, 1750, 1100, WIDTH)
UD = Servo(12, 1550, 1950, 2300, HEIGHT)

def goIdle():
    RL.goHome()
    UD.goHome()

def getFaces():
    img = np.empty((WIDTH * HEIGHT * 3), dtype=np.uint8)
    try:
        camera.capture(img, 'bgr')
    except Exception as e:
        print("Exception: {}".format(e))
        return []
    img = np.reshape(img,(HEIGHT, WIDTH, 3)) 
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    return face_cascade.detectMultiScale(img, 1.5, 3, minSize=(20,20), maxSize=(200,200))

def findBiggest(faces):
    index = 0
    area  = 0
    for n in range(len(faces)):
        (x,y,w,h) = faces[n]
        if w*h > area:
            area=w*h
            index=n
    (x,y,w,h) = faces[index]        
    return Rect(x,y,w,h)

def target(r):
    # use integer division to maintain integer math
    return Point(r.X-(r.W//2), r.Y+(r.H//3))


def goToFace(rect):
    t = target(rect)
    RL.goTo(t.X)
    UD.goTo(t.Y)
    
goIdle()
idle = True

lastDetection = time()

while True:
    faces = getFaces()
    if len(faces)>0:
        goToFace(findBiggest(faces))
        idle = False
        lastDetection = time()
    delta = time() - lastDetection
    if (not idle) and (delta > 6):
        goIdle()
        idle = True
