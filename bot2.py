#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from config import *
# 导入路径
import set_path
from cart.widgets import *
from cart.driver import Driver
from camera import Camera
from detector.detectors import *
from task_func import *

front_camera = Camera(FRONT_CAM, [640, 480])
side_camera = Camera(SIDE_CAM, [640, 480])
driver = Driver()
cruiser = Cruiser()
# 地面标志检测
sign_detector = SignDetector()
# 侧边目标物检测
task_detector = TaskDetector()
# 程序开启运行开关
start_button = Button_angel(1, "2")

# 程序关闭开关
stop_button = Button_angel(1, "4")

servo1 = Servo(1)
task_9_flag = False

STATE_IDLE = "idle"
STATE_CRUISE = "cruise"
STATE_LOCATE_TASK = "sign_detected"
STATE_DO_TASK = "task"

sign_list = [0] * 10
order_num = 1
cam_dir = 1  # 左边为-1，右边为1
dtrade_y = 0  # 阈值设置进行比较
tradeNum = 350


# 确认"4"按键是否按下，程序是否处于等待状态
def check_stop():
    if stop_button.clicked():
        return True
    return False


# 任务程序开始按钮检测函数
def idle_handler(params=None):
    driver.stop()
    global order_num
    order_num = 1
    print("IDLE")
    while True:
        if start_button.clicked():
            print("program start!")
            # 调用到巡航模式
            break
        driver.stop()
    print("START!")
    buzzer.rings()
    time.sleep(0.1)
    return STATE_CRUISE, None


# 按照给定速度沿着道路前进给定的时间
def lane_time(speed, my_time):
    start_time = time.time()
    driver.set_speed(speed)
    while True:
        if check_stop():
            return STATE_IDLE, None
        front_image = front_camera.read()
        error = cruiser.infer_cnn(front_image)
        driver.steer(error)
        timeout = time.time()
        if timeout - start_time > my_time:
            driver.stop()
            break


# 巡航模式
def cruise_handler(params=None):
    global order_num
    # 设置小车巡航速度
    global sign_list
    global cam_dir
    driver.set_speed(25)
    if order_num == 1 :
        driver.set_speed(25)
    else:
        driver.set_speed(40)
    if  params == 7 :
        driver.set_speed(45)
    if order_num == 3 or params == 4 or params == 6 or params ==10:
        driver.set_speed(40)
    if order_num == 9 :
        driver.set_kx(0.6)
        driver.set_speed(30)

    # driver.set_kx(0.84)
    servo1.servo_control(task[order_num]['angle'], 50)
    if task[order_num]['angle'] == -80:
        cam_dir = -1
    else:
        cam_dir = 1

    # lane_time(30, 1)
    # driver.set_speed(20)
    while True:
        if check_stop():
            return STATE_IDLE, None
        front_image = front_camera.read()
        angle = cruiser.infer_cnn(front_image)
        driver.steer(angle)
        # 侦测车道上有无标志图标
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            print(res)
            for sign in res:
                if sign.index == task[order_num]['sign']:
                    # angle = sign.error_from_center()[0] / 150
                    # driver.steer(angle)
                    # 获取标志识别结果，获得所在列表的索引值

                    sign_list[sign.index] += 1
                    # 连续加测到一定次数，认为检测到，进入到任务定位程序
                    if sign_list[sign.index] > REC_NUM:
                        print('*****', res, '*****')

                        return STATE_LOCATE_TASK, order_num

        else:
            sign_list = [0] * 7


def lane_test():
    while True:
        front_image = front_camera.read()
        angle = cruiser.infer_cnn(front_image)
        print(angle)
        time.sleep(0.5)


# 标志位置测试
def sign_detecte_test():
    while True:

        front_image = front_camera.read()
        res_front = sign_detector.detect(front_image)
        if len(res_front) > 0:
            print(res_front)
            time.sleep(0.01)


# 任务位置测试
def task_detecte_test():
    while True:

        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            print(res_side)
            time.sleep(1)


def walk_sign(params):
    is_run = True
    while is_run:
        continue_flag = 0
        front_image = front_camera.read()
        # 计算标签偏移，根据标签前进
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            for sign in res:
                print(sign)
                _x, _y = sign.error_from_center()
                print("from center x is{}, y is {}".format(_x, _y))
                if (sign.box[3] - sign.box[1]) < 160:
                    pass
                    # is_run = False
                if _y > 130:
                    is_run = False
                elif _y < 0:
                    continue_flag = 1
                    continue
                if sign.index == task[params]['sign']:
                    angle = _x / 160
                    driver.steer(angle)

        if continue_flag == 1:
            angle = cruiser.infer_cnn(front_image)
            driver.steer(angle)

    driver.stop()


