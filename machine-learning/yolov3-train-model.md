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

- 加上配置CUDNN_HALF和ARCH，性能约能提升三倍，显存占用也没有明显提升。
- 如果需要打开opencv=1，则需要安装：libopencv-dev

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

### step08 修改cfg/yolov3-voc.cfg（cfg/yolov3-spp.cfg使用该结构的效果会更好）
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

# update_num小于burn_in时，不是使用配置的学习速率更新策略，而是按照下面的公式更新
# lr = base_lr * power(batch_num/burn_in,pwr)
# 全局最优点就在网络初始位置附近，所以训练开始后的burn_in次更新，学习速率从小到大变化。
# update次数超过burn_in后，采用配置的学习速率更新策略从大到小变化，显然finetune时可以尝试。
burn_in=1000         # 这个值默认为1000，类别比较少时可以改小一点

# ....

[yolo]
classes=2         # 有三处需要修改，tiny有两处

[convolutional]
size=1
stride=1
pad=1
filters=18   # 这里原来是75=3*(len(classes)+5)，我们的类别数为1，则这里为18。有几个75都要修改过来，否则会报错: filters=(classes + 5)x3
activation=linear  # 注意这里，filter不要修改错了
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

在训练yolov4时，需要加上一个参数：`-dont_show`

在我的1050TI下运行:

```
8779: 0.389947, 0.476666 avg, 0.001000 rate, 1.363752 seconds, 140464 images 
Loaded: 0.000063 seconds

# 输出参数说明：
8779： 指示当前训练的迭代次数
0.389947： 是总体的Loss(损失）
0.476666 avg： 是平均Loss，这个数值应该越低越好，一般来说，一旦这个数值低于0.06 avg就可以终止训练了。
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

关于训练的说明：

- 如果你在avg loss里看到nan，意味着训练失败；在其他地方出现nan则是正常的。
- 如果出错并显示Out of memory，尝试将.cfg文件的subdivisions值增大（建议为2n）。
- 使用附加选项-dont_show来关闭训练时默认显示的损失曲线窗口
- 使用附加选项-map来显示mAP值
- 训练完成后的权重将保存于你在.data文件中设置的backup值路径下
- 你可以从backup值的路径下找到你的备份权重文件，并以此接着训练模型

### step10 计算mAP

yolov3-tiny的指标如下：

```
./darknet detector map cfg/gf.voc.data cfg/yolov3-tiny-gf.cfg backup/yolov3-tiny-gf_final.weights

# 预测时间: 
# cpu: 626.867000
# cpu+avx+openmp: 86.209000
# gpu: 281.105000
# gpu+cudnn: 2.588000
# gpu+cudnn_half: 2.860000

# output（有省略）:
Total BFLOPS 5.452 

 calculation mAP (mean average precision)...
1300
 detections_count = 3280, unique_truth_count = 1842  
class_id = 0, name = idcard, ap = 99.68%   	 (TP = 397, FP = 6) 
class_id = 1, name = idcard_back, ap = 99.50%   	 (TP = 315, FP = 2) 
class_id = 2, name = logo, ap = 97.10%   	 (TP = 791, FP = 145) 
class_id = 3, name = jobcard, ap = 99.49%   	 (TP = 312, FP = 18) 

 for thresh = 0.25, precision = 0.91, recall = 0.99, F1-score = 0.95 
 for thresh = 0.25, TP = 1815, FP = 171, FN = 27, average IoU = 77.33 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 0.989424, or 98.94 % 
Total Detection Time: 5.000000 Seconds
```

对比yolov3-spp指标：

```
Total BFLOPS 140.320
class_id = 0, name = idcard, ap = 99.72%   	 (TP = 398, FP = 4) 
class_id = 1, name = idcard_back, ap = 99.66%   	 (TP = 316, FP = 1) 
class_id = 2, name = logo, ap = 97.81%   	 (TP = 793, FP = 100) 
class_id = 3, name = jobcard, ap = 99.53%   	 (TP = 313, FP = 13) 

 for thresh = 0.25, precision = 0.94, recall = 0.99, F1-score = 0.96 
 for thresh = 0.25, TP = 1820, FP = 118, FN = 22, average IoU = 83.81 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 0.991824, or 99.18 % 
Total Detection Time: 20.000000 Seconds
```

对比enetb0的指标:

```
# 训练命令
# 需要先生成: enetb0.conv.15
./darknet partial cfg/enet-gf.cfg enetb0-coco_final.weights enetb0.conv.15 15
./darknet detector train cfg/gf.voc.data cfg/enet-gf.cfg enetb0.conv.15 -gpus 0,1

# 训练耗时: 约200分钟
8000: 0.129793, 0.129020 avg loss, 0.000020 rate, 2.997015 seconds, 1024000 images

# 预测时间: 
# cpu: 574.930000
# cpu+avx+openmp: 274.690000
# gpu: 346.442000
# gpu+cudnn: 17.471000
# gpu+cudnn_half: 18.417000

# 指标
Total BFLOPS 3.671
class_id = 0, name = idcard, ap = 99.43%   	 (TP = 397, FP = 6) 
class_id = 1, name = idcard_back, ap = 99.67%   	 (TP = 316, FP = 1) 
class_id = 2, name = logo, ap = 95.57%   	 (TP = 759, FP = 92) 
class_id = 3, name = jobcard, ap = 99.80%   	 (TP = 316, FP = 11) 

 for conf_thresh = 0.25, precision = 0.94, recall = 0.97, F1-score = 0.96 
 for conf_thresh = 0.25, TP = 1788, FP = 110, FN = 54, average IoU = 82.19 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 0.986163, or 98.62 % 
