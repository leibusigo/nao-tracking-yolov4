# -*- coding: UTF-8 -*-
import cv2
import numpy as np
from naoqi import ALProxy
import vision_definitions
import math
import time
import os


# 作用：写txt
# 参数：
#    file_src：文件的路径
#    write: 要写进文件的东西
def write_txt(file_src, write):
    fw = open(file_src, 'w')
    fw.write(write)
    fw.close()


# 作用：读txt
# 返回值：读到的txt文件字符串
def read_txt(file_src):
    fr = open(file_src, 'r')
    read = fr.read()
    fr.close()

    return read


# 作用：清空指定txt文件
def clean_txt(file_src):
    fw = open(file_src, 'w')
    fw.truncate(0)
    fw.close()


# 作用：让nao拍照
# 参数:
#   resolution:显示分辨率
#   colorSpace：显示色彩
#   fps：显示fps
def take_image(resolution, colorSpace, fps):
    # 获取图片
    cameraProxy.setActiveCamera(0)
    videoClient = cameraProxy.subscribe("python_GVM", resolution, colorSpace, fps)
    frame = cameraProxy.getImageRemote(videoClient)
    cameraProxy.unsubscribe(videoClient)
    frameWidth = frame[0]
    frameHeight = frame[1]
    frameChannels = frame[2]
    frameArray = np.frombuffer(frame[6], dtype=np.uint8).reshape([frameHeight, frameWidth, frameChannels])

    # 保存图片到此绝对路径
    cv2.imwrite('../img/image.jpg', frameArray)
    time.sleep(1)


# 作用:展示图片(注意路径)
def show_image():
    image_result = cv2.imread('../img/image_result.jpg')
    if image_result is not None:
        cv2.imshow('image', image_result)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()


# 作用：测距
# 返回值：
#   Forward_Distance：nao离目标物品前向距离
#   Sideward_Distance：nao离目标物品侧向距离
def ranging():
    # 测量的方法以目标检测检测到的物品的下中心点为基准
    read_coordinate = read_txt("../txt/coordinate.txt")
    # 以“，”分隔文档，得到框坐标
    coordinate = read_coordinate.split(",")
    print (coordinate)
    top = float(coordinate[0])
    bottom = float(coordinate[1])
    left = float(coordinate[2])
    right = float(coordinate[3])
    center = (left + right) / 2
    print (top,bottom,left,right,center)
    # 检测到物品下中心点的x坐标
    cxnum = (left + right) / 2
    # 检测到物品下中心点的y坐标
    rynum = bottom
    distx = -(cxnum - 640 / 2)
    disty = rynum - 480 / 2
    Picture_angle = disty * (47.64 / 480)

    # 摄像头距离地面高度
    h = 0.51

    # 摄像头自身离水平线的倾角
    Camera_angle = 1.2
    Total_angle = Picture_angle + Camera_angle
    d1 = h / math.tan(Total_angle * math.pi / 180)
    alpha = distx * (60.92 / 640)
    d2 = d1 / math.cos(alpha * math.pi / 180)
    Forward_Distance = round(d2 * math.cos(alpha * math.pi / 180), 2)
    Sideward_Distance = round(-d2 * math.sin(alpha * math.pi / 180), 2)
    print(Forward_Distance, Sideward_Distance)

    return Forward_Distance, Sideward_Distance


# 作用：进行通信nao机器人，初始化通信文档，初始化nao机器人api等一系列初始化操作
# 返回值：
#       cameraProxy：控制nao相机的api
#       sayProxy：控制nao说话的api
#       postureProxy：控制nao动作的api
#       motionProxy：控制nao移动的api
#       turn: 控制两个不同python环境能循的标志变量
def initialization():
    port = 9559  # crf 机器人端口
    robot_ip = "192.168.3.223"  # crf 机器人IP

    # 代理naoAPI
    cameraProxy = ALProxy("ALVideoDevice", robot_ip, port)
    sayProxy = ALProxy("ALTextToSpeech", robot_ip, port)
    postureProxy = ALProxy("ALRobotPosture", robot_ip, port)
    motionProxy = ALProxy("ALMotion", robot_ip, port)

    # 初始化py3.6与py2.7通信文档
    write_txt('../txt/turn_py2.7.txt', "0")
    write_txt('../txt/turn_py3.6.txt', "1")

    #防止有stop文件没清理
    clean_txt('../txt/stop.txt')

    # 初始化机器人头角度
    write_txt('../txt/x_angle.txt', "-1")

    # 初始化机器人姿势
    motionProxy.wakeUp()
    postureProxy.goToPosture("StandInit", 0.5)

    # py2.7与py3.6程序能循的通信文件
    turn = 1

    return cameraProxy, sayProxy, postureProxy, motionProxy, turn


