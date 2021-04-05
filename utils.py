import cv2
import numpy as np


# 基于角度(Degrees)的三角函数，大部分语言都使用弧度(Radians)作为标准
def sind(x):
    return np.sin(x*np.pi/180)

def cosd(x):
    return np.cos(x*np.pi/180)

# 针对opencv的矩形Rect的一些操作
# cv2 RotatedRect 数据格式
# [[x,y],[w,h],rotation]
# 顺带一提，最终画边框用drawContour的时候用的是BoxPoint，格式如下
# cv2 BoxPoints 数据格式
# [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

# 找到两个Rect长边朝向之间的夹角
def getCv2RotatedRectAngleDifference(rect1,rect2):
    return np.abs(getCv2RotatedRectOrientation(rect1)-getCv2RotatedRectOrientation(rect2))

# 找到两个Rect中心点的距离与较大Rect长边的比值
# TODO: 检测Rect中心点连线与较大Rect长边的夹角
def getCv2RotatedRectDistanceRatio(rect1,rect2):
    try:
        distance = np.sqrt(sum((np.array(rect1[0])-np.array(rect2[0]))**2))
        rect1_length = max(rect1[1][0],rect1[1][1])
        rect2_length = max(rect2[1][0],rect2[1][1])
        val = distance * 1.0 / max(rect1_length,rect2_length)
    except Exception as e:
        print(e.args)
        # put ratio to maximum so that it will fail ratio test
        val = np.inf
    return val

# 找到Rect以较长边h时的倾角(也就是该Rect,aka 灯条 的朝向)
def getCv2RotatedRectOrientation(rect):
    val = rect[2]
    w,h = rect[1]
    if w>h:
        val += 90
    while val>90:
        val -= 180
    while val<=-90:
        val += 180
    return val

# 图像处理辅助function，保证没有边被裁剪的同时完成缩放+旋转
def rotateImage(img,angle=0,scale=1):
    try:
        (h,w) = img.shape[:2]
        (cX,cY) = (w//2,h//2)
        M = cv2.getRotationMatrix2D((cX,cY),angle,scale)
        sa = np.abs(sind(angle))
        ca = np.abs(cosd(angle))
        outW = scale*(h*sa+w*ca)
        outH = scale*(h*ca+w*sa)
        M[0,2] += (outW/2) - cX
        M[1,2] += (outH/2) - cY
        return cv2.warpAffine(img,M,(int(outW),int(outH)))
    except Exception as e:
        print(e.args)
        return None
    