def walk_seesaw():
    is_run = True
    start_t = time.time() + 2.3
    while is_run:
        front_image = front_camera.read()
        # 计算标签偏移，根据标签前进
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            for sign in res:
                if sign.index == task[8]['sign']:

                    _x, _y = sign.error_from_center()
                    if _y > 50 and abs(_x) < 20:
                        start_t = time.time()
                    if _y > 200:
                        print("nearly")
                        is_run = False
                    if (sign.box[3] - sign.box[1]) < 150:
                        print("height is low")
                        is_run = False
                    angle = _x / 200
                    driver.steer(angle)
        if time.time() - start_t > 0.5:
            is_run = False
            print("time out")
    driver.stop()


# 寻找任务目标
def task_lookfor(params=None):
    start_time = time.time()

    print("looking for task")
    if params == 1 :
        driver.set_speed(15)
    if params == 9:
        driver.run(20, 20)
        time.sleep(3.5)
        driver.stop()
    find_flag = False
    if params == 10:
        driver.run(30,30)
        time.sleep(2)
        distance(3)
    if params == 3 or params == 4 or params == 6:
        driver.run(30, 30)
        time.sleep(2)
        distance(2)
    while find_flag is not True:
        side_image = side_camera.read()
        # print(side_image)
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            for res in res_side:
                if res.index in task[params]['index']:

                    # 标签到一定位置退出循环
                    global trade_y
                    _x, _y, trade_y = res.error_from_point(task_functions[res.index]['position'])
                    _x = _x * cam_dir
                    print("find trade distance is:", trade_y)
                    print("find task,distance is:", _x)

                    if task_functions[res.index]['location'] == False:
                        # 不需要定位直接做任务
                        print("do not location ")
                        print("do not location ")
                        return res.index
                    else:
                        driver.run(20, 20)
                    if _x > POSITION_THRESHOLD:
                        driver.run(-20, -20)
                        return res.index
                    elif _x > 0 - POSITION_THRESHOLD:
                        return res.index
            # else:
            #     front_image = front_camera.read()
            #     angle = cruiser.infer_cnn(front_image)
            #     driver.steer(angle)
            current_time = time.time()
            # 长时间未到达位置
            if current_time - start_time > LOCATE_TIME:
                return STATE_CRUISE


def location_ok(params=None):
    start_time = time.time()
    location_flag = False
    while location_flag is not True:
        # if params == 10:
        #     distance(3)
        #     adjust_angle()
        # if params == 3 or params == 4 or params == 6:
        #     distance(2)
        #     adjust_angle()
        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            for res in res_side:
                if res.index in task[params]['index']:
                    # 标签到一定位置退出循环
                    _x, _y, trade_y = res.error_from_point(task_functions[res.index]['position'])
                    print("tradetradetrade")
                    print(trade_y)
                    print("distance is", _x)
                    print(cam_dir)
                    _x = _x * cam_dir
                    print(_x)
                    if _x < 0 - POSITION_THRESHOLD:
                        print("front")
                        driver.run(30, 30)
                        time.sleep(1)
                        driver.stop()
                    elif _x > POSITION_THRESHOLD:
                        print("back")
                        driver.run(-30, -30)
                        time.sleep(1)
                        driver.stop()
                    else:
                        driver.stop()
                        print("location ok")
                        return STATE_DO_TASK, res.index
        current_time = time.time()
        # 长时间未到达位置
        if current_time - start_time > 3:
            return STATE_CRUISE, None


def locate_task_handler(params=None):
    global order_num
    global cam_dir

    walk_sign(params)

    adjust_angle()
    if task[params]['check'] is not True:
        order_num += 1
        print("ready to do task")
        return STATE_DO_TASK, task[params]['index'][0]

    print("sign location ok!")
    order_num += 1
    # if task[params]['location']:
    #     driver.set_speed(15)
    #     print("speed is 15")
    # else:
    #     driver.set_speed(20)
    #     print("speed is 20")
    driver.steer(0)

    if order_num > 11:
        order_num = 11

    print("looking for task")

    index = task_lookfor(params)
    if task_functions[index]['location'] == False:
        return STATE_DO_TASK, index
    print("find task!")
    # adjust_angle()
    location_ok(params)
    return STATE_DO_TASK, index


