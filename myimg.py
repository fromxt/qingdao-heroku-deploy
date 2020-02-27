#!/usr/bin/python
# -*- coding: UTF-8 -*-


# 图片识别


import pytesseract
from PIL import Image
import os
from pathlib import Path

# --------------------------------------class image--------------------------------
class MyImage():
    imgName = ''
    imgPath = ''
    def __init__(self, imgName):
        self.imgName = imgName
    
    def saveImage(self, res):
        with open(self.imgName, 'wb') as file:
            for data in res.iter_content(128):
                file.write(data)
        img = Image.open(self.imgName)
        return img
    # 使用pytesseract识别图片
    # 先去除干扰线，再把背景变透明
    def imgToString(self,img):
        img = img.convert('RGBA')
        pixdata = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x,y][0] == pixdata[x,y][1] and pixdata[x,y][0] == pixdata[x,y][3]:
                    pixdata[x, y] = (255, 255, 255,0)
                if pixdata[x,y][0] > 80 and pixdata[x,y][0] <= 220  and pixdata[x,y][1] > 80 and pixdata[x,y][1] <= 220 and pixdata[x,y][2] > 80 and pixdata[x,y][2]< 220:
                    pixdata[x, y] = (255, 255, 255,0)
        return pytesseract.image_to_string(img)
    # 删除图片
    def removeThisImg(self):
        path = os.path.abspath('.') + '\\' + self.imgName
        path = path.replace('\\','/')
        # print(path)
        my_file = Path(path)
        if my_file.exists():
            os.remove(path)
