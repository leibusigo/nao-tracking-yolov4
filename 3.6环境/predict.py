from PIL import Image
import cv2
from yolo import YOLO
import numpy as np
import time



# 写txt
def write_txt(file_src, write):
    fw = open(file_src, 'w')
    fw.write(write)
    fw.close()


# 读txt
def read_txt(file_src):
    fr = open(file_src, 'r')
    read = fr.read()
    fr.close()

    return read


if __name__ == "__main__":

    yolo = YOLO()
    flag = True
    turn = 2

    while True:
        sentence1 = read_txt('../txt/stop.txt')
        if sentence1 == 'stop':
            break
        else:
            # 等待py2.7完成指令
            turn_read = read_txt('../txt/turn_py2.7.txt')
            if turn_read == "":
                continue
            else:
                turn_read = int(turn_read)
                # print(turn_read, turn)
            if turn == turn_read and turn % 2 == 0:
                # time.sleep(2)
                turn = turn + 2
                write_txt('../txt/turn_py3.6.txt', str(turn - 1))

                image = Image.open('../img/image.jpg')
                # 使用目标检测算法对图片进行检测
                r_image, flag = yolo.detect_image(image, flag)
                # 将得到的数组转化为图片的形式
                r_image = np.array(r_image, np.uint8)
                # 将颜色从BGR转换为RGB
                r_image = cv2.cvtColor(r_image, cv2.COLOR_BGR2RGB)
                if flag:
                    cv2.imwrite('../img/image_result.jpg', r_image)
                    time.sleep(1)
                else:
                    write_txt('../txt/flag.txt', "none")
                    flag = True
