#!/usr/bin/env python
# coding: utf-8

# # Roll Call Edge

# In[21]:


import tkinter as tk
from tkinter import Tk, Label, Button
from tkinter.messagebox import showinfo, showwarning
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk, ImageFont, ImageDraw
from time import time, localtime, strftime
import cv2
from facegen import Faces
from sys import argv
import argparse
import platform
import face_recognition
import numpy as np
import paho.mqtt.publish as publish


# In[22]:


def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=60, flip_method=0):
    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            )

def downscale(image):
    if width > 0:  # downscale to save time for detection, no action if width <= 0
        r, w = image.shape[:2]
        newr = int((width / w) * r)
        img = cv2.resize(image, (width, newr))
        return img
    return image

def video_loop():
    global picture, rollcall_flg, video_flg
    
    success, frame = cam.read()
    if success:
        ns = []  # sign-in names
        picture = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if width < cam_w:  # downsize
            picture = downscale(picture) 
        n_len = -1
        if rollcall_flg:
            if faces.is_none() or time()-rollcall_start > 5.:  # check for 5 seconds
                rollcall_flg = False
                window.title(name)
            else:  # face recognition
                img = picture.copy()
                rets = detect(img)
                for r in rets:  # got the faces
                    (top, right, bottom, left, n) = r
                    if n != '不認識':
                        ns.append(n)
                    cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0))  # RGB
                    img = Image.fromarray(img)
                    f = ImageFont.truetype(font, 20)
                    ImageDraw.Draw(img).text((left, top-20), n, (255, 0, 0), f)  # RGB
                    img = np.array(img)
                n_len = len(ns)
        img = Image.fromarray(img if rollcall_flg else picture)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        if n_len > 0:
            rollcall_flg = False
            if mqtt_flg:
                mqtt_pub('rollcall/signin', ns)
            video_flg = False
            showinfo('sign in', f'{ns} sign in successfully.')
            video_flg = True
            window.title(name)
            
        cv2.waitKey(17)  # based on FPS 60
    
    if video_flg:
        window.after(1, video_loop)
            
def register():
    global video_flg, picture
    
    window.title(f'{name} registering ...')
    video_flg = False
    n = askstring('rollcall labeling', 'Label')
    if n and len(n) > 0:
        rtn = faces.update_image(picture, n)
        if rtn > 0:
            showinfo('rollcall labeling', f'Register {n} successfully.')
            if mqtt_flg:
                mqtt_pub('rollcall/register', n)
        else:
            showwarning('rollcall labeling', f'Failed to register {n}!')
    video_flg = True
    window.title(name)
    window.after(1, video_loop)  # resume the camera

def detect(face):
    ens = face_recognition.face_encodings(face)  # encode the faces
    ens_len = len(ens)  # get faces count
    ret = []
    if ens_len > 0:
        locs = face_recognition.face_locations(face)  # get the face frame
        if ens_len is not len(locs):
            print(f'something wrong!!! {ens_len} != {len(locs)}')
        for e in range(ens_len):  # judge each got face
            distance = face_recognition.face_distance(faces.encodes, ens[e])  # compute the distance with each face
            (top, right, bottom, left) = locs[e]
            facei = distance.argmin()  # decide the most likly face
            name = faces.labels[facei] if distance[facei] < threshold else '不認識'
            ret.append((top, right, bottom, left, name))
    return ret    

def rollcall():
    global video_flg, rollcall_flg, rollcall_start
    
    window.title(f'{name} signing in ...')
    video_flg = True
    rollcall_flg = True
    rollcall_start = time()

def mqtt_pub(topic, msg):
    if type(msg) is str:
        mm = f'{msg}|{strftime("%Y/%m/%d-%H:%M:%S", localtime())}'
        publish.single(topic, mm, hostname=ip)
    else:
        payload = []
        for m in msg:
            mm = f'{m}|{strftime("%Y/%m/%d-%H:%M:%S", localtime())}'
            payload.append((topic, mm, 0, False))
        publish.multiple(payload, hostname=ip)


# In[23]:


# parser design
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cam', action='store_true', help='change CAM')
parser.add_argument('-d', '--distance', type=float, default=0.5, help='threshold for recognition face distance')
parser.add_argument('-e', '--encoding', type=str, default='face.csv', help='face encoding in csv')
parser.add_argument('-f', '--font', type=str, help='font in ttf, ttc or otf')
parser.add_argument('-m', '--mqtt_broker', type=str, help='IP address of MQTT broker')  # None means no MQTT transmission
parser.add_argument('-r', '--resize', type=int, default=320, help='downscale the pic width to save detection time')

# avoid jupyter notebook exception
if argv[0][-21:] == 'ipykernel_launcher.py':
    args = parser.parse_args(args=[])
    name = 'rollcall'
else:
    args = parser.parse_args()
    name = argv[0]

# parameters  
video_flg = True  # flag for streaming or not
picture = None  # target face image
width = args.resize  # target image size
rollcall_flg = False
rollcall_start = None
faces = Faces(args.encoding)  # for face encoding generation
threshold = args.distance
font = args.font
if font is None:  # decide the default font for varient platforms
    font = 'NotoSansCJK-Regular.ttc' if platform.machine() == 'aarch64' else 'kaiu.ttf'  # Jetson Nano vs Windows
ip = args.mqtt_broker
mqtt_flg = ip is not None

# cam design
if platform.machine() == 'aarch64':  # Jetson Nano
    cam = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
else:
    cam = cv2.VideoCapture(int(args.cam))
    
cam_w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))  # in float
cam_h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))  # in float

# tk design
window = Tk()
window.title(name)
window.geometry(f'{width}x{width+50}')
panel = Label(window, width=width, height=width, bg='black')  # initialize image panel
panel.pack()
p = Button(window, text='點名', font=('Arial', 12), width=10, height=1, command=rollcall)
p.pack(side='left', padx=10, pady=10)
p = Button(window, text='註冊', font=('Arial', 12), width=10, height=1, command=register)
p.pack(side='right', padx=10, pady=10)

# loop
video_loop()
window.mainloop()
cam.release()
cv2.destroyAllWindows()

