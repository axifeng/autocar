#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 导入当前目录下的文件夹作为路径
import set_path
from cart.widgets import *
import time
from cart.driver import Driver
import threading
from camera import Camera
from detector.detectors import *

task_detector = TaskDetector()

driver = Driver()


def task_init():
    motor = Motor_rotate(2, 1)
    removemotor = Motor_rotate(2, 2)
    limit_switch = LimitSwitch(4)
    servo_grasp = Servo_pwm(2)
    magsens = Magneto_sensor(3)
    servo_grasp.servo_control(180, 70)
    print("aaaaaa")
    # time.sleep(2)
    motor.motor_rotate(80)
    time.sleep(1)
    motor.motor_rotate(0)
    kl = limit_switch.clicked()
    removemotor.motor_rotate(-60)
    while True:
        kl = limit_switch.clicked()
        if kl:
            time.sleep(0.05)
            removemotor.motor_rotate(0)
            break
    time.sleep(0.5)


def light_work(light_port, color, tim_t):
    light = Light(light_port)
    red = [80, 0, 0]
    green = [0, 80, 0]
    yellow = [80, 80, 0]
    off = [0, 0, 0]
    light_color = [0, 0, 0]
    if color == 'red':
        light_color = red
    elif color == 'green':
        light_color = green
    elif color == 'yellow':
        light_color = yellow
    elif color == 'off':
        light_color = off
    light.light_control(0, light_color[0], light_color[1], light_color[2])
    time.sleep(tim_t)
    time.sleep(1)
    servo = Servo_pwm(6)
    servo.servo_control(180, 100)
    light.light_off()


def purchase_good():
    # print("purchase_goods")
    removemotor = Motor_rotate(2, 1)
    removemotor.motor_rotate(80)
    time.sleep(6.5)
    removemotor.motor_rotate(0)

    servo = Servo_pwm(6)
    servo.servo_control(100, 100)
    time.sleep(1.5)
    motor = Motor_rotate(2, 2)
    motor.motor_rotate(-50)  # 负代表的是向右边走，出去夹球
    time.sleep(1)
    motor.motor_rotate(0)
    time.sleep(1)
    servo.servo_control(180, 100)
    time.sleep(1)

    removemotor.motor_rotate(80)
    time.sleep(1.5)
    removemotor.motor_rotate(0)

    motor.motor_rotate(50)
    time.sleep(1)
    motor.motor_rotate(0)

    removemotor.motor_rotate(-80)  # 负代表的是向右边走，出去夹球
    time.sleep(8)
    removemotor.motor_rotate(0)


def raise_flag(servoID, light_port, flagname):
    print("raise_flag start!")
    servo_raise = Servo(servoID)
    # noflag
    # servo_raise.servo_control(42,60)
    # time.sleep(2)
    if flagname == "dunhuang":
        # dunhuang
        servo_raise.servo_control(40, 80)
        time.sleep(1)
        for i in range(0, 3):
            light_work(light_port, "green", 0.1)
    elif flagname == "jstdb":
        # jsddb
        servo_raise.servo_control(-140, 50)
        time.sleep(1)
        for i in range(0, 3):
            light_work(light_port, "green", 0.1)
    elif flagname == "alamutu":
        # almutu
        servo_raise.servo_control(115, 80)
        time.sleep(1)
        for i in range(0, 3):
            light_work(light_port, "green", 0.1)
    # noflag
    servo_raise.servo_control(-50, 80)
    # time.sleep(2)
    print("raise_flag stop!")

#矮人
def shot_target():
    graspmotor = Motor_rotate(2, 2)
    graspmotor.motor_rotate(-35)
    time.sleep(0.5)
    graspmotor.motor_rotate(0)
    print("shot_target start!")
    motor = Motor_rotate(2, 1)
    motor.motor_rotate(80)
    time.sleep(11)
    motor.motor_rotate(0)
    servo_shot = Servo_pwm(1)  # 伸缩装置，全部伸开的角度是0度
    servo_shot.servo_control(80, 30)
    time.sleep(2)
    # driver.run(30,30)
    # time.sleep(1)
    # driver.stop()
    servo_shot.servo_control(180, 30)
    time.sleep(1)
    motor = Motor_rotate(2, 1)
    motor.motor_rotate(-80)
    time.sleep(11)
    motor.motor_rotate(0)

    graspmotor.motor_rotate(50)
    time.sleep(1)
    graspmotor.motor_rotate(0)

