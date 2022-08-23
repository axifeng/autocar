#!/usr/bin/python3
# -*- coding: utf-8 -*-
import config
from camera import Camera
from task_func import *
import set_path
from cart.driver import Driver
from detector.detectors import Cruiser


front_camera = Camera(config.FRONT_CAM, [640, 480])

driver = Driver()
cruiser = Cruiser()
# 程序开启运行开关
start_button = Button_angel(1, "2")
# 程序关闭开关
stop_button = Button_angel(1, "4")


# 确认"DOWN"按键是否按下，程序是否处于等待直行状态
def check_stop():
    if stop_button.clicked():
        return True
    return False


if __name__ == '__main__':
    front_camera.start()
    # 基准速度
    driver.set_speed(50)
    driver.set_kx(0.85)
    # 延时
    time.sleep(0.5)
    #while True:
        #if start_button.clicked():
            #time.sleep(0.3)
            #break
        #print("Wait for start!")
    while True:
        front_image = front_camera.read()
        angle = cruiser.infer_cnn(front_image)
        driver.steer(angle)
        if check_stop():
            driver.stop()
            print("End of program!")
            break
    front_camera.stop()