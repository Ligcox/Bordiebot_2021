from module import *
from utils import *

ROI_RECT = 0
ROI_BOX = 1
PNP_INFO = 2
ROI_DATALENTH = 3

log = open("log.log", "a+")


class targetDetector(module):
    name = "Empty Detector Control"

    def process(self, frame):
        return None


class simpleDetector(targetDetector):
    def __init__(self, hide_controls=True):
        self.controls = simple_detector_controls
        self.name = "SimpleDetector"
        super().__init__(hide_controls)

    def detectLightStrip(self, image=None):
        '''
        breif:返回灯条数据
        return:strip_list
        strip_list:为图像中全部装甲板灯条
                   0>>ROI_RECT：装甲板长方形框信息，输出结果为cv2.minAreaRect ((x, y), (w, h), θ )
                   1>>ROI_BOX:装甲板长方形框信息，输出结果为cv2.boxPoints((x0, y0), (x1, y1))
        '''
        try:
            if image.shape[2] == 3:
                gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            elif image.shape[2] == 1:
                gray_img = image
            else:
                print('Image Shape {} Unexpected'.format(image.shape))
                return []
        except Exception as e:
            print(e.args)
            return []
        blur_img = cv2.blur(gray_img, (9, 9))
        _, thresh_img = cv2.threshold(blur_img, 2, 255, 0)
        blur_thresh = cv2.blur(thresh_img, (3, 3))
        contours, _ = cv2.findContours(
            blur_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        strip_list = []
        contour_area_threshold = image.shape[0]*image.shape[1] * \
            self.getControlVal('Contour_Area_Threshold')
        for c in contours:
            c_area = cv2.contourArea(c)
            if c_area > contour_area_threshold:
                strip_data = [None for i in range(ROI_DATALENTH)]
                strip_data[ROI_RECT] = cv2.minAreaRect(c)
                strip_data[ROI_BOX] = np.int0(
                    cv2.boxPoints(strip_data[ROI_RECT]))
                strip_list.append(strip_data)
        return strip_list

    def getLightStripRelation(self, strip1, strip2):
        return [
            getCv2RotatedRectAngleDifference(
                strip1[ROI_RECT], strip2[ROI_RECT]),
            getCv2RotatedRectDistanceRatio(
                strip1[ROI_RECT], strip2[ROI_RECT])
        ]

    def detectArmor(self, lightstrip_list=[]):
        '''
        breif:返回装甲板数据
        return:armor_list
        armor_list:为图像中全部装甲板信息长度为ROI_DATALENTH
                   ROI_RECT：装甲板长方形框信息，输出结果为cv2.minAreaRect ((x, y), (w, h), θ )
                   ROI_BOX:装甲板长方形框信息，输出结果为cv2.boxPoints((x0, y0), (x1, y1))
        '''
        armor_list = []
        for i in range(len(lightstrip_list)):
            for j in range(i+1, len(lightstrip_list)):
                angle_differnce, distance_ratio = self.getLightStripRelation(
                    lightstrip_list[i], lightstrip_list[j])
                
                if (
                    angle_differnce <= self.getControlVal(
                        'LightStrip_Angle_Diff')
                    and
                    distance_ratio <= self.getControlVal(
                        'LightStrip_Displacement_Diff')
                ):
                    armor_data = [None for i in range(ROI_DATALENTH)]
                    armor_data[ROI_RECT] = cv2.minAreaRect(np.concatenate(
                        (lightstrip_list[i][ROI_BOX], lightstrip_list[j][ROI_BOX])))
                    armor_data[ROI_BOX] = np.int0(
                        cv2.boxPoints(armor_data[ROI_RECT]))
                    armor_data[PNP_INFO] = self.pnp_info(armor_data[ROI_BOX])
                    log.write(str(armor_data[ROI_BOX]) + "\n")
                    log.write(str(armor_data[PNP_INFO]) + "\n")
                    print(armor_data[PNP_INFO])

                    armor_list.append(armor_data)
        return armor_list

    def pnp_info(self, armor_box):
        '''
        breif:pnp解算结果
        lightstrip1, lightstrip2:两个灯条的boxPoint信息
        return: [距离， 偏转角， yaw偏转角，pitch偏转角， pitch, yaw, roll]
        '''
        w, h = self.getControlVal("normalArmour")
        Camera_intrinsic = {
            "mtx": np.array([[2.11895539e+03, 0.00000000e+00, 6.84356632e+02],
                            [0.00000000e+00, 2.11295321e+03, 3.14469541e+02],
                            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
                            dtype=np.double),
            "dist": np.array([[-4.69617536e-01, 1.39659792e+00, 2.67814536e-03, -1.41953799e-03,
                            -1.85555201e+01]], dtype=np.double),

        }   
        
        # 世界坐标
        # world_coordinate = np.array([
        #     [0, 0, 0],
        #     [w, 0, 0],
        #     [w, h, 0],
        #     [0, h, 0]
        # ], dtype=np.float64)

        w, h = w/2, h/2
        world_coordinate = np.array([
            [-w, h, 0],
            [w, h, 0],
            [w, -h, 0],
            [-w, -h, 0]
        ], dtype=np.float64)

        # 像素坐标
        pnts = np.array(armor_box, dtype=np.float64) 

        # rotation_vector 旋转向量 translation_vector 平移向量
        success, rvec, tvec = cv2.solvePnP(world_coordinate, pnts, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
        distance = np.linalg.norm(tvec)

        angle = np.arcsin(np.linalg.norm(tvec[:3]) / distance)
        yaw_angle = np.arcsin(np.linalg.norm(tvec[1:]) / distance)
        pitch_angle = np.arcsin(np.linalg.norm((tvec[1], tvec[2])) / distance)
        # 默认为弧度制，转换为角度制改下面
        # angle = angle/np.pi*180

        distance /= 10

        rvec_matrix = cv2.Rodrigues(rvec)[0]
        proj_matrix = np.hstack((rvec_matrix, rvec))
        eulerAngles = -cv2.decomposeProjectionMatrix(proj_matrix)[6]  # 欧拉角
        pitch, yaw, roll = eulerAngles[0], eulerAngles[1], eulerAngles[2]
        pnp_list = [distance, angle, yaw_angle, pitch_angle, pitch, yaw, roll]
        # print(pnp_list)
        return pnp_list

    def createRoiMask(self, image, roi_list):
        mask = np.zeros(image, shape[:2], np.uint8)*255
        boxes = []
        for r in roi_list:
            boxes.append(r[ROI_BOX])
        cv2.drawContours(image, boxes, -1, 255, -1)
        return mask

    def drawRoi(self, image, roi_list, color=(255, 255, 255), thickness=2):
        boxes = []
        center_points = []
        for r in roi_list:
            boxes.append(r[ROI_BOX])
        for r in roi_list:
            cv2.circle(image, tuple(int(i) for i in r[ROI_RECT][0]), 0, color, thickness)
        cv2.drawContours(image, boxes, -1, color, thickness)
        return image

    def process(self, image):
        lightstrips = self.detectLightStrip(image)
        armors = self.detectArmor(lightstrips)
        self.updateProcess(image, lightstrips, armors)
        return armors

    def updateProcess(self, frame, lightstrips=[], armors=[]):
        if not (self.getControlVal('silent') or (frame is None)):
            img = frame.copy()
            cv2.putText(img, 'ROI', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            img = self.drawRoi(img, lightstrips, self.getControlVal(
                'LightStrip_Box_Color'), self.getControlVal('LightStrip_Box_Thickness'))
            img = self.drawRoi(img, armors, self.getControlVal(
                'Armor_Box_Color'), self.getControlVal('Armor_Box_Thickness'))
        else:
            img = BLANK_IMG
        cv2.imshow(self.control_window_name, img)
