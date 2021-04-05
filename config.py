import cv2
from collections import OrderedDict

######## 参数设定 ########

######## TrackBar控制选项 ########
# 数据类型为字典类 (dict类)
# 数据格式为
# {
#   控制项名称	:   [类型，默认数据值，辅助配置]
# }
#
# 目前共有两种有效控制类
# 1. NUMERIC - 数值类
# 2. ENUM    - 枚举类 (ENUMERATE太长)
# 其中
#
# NUMERIC 的 辅助配置格式为
# [最小值，最大值，精度] (均为控制数值对应值，Trackbar相关数值交给程序计算)
#
# ENUM 的 辅助配置格式为 字典类，其中key暂时不用，value为对应数据
#
# TODO：
# 字典类排序比较混乱，key不用的话可以考虑换list
# 如果需要用key的话也许需要其他办法
#


# 定义Control类数值位置常量
IDX_CONTROL_TYPE = 0
IDX_CONTROL_VAL = 1
IDX_CONTROL_SETTING = 2

# 定义Control类型
TYPE_CONTROL_NONE = 0  # 占位，方便处理报错
TYPE_CONTROL_NUMERIC = 1
TYPE_CONTROL_ENUM = 2

# 定义Trackbar类数值位置常量
IDX_NUMERIC_MINVAL = 0
IDX_NUMERIC_MAXVAL = 1
IDX_NUMERIC_RES = 2

# 辅助BOOLEAN类实现的常量MAPPING
BOOLEAN_ENUM = {
    'False':   False,
    'True':   True
}


# 视频文件控制
video_controls = {
    'alpha'			:	[TYPE_CONTROL_NUMERIC, 1, [0, 10, 0.1]],
    'beta'			:	[TYPE_CONTROL_NUMERIC, -133, [-255, 255, 1]],
    'rotation':   [TYPE_CONTROL_NUMERIC, 0, [-180, 180, 90]],
    'scale':   [TYPE_CONTROL_NUMERIC, 0.1, [0, 1, 0.1]],
    'silent':   [TYPE_CONTROL_ENUM, 0, BOOLEAN_ENUM]
}




######## TrackBar辅助项 ########
# TrackBar读取数字值，套一层Mapping换成枚举值
# 摄像头编码
camera_codecs = {
    'V4L2_PIX_FMT_YUYV':   1448695129,
    # Not supported, 这个编码我们用的摄像头不支持
    # 'V4L2_PIX_FMT_H264' :   875967048,
    'V4L2_PIX_FMT_MJPEG':   1196444237
}

# 摄像头控制集
camera_controls = {
    'FourCC':   [TYPE_CONTROL_ENUM, 0, camera_codecs],
    'Brightness':   [TYPE_CONTROL_NUMERIC, 64, [0, 128, 1]],
    'Contrast':   [TYPE_CONTROL_NUMERIC, 32, [0, 95, 1]],
    'Saturation':   [TYPE_CONTROL_NUMERIC, 32, [0, 100, 1]],
    'Hue':   [TYPE_CONTROL_NUMERIC, 3000, [0, 4000, 100]],
    'Gain':   [TYPE_CONTROL_NUMERIC, 0, [0, 80, 1]],
    'Exposure':   [TYPE_CONTROL_NUMERIC, 20000, [0, 40000, 1000]],
    'Gamma':   [TYPE_CONTROL_NUMERIC, 150, [100, 300, 1]],
    'Sharpness':   [TYPE_CONTROL_NUMERIC, 2, [1, 7, 1]],
    'rotation':   [TYPE_CONTROL_NUMERIC, 0, [-180, 180, 90]],
    'scale':   [TYPE_CONTROL_NUMERIC, 0.4, [0, 5, 0.1]],
    'silent':   [TYPE_CONTROL_ENUM, 0, BOOLEAN_ENUM]
}

daheng_cam_controls = {
    'rotation':   [TYPE_CONTROL_NUMERIC, 0, [-180, 180, 90]],
    'scale':   [TYPE_CONTROL_NUMERIC, 0.4, [0, 5, 0.1]],
    'silent':   [TYPE_CONTROL_ENUM, 0, BOOLEAN_ENUM]
}

# 灯条捕捉Mask类型的Mapping，分为Binary和to_zero两种，
# Binary    满足条件的全为真，反之为假 -> 表现为黑白图像 真=255 | 假=0 -》 即消除亮度信息，做Mask时大部分情况是消除的，因为原图含有亮度信息
# To_zero   满足条件的不变，反之归零 -> 表现为黑白图像 不变=0~255 | 归零=0
channelMasks = {
    'Binary':   [cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV],
    'Normal':   [cv2.THRESH_TOZERO, cv2.THRESH_TOZERO_INV]
}