# 作用：控制noa转头
# 参数：angle：输入使nao偏转的角度
def turn_head(angle):
    motionProxy.setStiffnesses("Head", 1.0)
    names = ["HeadYaw", "HeadPitch"]
    # 设置转头角度[横向转头角度，纵向转头角度]
    angles = [angle, 0]
    fractionMaxSpeed = 0.2
    motionProxy.setAngles(names, angles, fractionMaxSpeed)
    # 休眠0.75s，让nao执行完转头动作
    time.sleep(0.75)
    motionProxy.setStiffnesses("Head", 0.0)


if __name__ == "__main__":
    # 执行初始化方法
    cameraProxy, sayProxy, postureProxy, motionProxy, turn = initialization()
    # 拍照方法的基本参数
    resolution = vision_definitions.kVGA
    colorSpace = vision_definitions.kBGRColorSpace
    fps = 20

    # 初始化第一轮次跟踪的标志变量
    track_turn = 1

    while True:
        # 等待py3.6完成指令
        turn_read = read_txt('../txt/turn_py3.6.txt')
        if turn_read == "":
            continue
        else:
            turn_read = int(turn_read)
            # print turn_read, turn
        if turn == turn_read and turn % 2 == 1:
            # time.sleep(2)
            turn = turn + 2
            write_txt('../txt/turn_py2.7.txt', str(turn - 1))

            read_x_angle = read_txt('../txt/x_angle.txt')
            x_angle = float(read_x_angle)

            # 由于py3.6第一次执行就会进行目标检测，所以可能检测上次运行程序所拍摄的照片。
            # 故先跳过第一轮检测
            if turn == 3:
                turn_head(x_angle)

                take_image(resolution, colorSpace, fps)
                continue
            else:
                sentence1 = read_txt('../txt/stop.txt')
                time.sleep(2)
                sentence2 = read_txt('../txt/flag.txt')
                # 如果读取到停止指令，程序完成
                if sentence1 == 'stop':
                    clean_txt('../txt/stop.txt')
                    motionProxy.rest()
                    break
                else:
                    # 如果没检测到物品，转头0.25并进行下一轮拍照
                    if sentence2 == 'none':
                        # sayProxy.say("未检测到物品")
                        # 如果是第二轮次的检测，因为要先在原方向上拍照检测一次，
                        # 如果没检测到物品就重新回到-1角度拍照寻找目标
                        if track_turn is not 1:
                            write_txt('../txt/x_angle.txt', "-1")
                            track_turn = 1
                        else:
                            # 设定的偏头角度范围-1~1
                            if x_angle <= 0.75:
                                x_angle = x_angle + 0.25
                                write_txt('../txt/x_angle.txt', str(x_angle))
                                turn_head(x_angle)
                            # 如果-1~1一个周期都未检测到目标，则判定视野范围内无目标，程序停止
                            else:
                                sayProxy.say("未检测到物品")
                                write_txt('../txt/stop.txt', 'stop')
                                continue
                        take_image(resolution, colorSpace, fps)
                        clean_txt('../txt/flag.txt')
                        continue
                    else:
                        # 执行展示照片程序
                        show_image()

                        if track_turn == 1:
                            # 调整机器人角度，nao的movTo属性三个参数[直走的距离，横走的距离，旋转的角度]
                            motionProxy.moveTo(0, 0, x_angle)
                        # 每次机器人行动后，头都会向下偏，执行程序让头回正
                        turn_head(0)

                        try:
                            # 执行测量程序
                            Forward_Distance, Sideward_Distance = ranging()
                            if turn_read > 1:
                                if Forward_Distance > 1.09:
                                    sayProxy.say("开始跟踪")
                                    motionProxy.moveTo(Forward_Distance - 1.09, 0, 0)

                                    turn_head(0)

                                    take_image(resolution, colorSpace, fps)

                                    # 执行完第一轮次跟踪程序后，让nao优先在原方向上再进行一次检测
                                    track_turn += 1

                                    clean_txt('../txt/coordinate.txt')
                                    # time.sleep(2)
                                    file_name = '../img/image_result.jpg'
                                    # 删除目标检测结果图片，避免影响nao机器人程序执行
                                    if os.path.exists(file_name):
                                        os.remove(file_name)
                                        # time.sleep(2)
                                else:
                                    sayProxy.say("完成跟踪")
                                    write_txt('../txt/stop.txt', 'stop')
                        except:
                            continue
