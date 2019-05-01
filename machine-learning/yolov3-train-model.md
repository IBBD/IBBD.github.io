# 使用yolov3训练目标检测模型

## 步骤

### step01 下载yolov3项目工程

按照YoLo官网下载`git clone https://github.com/pjreddie/darknet`


### step02 标注数据

标注工具`Vott`，最后得到的数据集：

```
voc
--VOCdevkit 
----VOCname        # 可以定义一个名字
------Annotations  # 放入所有的xml文件
------ImageSets    
--------Main       # 放入train.txt,val.txt文件
------JPEGImages   # 放入所有的图片文件
```

有效的标注好的图片数量530+.

### step03 修改Makefile文件及编译

```sh
cd darknet
vim Makefile

# 内容如下：
GPU=1
CUDNN=1
OPENCV=0  # 本地有安装opencv，但是设置该值为1的时候会报错
OPENMP=0
DEBUG=0

# 修改好之后，编译
make
```

### step04 修改voc_label.py, 生成训练数据

脚本在scripts目录，[修改后的脚本](./yolov3-voc_label.py)， 该脚本保存到`voc`目录，并执行。在voc下生成了helmet_helmet_train_utf8.txt 和 helmet_helmet_val_utf8.txt，分别存放了训练集和测试集图片的路径。 
### step05 下载预训练模型

`wget https://pjreddie.com/media/files/darknet53.conv.74`

### step06 修改cfg/voc.data

```sh
classes= 1
train  = /video/darknet/voc/helmet_helmet_train_utf8.txt
valid  = /video/darknet/voc/helmet_helmet_val_utf8.txt
names = data/voc.names
backup = backup
```

主要是类别数量，而train和valid这两个路径就是在step04生成的文件的路径。

### step07 修改data/voc.names

```
helmet
```

这个是检测的目录类别的名字

### step08 修改cfg/yolov3-voc.cfg
主要修改如下：

```sh
[net]
batch=16
subdivisions=4
```

### step09 开始训练

`./darknet detector train cfg/voc.data cfg/yolov3-voc.cfg darknet53.conv.74`

在我的1050TI下运行:

```
8779: 0.389947, 0.476666 avg, 0.001000 rate, 1.363752 seconds, 140464 images Loaded: 0.000063 seconds
```

GPU使用情况如下：

```
|===============================+======================+======================|
|   0  GeForce GTX 105...  Off  | 00000000:01:00.0 Off |                  N/A |
| 26%   61C    P0    N/A /  75W |   2273MiB /  4031MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+
```

显存占用不算高，batch参数应该可以再大一些。



