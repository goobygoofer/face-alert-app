#software to capture, process, and send images to server

#need to narrow down imports to save memory

#might need to be installed:
from PIL import Image  #pip install Pillow
import face_recognition#pip install face-recognition (may or may not require 
import requests        #pip install requests
import cv2             #pip install opencv-python
import numpy as np     #pip install numpy

#should not have to install:
import base64
import json
import tkinter
import threading
import time
import asyncio

class Camera:#doesn't necessarily have to be object, but useful if multiple cams on one machine
    def __init__(self):
        self.cam_port = 0  #cam port 0 should be default cam or first cam plugged in, [1:] should  be all other cams
                           #i.e. laptop default built in cam is [0], usb external cam is [1]
        
        self.cam = cv2.VideoCapture(self.cam_port, cv2.CAP_DSHOW)#actual camera object

        self.threadQueue = []    #either threads stay in obj and have to iter through obj's threads, or all objs append to global threadQueue...?
                                 #if all have their own threads and multple cams on machine, can put Camera objs in list and give
                                 #/cameras/ priority depending on etc
        
        self.priorityThreads = []#send these first! (faces sent as "priority" to server)

    def captureFrame(self):#raw image capture, put into dict with timestamp and type
        timestamp = time.time()
        retval, image = self.cam.read()
        return {'img':image, 'ts':timestamp, 'type':'stream'}

    def detectFaces(self, image):#takes dict from captureFrame {'img', 'ts', 'type'}, detects faces appends sendFrame to priorityThreads
        face_locations = face_recognition.face_locations(image['img'])
        
        if len(face_locations)==0: return #no faces
        
        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_image = image['img'][top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            imgStr = self.imgToB64String(pil_image, True)
            self.priorityThreads.append(self.sendFrame({'img': imgStr, 'ts': image['ts'], 'type':'priority'}))

    def imgToB64String(self, img, isPil=False):#if straight from cv2 capture, default on isPil=False, if pil image, put True as 2nd param
        
        if isPil:
            img = np.array(img)#appears to be only difference from processing a raw cam capture
            
        retval, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 50])#lower img quality to lighten load
        base64_bytes = base64.b64encode(buffer)
        imgStr = base64_bytes.decode('utf-8')
        return imgStr

    def processFrame(self):#main Camera fxn
        frame = self.captureFrame()
        self.detectFaces(frame)
        frame['img'] = self.imgToB64String(frame['img'])
        frame['type'] = 'stream'
        self.threadQueue.append(self.sendFrame(frame))
        time.sleep(0.1)#time between captures - change to suit needs/machine, no sleep might freeze things up -- will have to test
                       #this is why I implemented threading, sometimes processing takes a moment and the threading helped somewhat
                       #timestamp of frame is taken as frame is captured, so can be reordered server side if need be

    def sendFrame(self, frameDict):#node server running on 8080, /receiver set to receive and process images
        r = requests.post('http://localhost:8080/receiver', json=frameDict, timeout=5)

#make a Camera object and run in a loop, ctrl+c in python console to stop (crude but simple for examples sake)
cam = Camera()

def run():#this is just the method I used, threading might not even be necessary
          #just run cam.processFrame() to capture, process, and send a single frame
    while True:
        cam.threadQueue.append(cam.processFrame)#main cam fxn
        
        for toRun in cam.priorityThreads:       #run any priority threads first, faces were detected and that's important!
            t = threading.Thread(target = toRun)
            t.start()
            t.join()
        cam.priorityThreads = []#all threads started, clear to make room for more!
        
        for toRun in cam.threadQueue:#run all other threads (in this case cam.processFrame and cam.sendFrame)
                                     #detectFaces is called by processFrame, then if faces appends own sendFrame to priorityThreads
            t = threading.Thread(target = toRun)
            t.start()
            t.join()
        cam.threadQueue = []#all threads started, clear to make room for more!
