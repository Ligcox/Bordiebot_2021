def pnp_distance():
    obj = np.array([[-half_Weight, -half_Height, 0], [half_Weight, -half_Height, 0], [half_Weight, half_Height, 0],
                        [-half_Weight, half_Height, 0]], dtype=np.float64)  # 世界坐标
        pnts = np.array(box, dtype=np.float64) # 像素坐标 将识别出的坐标放到这里

        # rotation_vector 旋转向量 translation_vector 平移向量
        success, rvec, tvec = cv2.solvePnP(obj, pnts, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
        distance=math.sqrt(tvec[0]**2+tvec[1]**2+tvec[2]**2)  # 测算距离

        angle = np.arcsin(math.sqrt(tvec[0]**2+tvec[1]**2) / distance)
        angle = angle/np.pi*180
        print(f"{tvec[0]},  {tvec[1]},  {math.sqrt(tvec[0]**2+tvec[1]**2)},  {distance}")

        distance /= 10

        rvec_matrix = cv2.Rodrigues(rvec)[0]
        proj_matrix = np.hstack((rvec_matrix, rvec))
        eulerAngles = -cv2.decomposeProjectionMatrix(proj_matrix)[6]  # 欧拉角
        pitch, yaw, roll = eulerAngles[0], eulerAngles[1], eulerAngles[2]
        rot_params = np.array([yaw, pitch, roll])  # 欧拉角 数组
        # 这里pitch要变为其相反数(不知道为啥)
        cv2.putText(frame, "%.2fcm,%.2fAAA,%.2f,%.2f,%.2f" % (distance, angle, yaw, -pitch, roll),
                    (0,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)