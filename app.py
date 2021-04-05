#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2

from vInput import vInput
from imageFilter import colorFilter
from targetDetector import simpleDetector
import time
# from decision import Decision
# from connection import *

# source = 文件名以使用视频文件
# source = "1.mp4"
# source = 数字ID以使用摄像头
# source = DAHENG+数字ID以使用摄像头
source = "DAHENG0"

cFilter = colorFilter(False)
sDetector = simpleDetector(False)
# conn = Connection()
# hero = Hero()
# decision = Decision("hero_decision")

with vInput(source,False) as vIn:
    pre_x = 1
    while(True):
        frame = vIn.process()
        if not frame is None:
            # print(frame.shape)
            filtered_frame = cFilter.process(frame)
            armro_list = sDetector.process(filtered_frame)

            # for i in armro_list:
            #     x_offset, y_offset = decision.offset(i)
            #     conn.send(hero("Tripod_yaw", "h", x_offset))
            #     pre_x = x_offset
            #     # conn.send(hero("Tripod_pitch", "h", y_offset))
            #     break

            # if len(armro_list) == 0:
            #     print("====", pre_x)
            #     if pre_x ==0 :
            #         pre_x+=0.00001
            #     conn.send(hero("Tripod_yaw", "h", int(2*abs(pre_x)/pre_x)))

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

cv2.destroyAllWindows()