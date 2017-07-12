# 使用PySpark处理实际数据集

数据集的基本情况如下：

```
>>> df = spark.read.csv("/data/jm/result/jm_daoall2_areatags4/000122_0")
>>> df.count()
3321092                                                                         
>>> df.head(1)
[Row(_c0='2017', _c1='4', _c2='17', _c3='9', _c4='811079286356699', _c5='2017-04-17 09:59:45.378', _c6='2017-04-17 09:59:47.688', _c7='江门新体育中心南(从江门大林拉远)F-ZLH-2', _c8='蓬江', _c9='棠下镇', _c10='8-11时', _c11='N', _c12='\\N')]
```

## Step01: 删除多余的列

```
df01 = df.drop('_c0', '_c1', '_c2', '_c3', '_c10')
```

## Step02: 日期格式字段格式化
在原数据中，c5和c6两个字段的格式是`2017-04-17 09:59:47.688`，需要转换成时间戳才好计算。

```python
import time


def formatTime(val):
  time_arr = time.strptime(val.split('.')[0], "%Y-%m-%d %H:%M:%S")
  return int(time.mktime(time_arr))

def formatField(row):
    row = list(row)
    row[1] = formatTime(row[1])
    row[2] = formatTime(row[2])
    if row[7].startswith('\\'):
        row[7] = row[7][1:]
    return row

rdd02 = df01.rdd
rdd02 = rdd02.map(formatField)
rdd02.first()
```

注意：map中函数的参数是tuple，需要先转成list，否则会报错：TypeError: 'Row' object does not support item assignment


## Step03: 按用户ID聚合数据

```python
grouped = rdd02.groupBy(lambda r: r[0])

def user_map(row):
    row = list(row[1])
    data = sorted(row, key=lambda r: r[1])
    l = len(data)
    new_data = []
    continue_cnt = 0
    for i in range(0, l-1):
        if continue_cnt > 0:
            continue_cnt -= 1
            continue
        i_row = row[i]
        for j in range(i+1, l):
            if i_row[5] == row[j][5] and i_row[6] == row[j][6] and i_row[7] == row[j][7]:
                i_row[2] = row[j][2]
                continue_cnt += 1
        new_data.append(i_row)
    return new_data

data = grouped.flatMap(user_map)
```

## Step04: 保存数据

```python
# target_path: 结果的保存目录
# 如果目录不存在则会自动创建，相应的文件已经存在则会报错。
rdd.saveAsTextFile(target_path)
```

## 一个完整的使用spark做数据清洗的程序

```python
# -*- coding: utf-8 -*-
#
# Spark ETL: 道路识别
#
# spark-submit --master local[4] road_etl.py "$source_filename" "$target_path"
#
# Author: alex
# Created Time: 2017年07月11日 星期二 10时07分03秒
import sys
from pyspark import SparkContext

# ******************* 配置 ******************************

# 字段下标定义
uid_index = 0      # 用户ID字段
start_index = 1    # 开始时间字段，整型
end_index = 2      # 结束时间字段，整型
station_index = 3  # 基站字段
town_index = 5     # 镇名字段
road_index = 6     # 道路字段
cross_index = 7    # 路口字段

# 分析结果字段
real_road_index = 8       # 分析后的道路字段：经过道路旁边的基站并不一定就在道路上
cross_status_index = 9   # 路口状态字段：0表示不是经过路口，1表示出，2表示入

# 道路上基站允许的时间差
# 车在道路上行驶，可能会有掉线的可能
time_diff = 10

# 常量定义
jm_load_id = 1   # 道路id定义

# 道路出入口状态常量定义
cross_default = 0  # 路口的默认状态
cross_in = 1       # 道路入口(进入道路)
cross_out = 2      # 道路出口(从道路离开)
cross_stay = 3     # 在路口停留（可能是办事，或者工作，或者回家等）
cross_unknown = 4  # 未知状态

# ******************* 配置 ******************************

def main():
    # 格式化数据
    sc = SparkContext("local", "JM City ETL")
    source = sc.textFile(source_filename)
    mapped_data = source.map(init_map)

    # 按用户ID聚合数据
    grouped_data = mapped_data.groupBy(lambda x: x[uid_index])
    road_data = grouped_data.flatMap(load_map)

    road_data.map(save_map).saveAsTextFile(target_path)
    print("*"*40)


def save_map(row):
    """将数组格式化成csv的格式"""
    return ','.join((str(w) for w in row))


def init_map(line):
    """格式化数据：字段类型等"""
    line = line.split(',')
    line[start_index] = int(line[start_index])
    line[end_index] = int(line[end_index])
    line[road_index] = int(line[road_index]) if line[road_index] != 'N' else 0
    return line

def user_cross_map(data):
    # do somethings...
    return new_data


def user_road_map(data):
    """道路识别
    """
    l = len(data)
    new_data = []
    continue_cnt = 0
    for i in range(0, l-1):
        i_row = data[i]
        if continue_cnt > 0:
            continue_cnt -= 1
            i_row.append(jm_load_id)
            new_data.append(i_row)
            continue

        if i_row[road_index] != jm_load_id:
            # 如果不在jm大道上
            i_row.append(0)
            new_data.append(i_row)
            continue

        # 判断是否在jm大道上
        stations = [i_row[station_index]]
        for j in range(i+1, l):
            if data[j][road_index] == jm_load_id:
                # 如果基站在jm大道上
                continue_cnt += 1
                stations.append(data[j][station_index])
            else:
                break

        rate = float(continue_cnt) / float(len(set(stations)))
        if continue_cnt > 1 and rate < 1.45:  # 连续3个及以上的基站
            i_row.append(jm_load_id)
            new_data.append(i_row)
            continue

        i_row.append(0)
        new_data.append(i_row)
        continue_cnt = 0

    return new_data


def merge_station(data):
    """合并相同的基站
    """
    l = len(data)
    new_data = []
    continue_cnt = 0
    for i in range(0, l-1):
        if continue_cnt > 0:
            continue_cnt -= 1
            continue

        # 判断是否在jm大道上
        i_row = data[i]
        for j in range(i+1, l):
            if i_row[station_index] == data[j][station_index]:
                # 合并相同的基站
                i_row[end_index] = data[j][end_index]
                continue_cnt += 1
            else:
                break

        new_data.append(i_row)

    return new_data


def load_map(row):
    """根据用户ID进行聚合数据
    实现的目标：
    1. 道路模式识别: 快速经过路上的若干个基站
    2. 路口模式识别: """
    row = list(row[1])  # 二维数组
    data = sorted(row, key=lambda r: r[start_index])  # 按开始时间排序

    # 合并相同基站的数据
    data = merge_station(data)

    # 道路模式识别
    data = user_road_map(data)

    # 路口模式识别
    data = user_cross_map(data)

    return data


# 入口程序
if len(sys.argv) == 3:
    source_filename = sys.argv[1]   # 需要加载的csv文件
    target_path = sys.argv[2]       # 结果保存目录
    main()
else:
    print("+"*40)
    print("参数错误！")
```

