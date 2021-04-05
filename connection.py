import time
import sys
import copy
import threading
import serial
import cv2
import numpy as np
import struct

from config import *

# 串口号
PORTX = "COM10"
# 波特率
BPS = 115200
# 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
TIMEX = 0


class Connection(object):
    def __init__(self, p=PORTX, b=BPS, to=TIMEX):
        self.device = serial.Serial(port=p, baudrate=b, timeout=to)
        self.stop_flag = False

        self.tx_queue = []
        self.tx_thread = threading.Thread(target=self.tx_function)

        # self.reset_rx_buffer()
        # self.rx_queue = Queue.Queue()
        # self.rx_thread = threading.Thread(target=self.receive)

        self.start()

    def start(self):
        self.stop_flag = False
        # self.rx_thread.start()
        self.tx_thread.start()

    def stop(self):
        self.stop_flag = False
        self.rx_thread.join()
        self.tx_thread.join()

    def reset_rx_buffer(self):
        self.current_packet = SerialInfo()
        self.rx_status = 0
        self.rx_datalen = 0

    def rx_function(self):
        rx_bytes = self.device.read()
        for rx_byte in rx_bytes:
            if self.rx_status == 0:  # 等待HEAD
                if rx_byte == protocol.D_INFO["HEAD"]:
                    self.rx_status = 1
            elif self.rx_status == 1:  # 等待D_ADDR
                if rx_byte == protocol.UPD_ADDR:
                    self.current_packet.INFO["D_ADDR"] = rx_byte
                    self.rx_status = 2
                else:
                    self.reset_rx_buffer()
            elif self.rx_status == 2:  # 等待ID
                self.current_packet.INFO["ID"] = rx_byte
                self.rx_status = 3
            elif self.rx_status == 3:  # 等待LEN
                # 貌似python3直接转换byte->int，有问题自己纠正
                self.current_packet.INFO["LEN"] = rx_byte
                if rx_byte == 0:  # 不确定有没有这种包，以及对应的校验方式，有问题自己修改
                    self.rx_status = 5
                else:
                    self.rx_status = 4
            elif self.rx_status == 4:  # 等待DATA
                self.current_packet.INFO["DATA"].append(rx_byte)
                self.rx_datalen += 1
                if self.rx_datalen >= self.current_packet.INFO["LEN"]:
                    self.rx_status = 5
            elif self.rx_status == 5:  # 等待SUM_CHECK
                self.current_packet.sumcheck_cal()
                if rx_byte == self.current_packet.INFO["SUM_CHECK"]:
                    self.rx_status = 6
                else:  # 校验失败
                    self.reset_rx_buffer()
            elif self.rx_status == 6:  # 等待ADD_CHECK
                if rx_byte == self.current_packet.INFO["ADD_CHECK"]:
                    self.rx_queue.put(copy.deepcopy(self.current_packet))
                self.reset_rx_buffer()  # 校验失败或者成功后都需要重设
        

    def tx_function(self):
        while self.stop_flag is False:
            if len(self.tx_queue)>0:
                print(self.tx_queue)
                tx_packet = self.tx_queue.pop()
                # print([i for i in tx_packet])
                self.device.write(tx_packet)
                self.tx_queue = []
            # print(time.time())
            time.sleep(0.10)

    def send(self, tx_packet):
        self.tx_queue.append(copy.deepcopy(tx_packet))
        # print(self.tx_queue)

    def receive(self):
        while self.stop_flag is False:
            start_time = time.time()
            self.rx_function()

            if not self.rx_queue.empty():
                sys.stdout.write(self.monitor.INFO_monitor(
                    (self.rx_queue.get().INFO)))
                self.rx_queue = Queue.Queue()

class SerialInfo(object):
    def __init__(self):
        self.INFO = copy.deepcopy(D_INFO)

    def sumcheck_cal(self):
        sumcheck = 0
        addcheck = 0
        for i in [(k, v) for k, v in self.INFO.items()][:-3]:
            sumcheck += i[1]
            addcheck += sumcheck
        
        for i in self.INFO["DATA"]:
            sumcheck += i
            addcheck += sumcheck

        self.INFO["SUM_CHECK"] = int(sumcheck) & 0XFF
        self.INFO["ADD_CHECK"] = int(addcheck) & 0XFF

    def getInfo(self):
        return bytearray([
            self.INFO["HEAD"],
            self.INFO["D_ADDR"],
            self.INFO["ID"],
            self.INFO["LEN"],
            *self.INFO["DATA"],
            self.INFO["SUM_CHECK"],
            self.INFO["ADD_CHECK"]
        ])


class Robot(SerialInfo):
    def __init__(self, name=None, data=None):
        super().__init__()
        self.name = name
        self.initRobot()
        if data is not None:
            self.setDATA(*data)

    def __call__(self, id, identif, data):
        self.setID(id)
        self.setDATA(identif, data)
        return self.getInfo()

    def setID(self, id):
        self.INFO["ID"] = ID[id]

    def setDATA(self, identif, data):
        identif = "<" + identif
        if isinstance(data, int):
            self.INFO["DATA"] = struct.pack(identif, data)
        else:
            self.INFO["DATA"] = struct.pack(identif, *data)
        self.sumcheck_cal()

    def initRobot(self):
        self.INFO["D_ADDR"] = D_ADDR[self.name]
        self.INFO["LEN"] = 2

    def reset_robot():
        self.INFO = copy.deepcopy(D_INFO)

    def launch(self):
        self.setDATA("", self.INFO)

class Sentry_up():
    def __init__(self, name):
        super().__init__(name)

class Hero(Robot):
    def __init__(self, name="hero"):
        super().__init__(name)