#高人
def shot_target2():
    graspmotor = Motor_rotate(2, 2)
    graspmotor.motor_rotate(-35)
    time.sleep(0.5)
    graspmotor.motor_rotate(0)
    print("shot_target start!")
    motor = Motor_rotate(2, 1)
    motor.motor_rotate(80)
    time.sleep(15)
    motor.motor_rotate(0)
    servo_shot = Servo_pwm(1)  # 伸缩装置，全部伸开的角度是0度
    servo_shot.servo_control(75, 30)
    time.sleep(2)
    driver.run(30,30)
    time.sleep(1)
    driver.stop()


    servo_shot.servo_control(180, 30)
    time.sleep(2)
    motor = Motor_rotate(2, 1)
    motor.motor_rotate(-80)
    time.sleep(15)
    motor.motor_rotate(0)

    graspmotor.motor_rotate(50)
    time.sleep(1)
    graspmotor.motor_rotate(0)

def trade_good():
    removemotor = Motor_rotate(2, 2)
    servo_grasp = Servo_pwm(6)
    # 稍伸抓手
    removemotor.motor_rotate(-50)
    time.sleep(1.0)
    removemotor.motor_rotate(0)
    # 张开手抓
    servo_grasp.servo_control(75, 50)
    time.sleep(1.0)
    # 收回抓手
    removemotor.motor_rotate(50)
    time.sleep(0.8)
    servo_grasp.servo_control(180, 70)
    time.sleep(1.0)


def trade_good_1():
    # 伸出一点爪子，升起
    # 继续伸出爪子，张开爪子，合拢爪子
    # 回收爪子，下降
    graspmotor = Motor_rotate(2, 2)
    raisemotor = Motor_rotate(2, 1)
    servo_grasp = Servo_pwm(6)

    raisemotor.motor_rotate(80)
    time.sleep(8)
    raisemotor.motor_rotate(0)

    graspmotor.motor_rotate(-35)
    time.sleep(0.4)
    graspmotor.motor_rotate(0)

    raisemotor.motor_rotate(80)
    time.sleep(9)
    raisemotor.motor_rotate(0)

    servo_grasp.servo_control(75, 50)
    time.sleep(2)
    #
    graspmotor.motor_rotate(-50)
    time.sleep(1)
    graspmotor.motor_rotate(0)
    time.sleep(1)
    #
    servo_grasp.servo_control(180, 80)
    time.sleep(1)
    #

    #
def trade_good_2():
    graspmotor = Motor_rotate(2, 2)
    raisemotor = Motor_rotate(2, 1)
    servo_grasp = Servo_pwm(6)

    #上升
    raisemotor.motor_rotate(80)
    time.sleep(3)
    raisemotor.motor_rotate(0)
    #张开爪子
    servo_grasp.servo_control(75, 50)
    time.sleep(1)
    #往右边
    graspmotor.motor_rotate(-50)
    time.sleep(1)
    graspmotor.motor_rotate(0)
    time.sleep(1)

    #合拢
    servo_grasp.servo_control(180, 80)
    time.sleep(1)
def trade_over2():
    graspmotor = Motor_rotate(2, 2)
    raisemotor = Motor_rotate(2, 1)
    graspmotor.motor_rotate(50)
    time.sleep(1)
    graspmotor.motor_rotate(0)
    #
    raisemotor.motor_rotate(-80)
    time.sleep(4)
    raisemotor.motor_rotate(0)
    #


def trade_over():
    graspmotor = Motor_rotate(2, 2)
    raisemotor = Motor_rotate(2, 1)

    #
    raisemotor.motor_rotate(-80)
    time.sleep(17)
    raisemotor.motor_rotate(0)
    #
    graspmotor.motor_rotate(50)
    time.sleep(1)
    graspmotor.motor_rotate(0)


