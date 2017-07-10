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

grouped.flatMap(user_map).head(10)
```


## Step04: 