Total Detection Time: 20.000000 Seconds
```

说明：

- 相同的batch和subdivisions参数下，enetb0训练时会消耗更多的显存.

### step11 测试

训练之后，会在backup目录生成权重文件：

```sh
$ ls backup
yolov3-voc_100.weights ...... yolov3-voc_900.weights

# 执行测试
./darknet detector test cfg/voc.data cfg/yolov3-voc.cfg backup/yolov3-voc_900.weights data/210.jpg
./darknet detector demo cfg/voc.data cfg/yolov3-voc.cfg backup/yolov3-voc_900.weights data/210.jpg
```

#### step11.1 训练指标可视化

- 参考资料：[Darknet评估训练好的网络的性能](https://www.jianshu.com/p/7ae10c8f7d77)
- scripts目录下有相应的脚本
- 训练的时候，记得保存训练日志
- 查看损失的loss，可以使用[脚本](/machine-learning/yolov3-train-loss-show.py)

### step12 转成keras模型

使用`https://github.com/qqwweee/keras-yolo3/`提供的转换程序：

```sh
python3 convert.py ../darknet/cfg/yolov3-voc.cfg \
    ../darknet/backup/yolov3-voc_final.weights model_data/yolov3_helmet.h5

# 输出
Saved Keras model to model_data/yolov3_helmet.h5
Read 61576342 of 61576342.0 from Darknet weights.

python3 convert.py ../alexeyab_darknet/cfg/gf-yolov3-spp.cfg \
    ../alexeyab_darknet/backup-gf-yolov3-spp-0.066425/gf-yolov3-spp_final.weights \
    model_data/gf_yolov3_spp_l066425.h5
```

### step13 使用keras测试

```sh
# 原来的代码有点问题，参数无法生效，需要修改一下才能正常执行
# 图片
python3 yolo_video.py --image --model-path=model_data/yolov3_helmet.h5 \
    --anchors-path=model_data/yolov3_anchors.txt \
    --classes-path=model_data/yolov3_classes.txt 

# 视频
# 如果在服务器运行得注释掉两行代码，还的增加一行代码
# if return_value is False: break
# 输出avi需要修改：video_FourCC = cv2.VideoWriter_fourcc(*'XVID')
# 如果是服务器还得把 cv2.imshow("result", result) 这附件的两行注释掉
python3 yolo_video.py --model-path=model_data/yolov3_helmet.h5 \
    --input=../工作服安全帽.mp4 --output=out.avi \
    --anchors-path=model_data/yolov3_anchors.txt \
    --classes-path=model_data/yolov3_classes.txt 

# 检测图片
python3 yolo_video.py --image \
    --model-path=model_data/gf_yolov3_spp_l066425.h5 \
    --classes-path=../alexeyab_darknet/data/gf.voc.names
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

### 项目相关的数据和配置等，都应该放到同一个目录下

```sh
# 项目根目录：projects/windows-video-monitor/
# 标注的数据
Annotations
ImageSets
JPEGImages
# 生成的数据文件
train.txt
val.txt
labels
# 生成训练文件脚本
voc_label.py
# 配置文件
voc.data
voc.names
# 配置文件
yolov3.cfg
yolov3-spp.cfg
yolov3-tiny.cfg
# 模型保存目录
backup
```

### 默认每1000步保存一个文件

可以修改`src/detector.c`这个文件来改变该值：

```c
// 大概在300行左右的位置
        if (i >= (iter_save + 1000) || i % 1000 == 0) {
            iter_save = i;
#ifdef GPU
            if (ngpus != 1) sync_nets(nets, ngpus, 0);
#endif
            char buff[256];
            sprintf(buff, "%s/%s_%d.weights", backup_directory, base, i);
            save_weights(net, buff);
        }
```

### 提示找不到so文件：libcudart.so.10.0

这是原来make的时候，使用的是cuda10.0，后来更新了cuda版本，重新make即可。

### Error: l.outputs == params.inputs

- cfg配置文件中classes和filter关系是否对应


### 超出内存Out of memory

主要调节配置文件subdivisions和batch参数，Makfile中的cudnn也可以关闭。例如:

- 将subdivisions参数值调大。

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

### 使用darknet来预测

```c
// vim src/darknet.c
// test_detector这个函数在调用时, 第一个参数被固定了
// 导致自己训练的模型无法使用该命令
    } else if (0 == strcmp(argv[1], "detect")){
        float thresh = find_float_arg(argc, argv, "-thresh", .24);
        int ext_output = find_arg(argc, argv, "-ext_output");
        //char *filename = (argc > 4) ? argv[4]: 0;
        //test_detector("cfg/coco.data", argv[2], argv[3], filename, thresh, 0.5, 0, ext_output, 0, NULL, 0);
        char *filename = (argc > 5) ? argv[5]: 0;
        test_detector(argv[2], argv[3], argv[4], filename, thresh, 0.5, 0, ext_output, 0, NULL, 0);
    } else if (0 == strcmp(argv[1], "cifar")){
```

这样就可以使用下面的命令了:

```sh
./darknet detect cfg/gf.voc.data cfg/yolov3-tiny-gf.cfg backup/yolov3-tiny-gf_final.weights idcard-test.jpg
```

## 附录

- https://karbo.online/dl/yolo_starter/