# 做任务
def do_task_handler(params=None):
    print("*******", "now do task:", str(params), task_functions[params], "*******")
    global task_9_flag

    if params == 1:  # alamutu
        driver.run(-30, -30)
        time.sleep(1)
        driver.stop()
        raise_flag(2, 4, "alamutu")
        adjust_angle()


    elif params == 2:  # bad_person1
        if cam_dir == -1:
            driver.run(-25, -25)
            time.sleep(1.5)
            driver.stop()
            print(trade_y)
            if trade_y < 130:
                print("two")
                # adjust_angle()
                shot_target2()
            else:
                print("one")
                # adjust_angle()
                shot_target()
        else:
            driver.run(-25, -25)
            time.sleep(1.5)
            driver.stop()
            print(trade_y)
            if trade_y < 110:
                print("two")
                # adjust_angle()
                shot_target2()
            else:
                # 对最矮的进行判断
                print("one")
                # adjust_an/gle()
                shot_target()

    elif params == 3:  # bad_person2
        if cam_dir == -1:
            # adjust_angle()

            driver.run(-25, -25)
            time.sleep(1.5)
            driver.stop()
            print(trade_y)
            if trade_y < 130:
                # adjust_angle()
                print("two")
                shot_target2()
            else:
                print("one")
                shot_target()
        else:
            # adjust_angle()

            driver.run(-25, -25)
            time.sleep(1.5)
            driver.stop()
            print(trade_y)
            if trade_y < 110:
                # adjust_angle()
                print("two")

                shot_target2()
            else:
                # 对最矮的进行判断
                print("one")
                shot_target()

    elif params == 4:  # dunhuang
        driver.run(-30, -30)
        time.sleep(1)
        driver.stop()
        raise_flag(2, 4, "dunhuang")
        adjust_angle()


    elif params == 5:  # friendship
        # adjust_angle()
        driver.run(-25, -25)
        time.sleep(1)
        driver.run(30, 50)
        time.sleep(1.8)
        driver.run(25, 25)
        time.sleep(1.2)
        driver.run(0, -30)
        time.sleep(2)
        driver.run(25, 25)
        time.sleep(0.6)
        driver.stop()
        test()
        driver.run(25, -25)
        time.sleep(1.2)
        driver.run(35, 35)
        time.sleep(1.3)
        driver.run(-25, 25)
        time.sleep(1)  # time.sleep(1.2)
        # driver.run(50, 50)

    elif params == 6:  # goodperson1
        pass


    elif params == 7:  # goodperson2
        pass


    elif params == 8:  # jstdb

        driver.run(-30, -30)
        time.sleep(1)
        driver.stop()
        raise_flag(2, 4, "jstdb")
        adjust_angle()


    elif params == 9:  # purchase
        driver.stop()
        # adjust_angle()
        purchase_good()
        driver.run(-20, -20)
        time.sleep(1)


    elif params == 10:  # trade
        # adjust_angle()
        driver.stop()
        adjust_angle()
        driver.run(-20, -20)
        time.sleep(2.7)
        driver.stop()
        trade_good()

        driver.run(20, 20)
        time.sleep(1.7)
        driver.stop()
        print(trade_y)
        # 如果有返回值，那么一定在一层，否则在二层
        if trade_y > 200:
            adjust_angle()

            trade_good_2()
            trade_over2()

        else:
            adjust_angle()

            trade_good_1()
            driver.run(30,30)
            time.sleep(1)
            driver.stop()
            trade_over()

    elif params == 11:  # seesaw
        lane_time(30, 2)

    return STATE_CRUISE, None


def adjust_angle():
    while True:
        frame = front_camera.read()
        angle = cruiser.infer_cnn(frame)
        print(angle)
        if angle < -0.01:
            driver.run(0, 20)
        elif angle > 0.01:
            driver.run(20, 0)
        else:
            driver.stop()
            return


state_map = {
    STATE_IDLE: idle_handler,
    STATE_CRUISE: cruise_handler,
    STATE_LOCATE_TASK: locate_task_handler,
    STATE_DO_TASK: do_task_handler,
}

if __name__ == '__main__':
    front_camera.start()
    side_camera.start()
    # 基准速度
    driver.set_speed(35)
    driver.set_kx(0.85)

    current_state = STATE_IDLE
    arg = "cruise"

    order_num = 1
    servo1 = Servo(1)
    print("sdfsdafsf")
    servo1.servo_control(task[order_num]['angle'], 50)
    buzzer = Buzzer()
    for i in range(0, 3):
        buzzer.rings()

    button_new_3 = Button(1, "3")
    while True:
        if button_new_3.clicked():
            print("start")
            print("start")
            while True:
                params = None
                # order_num = 1
                if order_num == 1:
                    lane_time(40,4)
                if order_num == 9:
                    adjust_angle()
                    # driver.run(-25, -25)
                    # time.sleep(3)
                    driver.stop()

                # idle_handler()
                # if order_num == 11:
                #     lane_time(45, 5.5)
                    # driver.run(55,55)
                    # time.sleep(2)
                    driver.stop()
                _, params = cruise_handler(order_num)
                _, params = locate_task_handler(params)
                _, params = do_task_handler(params)
                driver.stop()
