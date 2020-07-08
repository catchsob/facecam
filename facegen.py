#!/usr/bin/env python
# coding: utf-8

# In[53]:


import face_recognition
from glob import glob
from os import path
#import pandas as pd
import csv

class Faces():
    def __init__(self, csv):
        self.facecsv = csv
        self.labels = None
        self.encodes = None
        self._load()
    
#     def _load_legacy(self):
#         face_df = pd.read_csv(self.facecsv)
#         self.labels = face_df['name'].values.tolist()
#         self.encodes = pd.eval(face_df['enc'])
    
    def _load(self):
        if not path.isfile(self.facecsv):
            return -1
        with open(self.facecsv, 'r', newline='', encoding='utf-8') as csvfile:
            rows = csv.reader(csvfile)
            self.labels = []
            self.encodes = []
            for i, r in enumerate(rows):
                if i == 0 and r[0] == 'name':
                    continue
                self.labels.append(r[0])
                self.encodes.append(eval(r[1]))
        return 0 if not self.labels else len(self.labels)
        
#     def _save_legacy(self):
#         if self.labels is None or self.encodes is None or self.facecsv is None:
#             return False
#         df = pd.DataFrame({'name': self.labels, 'enc': self.encodes})
#         df.to_csv(self.facecsv, index=False)
#         return True
    
    def _save(self):
        if self.labels is None or self.encodes is None or self.facecsv is None:
            return False
        with open(self.facecsv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name', 'enc'])
            for i in range(len(self.labels)):
                writer.writerow([self.labels[i], self.encodes[i]])
        return True
    
    def _encode(self, p):
        img = face_recognition.load_image_file(p)
        enc = face_recognition.face_encodings(img)[0] #回傳值被 list 包住
        lab = path.basename(p).split('.')[0] #取檔名當作 label
        return list(enc), lab
    
    def delete(self, label):
        if self._load() <= 0:
            return 0
                
        for i, v in enumerate(self.labels):
            if label == v:
                del self.labels[i]
                del self.encodes[i]
                return int(self._save())
            
        return 0
    
    def update(self, p):
        if path.isfile(p): #更新單個檔
            if self._load() < 0:
                return self.generate(p)
            
            enc, lab = self._encode(p)
            for i, v in enumerate(self.labels):
                if lab == v: #更新一筆
                    self.encodes[i] = enc
                    return int(self._save())
            #新增一筆
            self.encodes.append(enc)
            self.labels.append(lab)
            return int(self._save())
        
        elif path.isdir(p): #path, 更新目錄下所有檔
            if self._load() < 0:
                return self.generate(p)
            
            samples = glob(path.join(p, '*.jpg')) # 準備檔案清單
            count = 0
            for s in samples:
                enc, lab = self._encode(s)
                updated = False
                for i, v in enumerate(self.labels):
                    if lab == v: #更新一筆
                        self.encodes[i] = enc
                        updated = True
                        count += 1
                        break
                if not updated: #新增一筆
                    self.encodes.append(enc)
                    self.labels.append(lab)
                    count += 1
                    
            if count > 0 :
                return count if self._save() else 0
            
        return 0
        
    def generate(self, p):
        if path.isfile(p):
            samples = [p]
        elif path.isdir(p):
            samples = glob(path.join(p, '*.jpg')) # 準備檔案清單
        else:
            return 0
        
        # 創建模型
        self.labels = []
        self.encodes = []
        for s in samples:
            enc, lab = self._encode(s)
            self.encodes.append(enc) #轉成 list 才會有逗點，之後才能被叫用
            self.labels.append(lab)

        if len(self.labels) == 0:
            return 0
        
        return len(self.labels) if self._save() else 0 # 儲存模型


# In[1]:


import argparse
from sys import argv
from os import path
from time import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encoding', type=str, default='face.csv', help='face encoding in csv')
    parser.add_argument('-p', '--path', type=str, help='append or update one assigned picture or all in assigned path')
    parser.add_argument('-r', '--rebuild', action='store_true', help='rebuild the whole encoding instead of update')
    parser.add_argument('-d', '--deletelabel', type=str, help='delete some label')
    
    # 避掉 jupyter notebook exception
    if argv[0][-21:] == 'ipykernel_launcher.py':
        args = parser.parse_args(args=[])
    else:
        args = parser.parse_args()
    
    start = time()
    faces = Faces(args.encoding)
    if args.path is not None:
        if path.isfile(args.path):
            if args.rebuild:
                c = faces.generate(args.path)
                print(f'{c} face generated in {args.encoding} for {time()-start:.3f} secs')
            else:
                c = faces.update(args.path)
                print(f'{c} face updated in {args.encoding} for {time()-start:.3f} secs')
        elif path.isdir(args.path):
            if args.rebuild:
                c = faces.generate(args.path)
                print(f'{c} faces generated in {args.encoding} for {time()-start:.3f} secs')
            else:
                c = faces.update(args.path)
                print(f'{c} faces updated in {args.encoding} for {time()-start:.3f} secs')
        else:
            print(f'unknown path: {args.path}!')
    if args.deletelabel is not None:
        c = faces.delete(args.deletelabel)
        print(f'{c} face deleted for {time()-start:.3f} secs')


# In[ ]:




