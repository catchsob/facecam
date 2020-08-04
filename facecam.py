#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import pandas as pd
import csv
import face_recognition
import cv2
import numpy as np
import platform
from PIL import ImageFont, ImageDraw, Image
from os import path

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

class FaceCam():
    def __init__(self, csv, width=320, threshold=0.5, font='kaiu.ttf'):
        self.labels = None
        self.encodes = None
        self._load(csv)
        self.width = width
        self.threshold = threshold
        self.font=font
    
    def _load(self, file):
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rows = csv.reader(csvfile)
            self.labels = []
            self.encodes = []
            for i, r in enumerate(rows):
                if i == 0 and r[0] == 'name':
                    continue
                self.labels.append(r[0])
                self.encodes.append(eval(r[1]))
        return len(self.labels)
    
    def _detect(self, face):
        ens = face_recognition.face_encodings(face) #將圖編碼
        ens_len = len(ens) #取得臉數
        ret = []
        if ens_len > 0:
            locs = face_recognition.face_locations(face) #取得臉部框
            if ens_len is not len(locs):
                print(f'something wrong!!! {ens_len} != {len(locs)}')
            for e in range(ens_len): #針對每個擷取到的臉進行判讀
                distance = face_recognition.face_distance(self.encodes, ens[e]) #計算影像與每張臉的距離
                (top, right, bottom, left) = locs[e]
                facei = distance.argmin() #決定最像的臉
                name = self.labels[facei] if distance[facei] < self.threshold else '不認識'
                ret.append((top, right, bottom, left, name))
        return ret
    
    def _downscale(self, image):
        if self.width > 0: # downscale to save time for detection, no action if self.width <= 0
            r, w = image.shape[:2]
            newr = int((self.width / w) * r)
            img = cv2.resize(image, (self.width, newr))
            return img
        return image
    
    def run(self, interval=40, reverse_cam=False):
        if platform.machine() == 'aarch64': # Jetson Nano
            cam = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
        else:
            cam = cv2.VideoCapture(int(reverse_cam)) # Windows 10 & Raspberry Pi 3B+ 
            if self.width > 0: # downscale to save time for detection, but the size wont be same with assigned
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cam_w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)) # float
        cam_h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)) # float
        while(True):
            success, frame = cam.read() # 從攝影機擷取一張影像
            if success:
                if self.width < cam_w: # downsize for detection
                    frame = self._downscale(frame)
                rets = self._detect(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                for r in rets:
                    (top, right, bottom, left, n) = r
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255))
                    frame = Image.fromarray(frame)
                    f = ImageFont.truetype(self.font, 20)
                    ImageDraw.Draw(frame).text((left, top-20), n, (0,0,255), f)
                    frame = np.array(frame)
                cv2.imshow(f'FaceCam in {frame.shape[1]}x{frame.shape[0]} per {interval}ms', frame)
            if cv2.waitKey(1 if interval <= 0 else interval) in [ord('\r'), ord('q')]: # 離開迴圈熱鍵
                break
        cam.release() # 釋放攝影機
        cv2.destroyAllWindows() # 關閉所有 OpenCV 視窗
            
    def face(self, file, textonly=False):
        img = cv2.imread(file)
        img = self._downscale(img)
        rets = self._detect(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) #轉為RGB偵測
        
        if textonly:
            ns = [r[4] for r in rets]
            text = f'我認得 {ns}' if len(ns) > 0 else '找不到臉!'
            print(text)
            return
        
        for r in rets:
            (top, right, bottom, left, n) = r
            cv2.rectangle(img, (left, top), (right, bottom), (0,0,255)) #紅方框
            img = Image.fromarray(img)
            f = ImageFont.truetype(self.font, 20)
            ImageDraw.Draw(img).text((left, top-20), n, (0,0,255), f) #紅字
            img = np.array(img)
        cv2.imshow(f'FaceFace in {img.shape[1]}x{img.shape[0]}', img)
        cv2.waitKey(0) #等待用戶關閉圖檔
        cv2.destroyAllWindows() # 關閉所有 OpenCV 視窗


# In[43]:


import argparse
from sys import argv
from os import path
from time import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encoding', type=str, default='face.csv', help='face encoding in csv')
    parser.add_argument('-p', '--pic', type=str, help='picture file for facing')
    parser.add_argument('-t', '--textonly', action='store_true', help='show text result only')
    parser.add_argument('-r', '--resize', type=int, default=320, help='downscale the pic width to save detection time')
    parser.add_argument('-d', '--distance', type=float, default=0.5, help='threshold for recognition face distance')
    parser.add_argument('-i', '--interval', type=int, default=40, help='frame capture interval in ms')
    parser.add_argument('-f', '--font', type=str, help='font in ttf, ttc or otf')
    parser.add_argument('-c', '--cam', action='store_true', help='change CAM')
    
    # 避掉 jupyter notebook exception
    if argv[0][-21:] == 'ipykernel_launcher.py':
        args = parser.parse_args(args=[])
    else:
        args = parser.parse_args()
    
    font = args.font
    if font is None: # decide the default font for varient platforms
        font = 'NotoSansCJK-Regular.ttc' if platform.machine() == 'aarch64' else 'kaiu.ttf' # Jetson Nano vs Windows
    if not path.isfile(args.encoding):
        print(f'{args.encoding} not existed!')
    elif args.pic is None:
        FaceCam(args.encoding, args.resize, args.distance, font).run(args.interval, args.cam)
    elif path.isfile(args.pic):
        if args.textonly:
            start = time()
        FaceCam(args.encoding, args.resize, args.distance, font).face(args.pic, textonly=args.textonly)
        if args.textonly:
            print(f'elapsed {time()-start:.3f} secs')
    else:
        print(f'{args.pic} not existed!')

