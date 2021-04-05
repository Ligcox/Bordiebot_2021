修改了一部分程序结构
* Control类型结构重做，详细参考config.py内容
* 处理预览整合到Trackbar控制项内，可以根据需要开/关，默认为开
* 处理预览不再显示在独立窗口，现在与控制在同一窗口内显示

文件列表
app.py    - 程序本体
module.py - 标准化模块(已注释,主要改动)
 - vInput.py           图像采集(已注释)
 - imageFilter.py      图像处理
 - targetDetector.py   目标检测器
 - classifier.py       识别器（咕咕
config.py - 整体配置文件(已注释,主要改动)
utils.py  - 辅助代码(已注释)


视频测试文件依然在学校网盘
学校封网打不开的话请使用VPN
http://myun.sues.edu.cn:80/link/955FE1CD2693C0146DA69003665FBB72