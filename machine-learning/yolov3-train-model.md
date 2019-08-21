# 使用yolov3训练目标检测模型

## 步骤

### step01 下载yolov3项目工程

按照YoLo官网下载`git clone https://github.com/pjreddie/darknet`

https://github.com/AlexeyAB/darknet : 事实证明用这个来编译会更加高效，当然GPU得支持。


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

https://github.com/AlexeyAB/darknet/blob/master/Makefile 这个的可配置项比较多，可以配置如下：

```sh
# set GPU=1 and CUDNN=1 to speedup on GPU
# set CUDNN_HALF=1 to further speedup 3 x times (Mixed-precision on Tensor Cores) GPU: Volta, Xavier, Turing and higher
# set AVX=1 and OPENMP=1 to speedup on CPU (if error occurs then set AVX=0)
GPU=1
CUDNN=1
CUDNN_HALF=1
OPENCV=0
AVX=0
OPENMP=0
LIBSO=0
ZED_CAMERA=0

# 如果是2080TI，还可以开启如下配置
# GeForce RTX 2080 Ti, RTX 2080, RTX 2070, Quadro RTX 8000, Quadro RTX 6000, Quadro RTX 5000, Tesla T4, XNOR Tensor Cores
ARCH= -gencode arch=compute_75,code=[sm_75,compute_75]
```

加上配置CUDNN_HALF和ARCH，性能约能提升三倍，显存占用也没有明显提升。


### step04 修改voc_label.py, 生成训练数据

脚本在scripts目录，[修改后的脚本](./yolov3-voc_label.py)， 该脚本保存到`voc`目录，并执行。在voc下生成了helmet_helmet_train.txt 和 helmet_helmet_val.txt，分别存放了训练集和测试集图片的路径。 

如果有多个train文件或者val文件，则可以合并成单一的train文件和val文件。

```sh
cat *_train.txt > train.txt
cat *_val.txt > val.txt
```

注意：需要进入容器内运行。

### step05 下载预训练模型

`wget https://pjreddie.com/media/files/darknet53.conv.74`

### step06 修改cfg/voc.data

```sh
classes= 1
train  = voc/helmet_train_utf8.txt
valid  = voc/helmet_val_utf8.txt
names = data/voc.names
backup = backup     # 训练的时候，该目录必须存在
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
# 如果是1050TI，可能这两个值都只能设置为1才不至于超出内存
batch=64
subdivisions=16
max_batches = 2000   # classes*2000
step = 1600,1800     # change line steps to 80% and 90% of max_batches
width=416            # 
height=416

# ....

[yolo]
classes=2         # 有三处需要修改

[convolutional]
size=1
stride=1
pad=1
filters=18   # 这里原来是75=3*(len(classes)+5)，我们的类别数为1，则这里为18。有几个75都要修改过来，否则会报错: filters=(classes + 5)x3
activation=linear
```

subdivision：这个参数很有意思的，它会让你的每一个batch不是一下子都丢到网络里。而是分成subdivision对应数字的份数，一份一份的跑完后，在一起打包算作完成一次iteration。这样会降低对显存的占用情况。如果设置这个参数为1的话就是一次性把所有batch的图片都丢到网络里，如果为2的话就是一次丢一半。

参数说明：
- https://www.twblogs.net/a/5bc0da662b717711c923fb3b/zh-cn/

### step09 开始训练

```sh
./darknet detector train cfg/voc.data cfg/yolov3-voc.cfg darknet53.conv.74

# 如果使用多GPU训练
./darknet detector train cfg/voc.data cfg/yolov3-voc.cfg darknet53.conv.74 -gpus 0,1
./darknet detector train cfg/gf.voc.data cfg/gf-yolo3-voc.cfg darknet53.conv.74 -gpus 0,1

# 如果想暂停训练，并且从断点开始训练
./darknet detector train cfg/coco.data cfg/yolov3.cfg backup/yolov3.backup -gpus 0,1


# 写成一个脚本如下：
start_data=$(date)
./darknet detector train cfg/voc.data cfg/yolov3-voc.cfg darknet53.conv.74 -gpus 0,1
echo "start: $start_data"
echo "end: " $(date)
```

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

训练完成会输出：

```sh
Saving weights to backup/yolov3-voc.backup
Saving weights to backup/yolov3-voc_final.weights
```

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
python3 convert.py ../darknet/cfg/yolov3-voc.cfg \
    ../darknet/backup/yolov3-voc_final.weights model_data/yolov3_helmet.h5

# 输出
Saved Keras model to model_data/yolov3_helmet.h5
Read 61576342 of 61576342.0 from Darknet weights.
```

### step12 使用keras测试

```sh
# 图片
python3 yolo_video.py --image --model=model_data/yolov3_helmet.h5 \
    --anchors=model_data/yolov3_anchors.txt \
    --classes=model_data/yolov3_classes.txt 

# 视频
# 如果在服务器运行得注释掉两行代码，还的增加一行代码
# if return_value is False: break
# 输出avi需要修改：video_FourCC = cv2.VideoWriter_fourcc(*'XVID')
# 如果是服务器还得把 cv2.imshow("result", result) 这附件的两行注释掉
python3 yolo_video.py --model=model_data/yolov3_helmet.h5 \
    --input=../工作服安全帽.mp4 --output=out.avi \
    --anchors=model_data/yolov3_anchors.txt \
    --classes=model_data/yolov3_classes.txt 
```

这个脚本有问题，参数可以直接修改yolo.py

说明：anchors参数对应的文件的值来自训练时的cfg/yolov3-voc.cfg这个文件中对应的值：

```sh
[yolo]
mask = 6,7,8
anchors = 10,13,  16,30,  33,23,  30,61,  62,45,  59,119,  116,90,  156,198,  373,326
classes=1
```

把对应的anchors的值复制到文件model_data/yolov3_anchors.txt即可。


## 踩坑问题

https://blog.csdn.net/Pattorio/article/details/80051988

### Error: l.outputs == params.inputs

- cfg配置文件中classes和filter关系是否对应


### 超出内存Out of memory

主要调节配置文件subdivisions和batch参数，Makfile中的cudnn也可以关闭

### Darknet yoloV3 训练VOC数据集时不收敛 “-nan”报错或者检测无效果

50200: -nan, nan avg, 0.000010 rate, 0.434793 seconds, 50200 images

主要是对于yolov3-voc.cfg文件。其中的batch和subvision训练和测试的时候应当是不一样的。默认的都是1，那是测试的时候的批次数量。在训练的时候我是改成batch=64，subversion=16；基本训练就没啥问题，也会有“nan”的报告，但是基本网络还是能够收敛的。

### 使用的配置文件可能并不是yolov3的

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

改成用：`https://github.com/allanzelener/YAD2K/blob/master/yad2k.py`成功，但这可能并不是需要的。





