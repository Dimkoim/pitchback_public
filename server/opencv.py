#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2 as cv
import numpy as np

eye_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_eye.xml')
face_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_profileface.xml')

def run_opencv(img_str):

	nparr = np.fromstring(img_str, np.uint8)
	img = cv.imdecode(nparr, cv.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
	gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	
	faces = face_cascade.detectMultiScale(
	    gray,
	    scaleFactor=1.1,
	    minNeighbors=10,
	    minSize=(25, 25),
	    flags=cv.CASCADE_SCALE_IMAGE
	)
	
	for (x, y, w, h) in faces:
	    img = cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
	    roi_gray = gray[y:y+h, x:x+w]
	    roi_color = img[y:y+h, x:x+w]
	    eyes = eye_cascade.detectMultiScale(roi_gray,
	        scaleFactor=1.3,
	        minNeighbors=10,
	        minSize=(50, 50),
	        flags=cv.CASCADE_SCALE_IMAGE
	    )
	    for (ex,ey,ew,eh) in eyes:
	       cv.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,120),2)
	
	profiles = profile_cascade.detectMultiScale(
	    gray,
	    scaleFactor=1.1,
	    minNeighbors=10,
	    minSize=(25, 25),
	    flags=cv.CASCADE_SCALE_IMAGE
	)
	for (x, y, w, h) in profiles:
	    img = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

	img = cv.imencode('.jpg', img)[1]
	return [len(faces), len(profiles), img]
	