# Filter控制类集
channel_filter_controls = {
    'blueTarget'	:	[TYPE_CONTROL_NUMERIC, 245, [0, 255, 1]],
    'blueTolerance'	:	[TYPE_CONTROL_NUMERIC, 20, [0, 20, 1]],
    'greenTarget'	:	[TYPE_CONTROL_NUMERIC, 245, [0, 255, 1]],
    'greenTolerance':	[TYPE_CONTROL_NUMERIC, 20, [0, 20, 1]],
    'redTarget'		:	[TYPE_CONTROL_NUMERIC, 245, [0, 255, 1]],
    'redTolerance'	:	[TYPE_CONTROL_NUMERIC, 10, [0, 20, 1]],
    'maskMethod':   [TYPE_CONTROL_ENUM, 0, channelMasks],
    'silent':   [TYPE_CONTROL_ENUM, 0, BOOLEAN_ENUM]
}


# 颜色Mapping，方便调整标记的颜色
color_map = {
    # Key -> Color in RGB Code
    '#FF0000':   (0, 0, 255),
    '#00FF00':   (0, 255, 0),
    '#0000FF':   (255, 0, 0),
    '#FFFF00':   (0, 255, 255),
    '#FF00FF':   (255, 0, 255),
    '#00FFFF':   (255, 255, 0)
}

# 装甲板等条控制类
# bigArmour：大装甲板（2021赛季为230*127）
# normalArmour:小装甲板（2021赛季为135*125）
armourSize = {
    "bigArmour":[230, 127],
    "normalArmour":[140, 58]
}

# Detector控制集
simple_detector_controls = {
    # 轮廓线筛选，0为不设限
    'Contour_Area_Threshold':   [TYPE_CONTROL_NUMERIC, 0.001, [0, 0.01, 0.001]],
    # 长边最大夹角，0为不设限
    'LightStrip_Angle_Diff':   [TYPE_CONTROL_NUMERIC, 17, [0, 90, 1]],
    # 间距与较长一方长边比的最小值，0为不设限
    'LightStrip_Displacement_Diff':   [TYPE_CONTROL_NUMERIC, 39, [0, 5, 0.1]],
    'LightStrip_Box_Color':   [TYPE_CONTROL_ENUM, 1, color_map],
    'LightStrip_Box_Thickness':   [TYPE_CONTROL_NUMERIC, 2, [1, 10, 1]],
    'Armor_Box_Color':   [TYPE_CONTROL_ENUM, 2, color_map],
    'Armor_Box_Thickness':   [TYPE_CONTROL_NUMERIC, 2, [1, 10, 1]],
    'silent':   [TYPE_CONTROL_ENUM, 0, BOOLEAN_ENUM],
    "bigArmour":    [TYPE_CONTROL_ENUM, 0, armourSize],
    "normalArmour": [TYPE_CONTROL_ENUM, 1, armourSize]
}


# ######################################通讯协议相关######################################
# ################################通讯协议按照下列格式发送#################################
#
# 帧头    目标地址    功能码  数据长度    数据内容    和校验    附加校验
# HEAD    D_ADDR       ID      LEN       DATA     SUMCHECK  ADDCHECK
'''
# 帧头
# 固定为0xFF

# 目标地址
# 广播地址：0x00
# 上位机：0x01
# 机器人：0x02-0x08

# 功能码
# 轨道：0x01
# 云台yaw：0x02
# 云台pitch：0x03
# 枪管：0x04
# 裁判系统信息0x05

# 数据长度
# 固定为2

# 数据内容
# 轨道:0x00(空缺) 0x00轨道静止 0x01加速 0x02减速
# 云台偏移量: -655~655
# 枪管: UINT8 初速度设置   BOOL   是否发射


大小端转换参考：
https://docs.python.org/3/library/struct.html
https://www.cnblogs.com/coser/archive/2011/12/17/2291160.html
'''


D_INFO = {
    "HEAD":  0xFF,
    "D_ADDR":  None,
    "ID": None,
    "LEN":  None,
    "DATA":  bytearray(),
    "SUM_CHECK":  None,
    "ADD_CHECK":  None
}
D_INFO = OrderedDict(D_INFO)

D_ADDR = {
    "broadcast": 0x00,
    "mainfold": 0x01,
    "sentry_up": 0x02,
    "sentry_down": 0x03,
    "infantry": 0x04,
    "engineer": 0x05,
    "hero": 0x06,
    "air": 0x07,
    "radar": 0x08
}

ID = {
    "pathway": 0x01,
    "Tripod_yaw": 0x02,
    "Tripod_pitch": 0x03,
    "barrel": 0x04,
    "referee_system": 0x05
}

LEN = {
    "LEN": 2
}


DATA = {
    "pathway": bytearray([0x00, 0x00]),
    "sentry_up": bytearray([0x00, 0x00]),
    "sentry_down": bytearray([0x00, 0x00]),
    "barrel": bytearray([0x00, 0x00]),
}
