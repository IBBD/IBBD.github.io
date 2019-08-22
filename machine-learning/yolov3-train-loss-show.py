# -*- coding: utf-8 -*-
#
# yolov3训练误差可视化
# python3 machine-learning/yolov3-train-loss-show.py \
#    --filename /tmp/yolov3-spp-loss.txt \
#    --n 200
# Author: alex
# Created Time: 2019年08月22日 星期四 10时32分44秒
import re
import pandas as pd
from matplotlib import pyplot as plt


def read_data(filename):
    #  1: 3983.445801, 3983.445801 avg loss, 0.000000 rate, 8.518392 seconds, 128 images
    pattern = re.compile("^\\s*(\\d+):.*?, (.*?) avg loss")
    lines = None
    with open(filename) as r:
        lines = r.readlines()

    data = [pattern.findall(line)[0] for line in lines]
    data = [(int(row[0]), float(row[1])) for row in data]
    return pd.DataFrame(data, columns=['epoch', 'loss'])


def show(filename, n=1):
    """
    可视化yolov3训练loss
    :param filename 文件名
    :param n 设置若干个epoch的loss合并到一起，在相同区间内取最小值
    """
    df = read_data(filename)
    loss_min = min(df.loss)
    print("Loss最小值：", loss_min)
    print("对应epoch：", list(df.epoch[df.loss == loss_min]))
    epochs = max(df.epoch)
    y = [min(df.loss[(i*n < df.epoch) & (df.epoch <= (i+1)*n)])
         for i in range(epochs//n)]
    plt.title("Yolov3 train loss")
    plt.xlabel("Epoch")
    plt.ylabel("loss")
    plt.plot([(i+1)*n for i in range(epochs//n)], y)
    plt.show()


if __name__ == '__main__':
    import fire
    fire.Fire(show)
