#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import Tk, Label, Button
from tkinter.messagebox import showinfo, showwarning
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
import cv2
from facegen import Faces
from sys import argv
import argparse
import platform


# In[3]:


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
    global width
    if width > 0:  # downscale to save time for detection, no action if width <= 0
        r, w = image.shape[:2]
        newr = int((width / w) * r)
        img = cv2.resize(image, (width, newr))
        return img
    return image

def video_loop():
    global picture, width
    success, frame = cam.read()
    if success:
        cv2.waitKey(17)
        picture = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if width < cam_w:  # downsize
            picture = downscale(picture)
        img = Image.fromarray(picture)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        if video:
            window.after(1, video_loop)
            
def pic():
    global video, picture
    video = False
    name = askstring('faceme labeling', 'Label')
    if name and len(name) > 0:
        rtn = faces.update_image(picture, name)
        if rtn > 0:
            showinfo('faceme labeling', f'Register {name} successfully.')
        else:
            showwarning('faceme labeling', f'Failed to register {name}!')
    video = True
    window.after(1, video_loop)  # resume the camera

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--encoding', type=str, default='face.csv', help='face encoding in csv')
parser.add_argument('-r', '--resize', type=int, default=320, help='downscale the pic width to save detection time')
# avoid jupyter notebook exception
if argv[0][-21:] == 'ipykernel_launcher.py':
    args = parser.parse_args(args=[])
    name = 'faceme'
else:
    args = parser.parse_args()
    name = argv[0]

video = True  # flag for streaming or not
picture = None  # target face image
width = args.resize  # target image size

faces = Faces(args.encoding)  # for face encoding generation

if platform.machine() == 'aarch64':  # Jetson Nano
    cam = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
else:
    cam = cv2.VideoCapture(0)
    
cam_w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))  # float
cam_h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float
window = Tk()
window.title(name)
window.geometry(f'{width}x{width+50}')

panel = Label(window, width=width, height=width, bg='black')  # initialize image panel
panel.pack()

p = Button(window, text='PIC', font=('Arial', 12), width=6, height=1, command=pic)
p.pack(side='bottom', padx=10, pady=10)

video_loop()
window.mainloop()
cam.release()
cv2.destroyAllWindows()

