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
CUDNN=0   # 设置为1时，超出内存。。。
OPENCV=0  # 本地有安装opencv，但是设置该值为1的时候会报错
OPENMP=0  # 如果使用cpu训练，设置该值为1，不然只会使用单个cpu
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
batch=1
subdivisions=1

# ....

[convolutional]
size=1
stride=1
pad=1
filters=18   # 这里原来是75=3*(len(classes)+5)，我们的类别数为1，则这里为18。有几个75都要修改过来，否则会报错
activation=linear
```

subdivision：这个参数很有意思的，它会让你的每一个batch不是一下子都丢到网络里。而是分成subdivision对应数字的份数，一份一份的跑完后，在一起打包算作完成一次iteration。这样会降低对显存的占用情况。如果设置这个参数为1的话就是一次性把所有batch的图片都丢到网络里，如果为2的话就是一次丢一半。

1050TI太渣了，只能设成1才不至于超出内存。。。

### step09 开始训练

`./darknet detector train cfg/voc.data cfg/yolov3-voc.cfg darknet53.conv.74`

在我的1050TI下运行:

```
8779: 0.389947, 0.476666 avg, 0.001000 rate, 1.363752 seconds, 140464 images 
Loaded: 0.000063 seconds

# 输出参数说明：
8779： 指示当前训练的迭代次数
0.389947： 是总体的Loss(损失）
0.476666 avg： 是平均Loss，这个数值应该越低越好，一般来说，一旦这个数值低于0.060730 avg就可以终止训练了。
0.0001000 rate： 代表当前的学习率，是在.cfg文件中定义的。
1.363752 seconds： 表示当前批次训练花费的总时间。
140464 images： 这一行最后的这个数值是8779*16的大小，表示到目前为止，参与训练的图片的总量。
```

貌似loss一直这里徘徊，在1500次后基本没有实质的下降。

GPU使用情况如下：

```
|===============================+======================+======================|
|   0  GeForce GTX 105...  Off  | 00000000:01:00.0 Off |                  N/A |
| 26%   61C    P0    N/A /  75W |   2273MiB /  4031MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+
```

显存占用不算高，但是如果batch参数设置

### step10 测试

训练之后，会在backup目录生成权重文件：

```sh
$ ls backup
yolov3-voc_100.weights  yolov3-voc_400.weights  yolov3-voc_700.weights  yolov3-voc.backup
yolov3-voc_200.weights  yolov3-voc_500.weights  yolov3-voc_800.weights
yolov3-voc_300.weights  yolov3-voc_600.weights  yolov3-voc_900.weights

# 执行测试
./darknet detector test cfg/voc.data cfg/yolov3-voc.cfg backup/yolov3-voc_900.weights data/210.jpg
```

### step11 转成keras模型

使用`https://github.com/qqwweee/keras-yolo3/`提供的转换程序：

```sh
python convert.py ../darknet/cfg/yolov3-voc.cfg ../darknet/backup/yolov3-voc_10000.weights model_data/yolov3_helmet.h5
```

报错如下：

```
Traceback (most recent call last):
  File "convert.py", line 262, in <module>
    _main(parser.parse_args())
  File "convert.py", line 235, in _main
    'Unsupported section header type: {}'.format(section))
ValueError: Unsupported section header type: reorg_0
```

改成用：`https://github.com/allanzelener/YAD2K/blob/master/yad2k.py`成功。


## 踩坑问题

https://blog.csdn.net/Pattorio/article/details/80051988


