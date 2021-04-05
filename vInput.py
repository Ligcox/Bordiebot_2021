from utils import *
from module import *
import gxipy as gx
from PIL import Image

######## 定义常量 ########
VINPUT_SOURCE_UNDEFINED = 0
VINPUT_SOURCE_CAMERA = 1
VINPUT_SOURCE_VIDEO = 2
VINPUT_SOURCE_DAHENG_CAM = 2

# 定义与Control集对应的摄像头参数，方便调取
camera_keys = {
    'FPS':   cv2.CAP_PROP_FPS,
    # Not available
    # 'FrameCount':   cv2.CAP_PROP_FRAME_COUNT,
    'FourCC':   cv2.CAP_PROP_FOURCC,
    'Mode':   cv2.CAP_PROP_MODE,
    'Brightness':   cv2.CAP_PROP_BRIGHTNESS,
    'Contrast':   cv2.CAP_PROP_CONTRAST,
    'Saturation':   cv2.CAP_PROP_SATURATION,
    'Hue':   cv2.CAP_PROP_HUE,
    'Gain':   cv2.CAP_PROP_GAIN,
    'Exposure':   cv2.CAP_PROP_EXPOSURE,
    'Gamma':   cv2.CAP_PROP_GAMMA,
    'Sharpness':   cv2.CAP_PROP_SHARPNESS
}


class vInput(module):
    def __init__(self, vinput_source=None, hide_controls=True):
        # 获取数据源
        self.source = vinput_source
        # 先将数据源类型定位空，之后检测时更新
        self.type = VINPUT_SOURCE_UNDEFINED
        if self.source is None:
            self.device = None
        else:
            if isinstance(self.source, int):
                # 采集源是摄像头
                self.type = VINPUT_SOURCE_CAMERA
                # 载入对应Control集
                self.controls = camera_controls
                # 定义模块名
                self.name = 'Camera'
            elif self.source[:6] == "daheng" or self.source[:6] == "DAHENG":
                self.type = VINPUT_SOURCE_DAHENG_CAM
                # 设备id
                self.source = eval(self.source[6:])
                self.controls = daheng_cam_controls
                # 定义模块名
                self.name = 'Daheng_cam'
            else:
                # 采集源是文件
                self.type = VINPUT_SOURCE_VIDEO
                # 载入对应Control集
                self.controls = video_controls
                # 定义模块名
                self.name = 'Video'
            try:
                if self.type == VINPUT_SOURCE_DAHENG_CAM:
                    device_manager = gx.DeviceManager()
                    dev_num, dev_info_list = device_manager.update_device_list()
                    cam = device_manager.open_device_by_index(1)

                    # exit when the camera is a mono camera
                    if cam.PixelColorFilter.is_implemented() is False:
                        print("This sample does not support mono camera.")
                        cam.close_device()
                        return

                    # set continuous acquisition
                    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

                    # get param of improving image quality
                    if cam.GammaParam.is_readable():
                        gamma_value = cam.GammaParam.get()
                        gamma_lut = gx.Utility.get_gamma_lut(gamma_value)
                    else:
                        gamma_lut = None
                    if cam.ContrastParam.is_readable():
                        contrast_value = cam.ContrastParam.get()
                        contrast_lut = gx.Utility.get_contrast_lut(contrast_value)
                    else:
                        contrast_lut = None
                    if cam.ColorCorrectionParam.is_readable():
                        color_correction_param = cam.ColorCorrectionParam.get()
                    else:
                        color_correction_param = 0

                    # start data acquisition
                    cam.stream_on()
                    self.device = cam
                else:
                    # 尝试打开文件/摄像头
                    self.device = cv2.VideoCapture(self.source)
            except Exception as e:
                # 如果出错则将错误打印到控制台，并架空采集设变变量
                print(e.args)
                self.device = None
        super().__init__(hide_controls)

    def updateControls(self, key, value):
        # 调用原始updateControls方法更新self.controls
        super().updateControls(key, value)
        # 添加针对摄像头的参数写入
        try:
            if self.type == VINPUT_SOURCE_CAMERA:
                if key in camera_keys.keys():  # 如果key存在于摄像头设定中
                    # 设定摄像头
                    self.device.set(camera_keys[key], int(
                        self.getControlVal(key)))
        except Exception as e:
            print(e.args)

    def process(self):
        # 预留输出变量
        output = None
        if not self.device is None:
            try:
                # 读取帧
                if self.type == VINPUT_SOURCE_DAHENG_CAM:
                    print(111)
                    print(self.device)
                    raw_image = self.device.data_stream[0].get_image()
                    rgb_image = raw_image.convert("RGB")
                    numpy_image = rgb_image.get_numpy_array()
                    frame = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
                else:
                    _, frame = self.device.read()

                if not frame is None:
                    # 旋转与缩放
                    output = rotateImage(frame, self.getControlVal(
                        'rotation'), self.getControlVal('scale'))
                    if self.type == VINPUT_SOURCE_VIDEO:
                        # 如果是视频的话调整亮度
                        # TODO: 也许摄像头也需要这个
                        output = np.uint8(np.clip(self.getControlVal(
                            'alpha')*output+self.getControlVal('beta'), 0, 255))
                        # 视频到最后一帧后跳回初始进行循环播放
                        frame_count = self.device.get(cv2.CAP_PROP_FRAME_COUNT)
                        frame_no = self.device.get(cv2.CAP_PROP_POS_FRAMES)
                        if frame_no >= frame_count:
                            self.device.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        # TODO： 也许应该加入视频控制接口（跳转，快进/退，暂停)
            except Exception as e:
                print(e.args)
                output = None
        # 更新处理预览
        self.updateProcess(output)
        return output

    def updateProcess(self, frame):
        if not (self.getControlVal('silent') or (frame is None)):
            img = frame.copy()
            # 给预览图打上标注
            cv2.putText(img, 'Input', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        else:
            img = BLANK_IMG
        cv2.imshow(self.control_window_name, img)

    # 修改原有cleanup，保证摄像头的释放
    def cleanup(self):
        if not self.device is None:
            self.device.release()
        super().cleanup()
