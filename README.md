# 基于nao机器人实现yolov4目标检测并进行跟踪
## Introduction - 介绍
本项目为yolov4算法在nao机器人上的应用。<br><br>
**关于YOLOv4原理请参考[YOLOv4原论文](https://arxiv.org/pdf/2004.10934.pdf)<br>
本项目主要YOLOv4框架参考Bubbliiiing博主复现的代码<br>
原博客链接：https://blog.csdn.net/weixin_44791964/article/details/106214657<br>
复现代码链接：https://github.com/bubbliiiing/yolov4-pytorch<br>
nao机器人单目测距方法请参考：https://wenku.baidu.com/view/bdc7eea7482fb4daa48d4b24.html<br>
使用本项目前请先下载复现YOLOv4代码，并用py3.6文件夹中.py文件替换原文件中的同名文件<br>**<br><br>
下图为目标跟踪流程图。由于nao机器人sdk库naoqi仅支持py2.7环境,本项目需分别运行py2.7环境下的"封装跟踪.py"文件和py3.6环境下的"predict.py"文件。<br>
该项目可以让nao机器人转头寻找水瓶目标，检测到目标后通过单目测距向目标前进，当目标距离和nao小于1.09m时，程序完成运行。
![image](https://github.com/leibusigo/nao-tracking-yolov4/blob/main/img/nao%E6%9C%BA%E5%99%A8%E4%BA%BA%E8%B7%9F%E8%B8%AA%E6%B5%81%E7%A8%8B.png)
## Requirements - 必要条件
### **py2.7环境**<br>
numpy==1.16.6+vanilla<br>
opencv-python==2.4.13.7<br>
Pillow==6.2.2<br>
pynaoqi==2.1.4.13<br>
### **tips**
**naoqi库为软银官方提供的nao机器人sdk<br>naoqi库百度云链接：链接: https://pan.baidu.com/s/1kib-Bx9BjiOXCjrIycsIAw 提取码: 5k8b**
***
### **py3.6环境**<br>
torch==1.2.0 <br>
cuda>=10.0.0<br>
参考环境见[py3.6环境文件](https://github.com/leibusigo/nao-tracking-yolov4/blob/main/3.6%E7%8E%AF%E5%A2%83/requirements.txt)(**仅供参考，因为包含了很多自用无关的库**)
## Configuration - 配置
使用本项目前请先下载复现YOLOv4代码，并用py3.6文件夹中.py文件替换原文件中的同名文件<br>
YOLOv4环境的配置方法:<br>
**1.将训练好的只检测水瓶类的权重文件放入model_data文件夹，并替换yolo.py中的初始路径<br>
2.把model_data文件夹下的voc_classes.txt文件中物品类别改为只有bottle<br>
3.更多问题详见Bubbliiiing博文。<br><br>**
本项目跟踪的只有水瓶类，所以训练时只提取了VOC2007数据集中的水瓶类别<br>
只有水瓶类别的VOC2007数据集百度云链接：链接: https://pan.baidu.com/s/1d11f3lm2BvPtwxXuRYZ5HQ 提取码: w2kn <br>
训练好的只检测水瓶类的权重百度云链接: 链接: https://pan.baidu.com/s/1Qt__j8RAOZeRbY8BjXitpA 提取码: 5u2b <br><br>
## Usage - 用法
配置好py3.6和py2.7环境后。先运行"封装跟踪.py"文件，再运行"predict.py"文件。<br>
检测到的图片信息可见于img文件夹<br>
## Changelog - 更新日志
## License - 版权信息
本项目证书为GPL-3.0 License，详见[GPL-3.0 License.md](https://github.com/leibusigo/nao-tracking-yolov4/blob/main/LICENSE)
