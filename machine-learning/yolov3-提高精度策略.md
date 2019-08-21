# Yolov3训练：提高精度策略
see: https://github.com/AlexeyAB/darknet#how-to-improve-object-detection

- 在.cfg文件中设置random=1，它会通过对不同分辨率的图片进行训练以提高精度
- 使用高分辨率的图像输入。在.cfg文件中设置height和width值。但是你无需重头训练，只需使用回416x416分辨率的权重数据就好了。
- 检查数据集标注是否正确符合规范
- 检查训练数据集数据量是否过少
- 迭代次数推荐不低于2000 * classes
- 你的训练样本希望包含没有目标物体的图像，即该图像中没有出现目标物体，标签文件是空的文本。
- 对于要检测的每个对象，训练数据集中必须至少有一个类似的对象，其大致相同：形状、对象侧面、相对大小、旋转角度、倾斜、照明。
- 如果图片里有很多数量的目标物体，那么在.cfg文件中最后的[yolo]层或[region]层中添加参数max=200，这也可以设定成更高的值。
- 如果目标物体很小（缩放成416x416尺寸后小于16x16），那么将第720行设置为layers = -1, 11，将第717行设置为stride=4
- 如果目标物体有些很大有些又很小，那么请使用修改后的模型：
    - Full-model: 5 yolo layers
    - Tiny-model: 3 yolo layers
    - Spatial-full-model: 3 yolo layers
- 如果你的模型需要区分左右手性，例如区分左手和右手、左转和右转，那么需要关闭翻转数据增强选项，即添加flip=0到这里
- 如果想要模型具有尺度的鲁棒性，则必须训练样本中包含多尺度的照片。这是因为YOLO不具有尺度变化的适应性。
- 要想加速模型的训练（但会降低预测精度）应该使用Fine-Tuning而不是Transfer-Learning，需要在这里设置参数stopbackward=1，然后运行./darknet partial cfg/yolov3.cfg yolov3.weights yolov3.conv.81 81，这会创建文件yolov3.conv.81，然后使用该文件yolov3.conv.81训练。
- 复杂物体应该使用复杂的神经网络来训练
- 你可以修改anchors的大小。略。
- 修改配置文件的参数，如height=608 and width=608, 修改为height=832 and width=832（值需要为32的倍数），增大height和width对检测小目标更有利。

