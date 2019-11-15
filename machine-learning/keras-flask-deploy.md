# 使用flask部署keras深度学习模型的一个坑

## 背景

Yolo模型代码大概如下

```python
class YOLO(object):
    def __init__(self, **kwargs):
        # 初始化及加载模型

    def predict(self, image):
        # 预测
```

## 最早的方案

最开始就是将模型初始化放到全局上，大概如下：

```python
yolo = YOLO()

@app.route("/predict", methods=["POST"])
def predict():
    yolo.predict(image)
```

可是这样子会报错：RuntimeError: The Session graph is empty.

## 优化方案一

因为flask本身会多个进程，会导致报错，于是改成了下面的形式：

```python
@app.route("/predict", methods=["POST"])
def predict():
    yolo = YOLO()
    yolo.predict(image)
```

这样确实不会报错了，但是每次请求都会重新对模型进行初始化，这个步骤很耗时间，也不好判断是否会内存泄露。

## 优化方案二
于是还是回到原来的设想，模型初始化必须放在全局进行，剩下的就是解决问题。这问题肯定不止我一个人遇到，继续找原因。综合来看，报错`RuntimeError: The Session graph is empty.`，是因为tensorflow默认的是动态图，而flask会被多个进程使用，如果放在全局的话，就会出现empty的情况。解决途径如下：

```python
yolo = YOLO()
graph = tf.get_default_graph()

class YOLO(object):
    def __init__(self, **kwargs):
        # 初始化及加载模型

    def predict(self, image):
        # 预测
        with graph.as_default():
            sess.run(...)

@app.route("/predict", methods=["POST"])
def predict():
    yolo.predict(image)
```

将计算图固化下来，每次都使用默认的graph。这样，重复初始化的耗时问题就解决了。

## 最终方案
不过实际在本地测试的时候，还会遇到显存占用的问题，keras默认在显存都占用了，导致其他需要显存的应用总是跑不起来。
解决办法就是修改显存的申请方式：

```python
# 在初始化的时候加上：
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
```

至此，整个世界都清净了。
