# Yolov4模型训练

- 训练命令：`./darknet detector train projects/windows-video-monitor/voc.data projects/windows-video-monitor/yolov4.cfg yolov4.conv.137 -dont_show -gpus 0,1`
- 配置过程和yolov3类似
- 使用以下配置，在11G的2080TI上，只能使用416*416：

```sh
# vim Makefile
GPU=1
CUDNN=1
CUDNN_HALF=1
OPENCV=1

# vim yolov4.cfg
batch=32
subdivisions=8
# Training
height=416
width=416
```

这样勉强够用。


## 踩坑记录

## Tensor Cores are disabled until the first 600 iterations are reached.

这个不是错误信息，错误信息还在后面

