#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2 as cv
import cv2 as cv2

img = cv.imread('foo.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

eye_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_eye.xml')
face_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv.CascadeClassifier(
    '/usr/share/opencv/haarcascades/haarcascade_profileface.xml')

faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=10,
    minSize=(25, 25),
    flags=cv2.CASCADE_SCALE_IMAGE
)

for (x, y, w, h) in faces:
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray,
        scaleFactor=1.3,
        minNeighbors=10,
        minSize=(50, 50),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    for (ex,ey,ew,eh) in eyes:
       print("eye")
       cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,120),2)

profiles = profile_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=10,
    minSize=(25, 25),
    flags=cv2.CASCADE_SCALE_IMAGE
)
for (x, y, w, h) in profiles:
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)


# dlib
# import dlib
# from skimage import io
# detector = dlib.get_frontal_face_detector()
# img2 = io.imread('imgs/group1.jpg')
# dets = detector(img2, 1)
# for i, d in enumerate(dets):
    # print("Number of faces detected: {}".format(len(dets)))
    # img = cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255), 2)


cv2.imshow('img', img)
cv2.waitKey(0)
