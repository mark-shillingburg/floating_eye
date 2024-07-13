#!/usr/bin/python3
from datetime import datetime
import time
import threading
import cv2
from picamera2 import Picamera2



class FaceDetector():
    def __init__(self, width=1280, height=720, minPxls=50, maxPxls=500):
        self.camera = Picamera2()
        self.minBox = (minPxls, minPxls)
        self.maxBox = (maxPxls, maxPxls)
        self.camera.preview_configuration.main.size=(width, height)
        self.camera.preview_configuration.main.format="RGB888"
        self.camera.start()
        self.cascade = cv2.CascadeClassifier('./lbpcascade_frontalface_improved.xml')
        self.faces = []
        self.stop = False
        self.t = threading.Thread(target=self.run, args=())
        self.t.start()


    def run(self):
        while not self.stop:
            image = self.camera.capture_array()
            self.faces = self.cascade.detectMultiScale(image,1.5, 3,  minSize=self.minBox, maxSize=self.maxBox)
            time.sleep(0.025)
        self.camera.stop()

    def getFaces(self):
        return self.faces

    def exit(self):
        self.stop = True
        self.t.join()


if __name__ == "__main__":
    #detector = FaceDetector(width=800, height=600)
    detector = FaceDetector()
    starttime = datetime.now()
    for x in range(400):
        faces = detector.getFaces()
        for face in faces:
            print(x, face)
        time.sleep(0.1)    
    detector.exit()
    elapsed = datetime.now() - starttime
    print("Elapsed:", elapsed)

