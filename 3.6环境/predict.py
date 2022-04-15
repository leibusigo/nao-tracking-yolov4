from PIL import Image
import cv2
from yolo import YOLO
import numpy as np
import time
from paddleocr import PaddleOCR, draw_ocr
import re


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


# 作用：清空指定txt文件
def clean_txt(file_src):
    fw = open(file_src, 'w')
    fw.truncate(0)
    fw.close()


# 用paddle ocr进行图片文字检测
def ocr_test(r_image, top, bottom, left, right):
    cropImg = r_image[top:bottom, left:right]
    cv2.imwrite('../img/cut_result.jpg', cropImg)
    # time.sleep(2)
    zoom = interpolation(cropImg, top, bottom, left, right)
    # Paddleocr目前支持中英文、英文、法语、德语、韩语、日语，可以通过修改lang参数进行切换
    # 参数依次为`ch`, `en`, `french`, `german`, `korean`, `japan`。
    ocr = PaddleOCR(use_angle_cls=True, lang="en")  # need to run only once to download and load model into memory
    result = ocr.ocr(zoom, cls=True)
    i = 0
    textArr = []
    while i < len(result):
        textArr.append(result[i][1][0])
        # print(result[i][1][0])
        i += 1
    print(textArr)
    return textArr


# 双三次插值主程序
def interpolation(cropImg, top, bottom, left, right):
    zoom = function(cropImg, (bottom - top) * 5, (right - left) * 5)
    cv2.imwrite("../img/result_1.jpg", zoom)
    time.sleep(2)

    return zoom


# 双三次插值内部执行函数
def S(x):
    x = np.abs(x)
    if 0 <= x < 1:
        return 1 - 2 * x * x + x * x * x
    if 1 <= x < 2:
        return 4 - 8 * x + 5 * x * x - x * x * x
    else:
        return 0


# 双三次插值
def function(img, m, n):
    height, width, channels = img.shape
    emptyImage = np.zeros((m, n, channels), np.uint8)
    sh = m / height
    sw = n / width
    for i in range(m):
        for j in range(n):
            x = i / sh
            y = j / sw
            p = (i + 0.0) / sh - x
            q = (j + 0.0) / sw - y
            x = int(x) - 2
            y = int(y) - 2
            A = np.array([
                [S(1 + p), S(p), S(1 - p), S(2 - p)]
            ])
            if x >= m - 3:
                m - 1
            if y >= n - 3:
                n - 1
            if x >= 1 and x <= (m - 3) and y >= 1 and y <= (n - 3):
                B = np.array([
                    [img[x - 1, y - 1], img[x - 1, y],
                     img[x - 1, y + 1],
                     img[x - 1, y + 1]],
                    [img[x, y - 1], img[x, y],
                     img[x, y + 1], img[x, y + 2]],
                    [img[x + 1, y - 1], img[x + 1, y],
                     img[x + 1, y + 1], img[x + 1, y + 2]],
                    [img[x + 2, y - 1], img[x + 2, y],
                     img[x + 2, y + 1], img[x + 2, y + 1]],
                ])
                C = np.array([
                    [S(1 + q)],
                    [S(q)],
                    [S(1 - q)],
                    [S(2 - q)]
                ])
                blue = np.dot(np.dot(A, B[:, :, 0]), C)[0, 0]
                green = np.dot(np.dot(A, B[:, :, 1]), C)[0, 0]
                red = np.dot(np.dot(A, B[:, :, 2]), C)[0, 0]

                # ajust the value to be in [0,255]
                def adjust(value):
                    if value > 255:
                        value = 255
                    elif value < 0:
                        value = 0
                    return value

                blue = adjust(blue)
                green = adjust(green)
                red = adjust(red)
                emptyImage[i, j] = np.array([blue, green, red], dtype=np.uint8)

    return emptyImage


if __name__ == "__main__":

    yolo = YOLO()
    flag = True
    turn = 2
    run = 1

    while True:
        sentence1 = read_txt('../txt/stop.txt')
        if sentence1 == 'stop':
            clean_txt('../txt/turn_py3.6.txt')
            write_txt('../txt/turn_py3.6.txt', str(turn + 1))
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
                print("第" + str(run) + "轮")
                run += 1
                # time.sleep(2)
                turn = turn + 2

                image = Image.open('../img/image.jpg')
                # 使用目标检测算法对图片进行检测
                r_image, flag, top, bottom, left, right = yolo.detect_image(image, flag)
                print(top, bottom, left, right)
                # 将得到的数组转化为图片的形式
                r_image = np.array(r_image, np.uint8)
                # 将颜色从BGR转换为RGB
                r_image = cv2.cvtColor(r_image, cv2.COLOR_BGR2RGB)
                cv2.imwrite('../img/detect_image.jpg', r_image)
                print(flag)
                if flag:
                    for num in range(len(top)):
                        textArr = ocr_test(r_image, top[num], bottom[num], left[num], right[num])
                        print(textArr)
                        i = 0
                        if len(textArr) != 0:
                            text = textArr[0]
                            print(text)
                            regexp = re.compile(r'H')
                            if regexp.search(text):
                                print("yes")
                                cv2.imwrite('../img/image_result.jpg', r_image)
                                write_txt('../txt/turn_py3.6.txt', str(turn - 1))
                                write_txt('../txt/coordinate.txt',str(top[num])+","+str(bottom[num])+","+str(left[num])+","+str(right[num]))
                                time.sleep(1)
                            else:
                                print("not this bottle!")
                                write_txt('../txt/flag.txt', "none")
                                write_txt('../txt/turn_py3.6.txt', str(turn - 1))
                                time.sleep(1)
                        else:
                            print("not this bottle!")
                            write_txt('../txt/flag.txt', "none")
                            write_txt('../txt/turn_py3.6.txt', str(turn - 1))
                            time.sleep(1)
                else:
                    write_txt('../txt/flag.txt', "none")
                    write_txt('../txt/turn_py3.6.txt', str(turn - 1))
                    time.sleep(1)
                    flag = True