# def trade_good():
#     motor = Motor_rotate(2, 1)
#     traverse_motor = Motor_rotate(2, 2)
#     limit_switch = LimitSwitch(2)
#     servo_grasp = Servo_pwm(2)
#     mag_sens = Magneto_sensor(3)
#     ultrasonic = UltrasonicSensor(4)
#     # go
#     while True:
#         distance = ultrasonic.read()
#         if distance != None and distance < 10:
#             print("---------------------->")
#             motor.motor_rotate(50)
#             time.sleep(0.5)
#             motor.motor_rotate(0)
#             time.sleep(0.5)
#             servo_grasp.servo_control(50, 70)
#             time.sleep(0.5)
#             servo_grasp.servo_control(160, 70)
#             time.sleep(0.5)
#             motor.motor_rotate(-50)
#             time.sleep(0.5)
#             motor.motor_rotate(0)
#             # 张开手抓
#             servo_grasp.servo_control(50, 70)
#             time.sleep(0.5)
#             break
#     # 下降定位
#     traverse_motor.motor_rotate(-60)
#     while True:
#         kl = mag_sens.read()
#         print("kl=", kl, "\n")
#         if kl >= 93:
#             time.sleep(0.8)
#             traverse_motor.motor_rotate(0)
#             break
#     traverse_motor.motor_rotate(60)
#     time.sleep(1.5)
#     while True:
#         kh = mag_sens.read()
#         print("kh=", kh, "\n")
#         if kh >= 94:
#             time.sleep(0.8)
#             traverse_motor.motor_rotate(0)
#             break
#     motor.motor_rotate(50)
#     time.sleep(0.3)
#     motor.motor_rotate(0)
#     time.sleep(1)
#     servo_grasp.servo_control(160, 70)
#     motor.motor_rotate(-50)
#     time.sleep(0.5)
#     motor.motor_rotate(0)
#     traverse_motor.motor_rotate(-60)
#     time.sleep(1)
#     # 下降归位
#     while True:
#         kw = limit_switch.clicked()
#         if kw:
#             time.sleep(0.05)
#             traverse_motor.motor_rotate(0)
#             break


def test():
    t = threading.Thread(target=task5_thread, args=())
    t.start()
    t.join()

    for i in range(1, 4):
        light_work(4, "red", 0.2)
        time.sleep(0.2)


def task5_thread():
    buzzer = Buzzer()
    for i in range(1, 4):
        buzzer.rings()
        time.sleep(0.5)


def buzzer():
    buzzer = Buzzer()
    for i in range(1, 10):
        # print(i)
        buzzer.rings()
        time.sleep(0.5)


def color():
    while True:
        cap = cv2.VideoCapture(1)
        side_camera = Camera(1, [640, 480])
        side_image = side_camera.read()
        # res_side = task_detector.detect(side_image)
        # for res in res_side:
        # if res.index in task[1]['index']:
        hsv_frame = cv2.cvtColor(side_image, cv2.COLOR_BGR2HSV)
        print(hsv_frame)
        height, width, _ = hsv_frame.shape

        wx = int(width / 2)  # center
        wy = int(height / 2)

        center_color = hsv_frame[wy, wx]  # 中心点HSV像素值
        print(center_color)
        hue_value = center_color[0]  # 取Hue

        if hue_value < 5:
            color = 'RED'
        elif hue_value < 22:
            color = 'ORANGE'
        elif hue_value < 33:
            color = 'YELLOW'
        elif hue_value < 78:
            color = 'GREEN'
        elif hue_value < 131:
            color = 'BLUE'
        elif hue_value < 167:
            color = 'VIOLET'
        else:
            color = 'RED'
        side_camera.stop()

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(color)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def distance(port):
    ultrasonic = UltrasonicSensor(port)
    # driver.run(25,25)
    # time.sleep(1)
    driver.run(-25,-25)
    while True:
        distance = ultrasonic.read()
        print(distance)
        if distance != None and (distance < 30) and distance > 0:
            driver.stop()
            break
    driver.stop()
    # driver.run(-25,-25)
    # time.sleep(1.5)
    # driver.stop()



if __name__ == '__main__':
    # ultrasonic = UltrasonicSensor(2)
    # driver.run(-20, -20)
    # # go
    # while True:
    #     distance = ultrasonic.read()
    #     print(distance)
    #     # if distance != None and (distance < 30) and distance > 0:
    #         # driver.stop()
    #         # break

    # driver.run(25, 25)
    # time.sleep(3.5)
    # driver.stop()
    # driver.run(0,25)
    # time.sleep(2.5)
    # driver.stop()
    # time.sleep(1.5)fshot_target2
    # raise_flag(2, 4, "jstdb")
    # driver.run(30, 30)
    # time.sleep(3)
    # driver.stop()
    servo = Servo(1)
    servo.servo_control(-80,50)