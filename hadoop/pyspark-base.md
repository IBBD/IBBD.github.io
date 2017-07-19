# pyspark基础入门
基于version 2.1.0版本下。

## 配置与启动

- pyspark默认使用python2, 如果需要修改为python3, 则`vim ~/.bash_profile`，增加一行`export PYSPARK_PYTHON=python3`，注意需要重启shell。
- 使用ipython作为默认的shell：`export PYSPARK_DRIVER_PYTHON=ipython`
- 启动：`app/spark/bin/pyspark`

## spark核心概念

### 核心理念

![spark task](/_img/spark-base.png)

### RDD(Resilient Distributed Dataset) 弹性分布数据集介绍 
弹性分布式数据集（基于Matei的研究论文）或RDD是Spark框架中的核心概念。可以将RDD视作数据库中的一张表。其中可以保存任何类型的数据。Spark将数据存储在不同分区上的RDD之中。 

RDD可以帮助重新安排计算并优化数据处理过程。 

此外，它还具有容错性，因为RDD知道如何重新创建和重新计算数据集。 

RDD是不可变的。你可以用变换（Transformation）修改RDD，但是这个变换所返回的是一个全新的RDD，而原有的RDD仍然保持不变。 

RDD支持两种类型的操作：

- `变换（Transformation）`: 变换的返回值是一个新的RDD集合，而不是单个值。调用一个变换方法，不会有任何求值计算，它只获取一个RDD作为参数，然后返回一个新的RDD。变换函数包括：map，filter，flatMap，groupByKey，reduceByKey，aggregateByKey，pipe和coalesce。
- `行动（Action）`: 行动操作计算并返回一个新的值。当在一个RDD对象上调用行动函数时，会在这一时刻计算全部的数据处理查询并返回结果值。行动操作包括：reduce，collect，count，first，take，countByKey以及foreach。

### 共享变量（Shared varialbes） 

- 广播变量（Broadcast variables）
- 累加器（Accumulators）

### Master/Worker/Driver/Executor 

- Master：1. 接受Worker的注册请求，统筹记录所有Worker的CPU、Memory等资源，并跟踪Worker结点的活动状态；2. 接受Driver中App的注册请求(这个请求由Driver端的Client发出)，为App在Worker上分配CPU、Memory资源，生成后台Executor进程；之后跟踪Executor和App的活动状态。
- Worker：负责接收Master的指示，为App创建Executor进程。Worker在Master和Executor之间起着桥梁作用，实际不会参与计算工作。
- Driver：负责用户侧逻辑处理。
- Executor：负责计算，接受并执行由App划分的Task任务，并将结果缓存在本地内存或磁盘。

## 第一个demo：词频统计
原理图如下：

![spark单词统计原理图](/_img/spark-base-wordcount.png)

数据文件：

```
# cat hello-spark.log 
This is spark time
Learn spark
```

代码如下：

```python
conf = SparkConf().setMaster("local").setAppName("My App")
sc = SparkContext(conf = conf)

text = sc.textFile("./hello-spark.log")
text_map = text.flatMap(lambda line: line.split()).map(lambda word: (word, 1))
wordcount = text_map.reduceByKey(lambda x, y: x + y)
```

配置参数说明:

- 集群 URL: 告诉 Spark 如何连接到集群上。在这几个例子中我们使用的是 local ,这个特殊值可以让 Spark 运行在单机单线程上而无需连接到集群。
- 应用名: 在例子中我们使用的是 My App 。当连接到一个集群时,这个值可以帮助你在集群管理器的用户界面中找到你的应用。

注意：这里会报错`Input path does not exist: hdfs://ibbd/user/hadoop/hello-spark.log`

默认会直接到hdfs中查找，但是我们的文件还在外部的文件系统中。应该改为如下：

```python
text = sc.textFile("file:/home/hadoop/hello-spark.log")
text_map = text.flatMap(lambda line: line.split()).map(lambda word: (word, 1))

# 这行可以引入：from operator import add
wordcount = text_map.reduceByKey(lambda x, y: x + y)

# 显示最后的结果
wordcount.collect()
# 输出：[('Learn', 1), ('is', 1), ('spark', 2), ('This', 1), ('time', 1)]
```

上面的思路，简单讲就是：Map =》Reduce。而上面又用了两个map函数，注意其不同：

```
>>> help(text.flatMap)
flatMap(f, preservesPartitioning=False) method of pyspark.rdd.RDD instance
    Return a new RDD by first applying a function to all elements of this
    RDD, and then flattening the results.
    
    >>> rdd = sc.parallelize([2, 3, 4])
    >>> sorted(rdd.flatMap(lambda x: range(1, x)).collect())
    [1, 1, 1, 2, 2, 3]
    >>> sorted(rdd.flatMap(lambda x: [(x, x), (x, x)]).collect())
    [(2, 2), (2, 2), (3, 3), (3, 3), (4, 4), (4, 4)]

>>> help(text.map)
map(f, preservesPartitioning=False) method of pyspark.rdd.RDD instance
    Return a new RDD by applying a function to each element of this RDD.
    
    >>> rdd = sc.parallelize(["b", "a", "c"])
    >>> sorted(rdd.map(lambda x: (x, 1)).collect())
    [('a', 1), ('b', 1), ('c', 1)]
```

简单说，就是：

- flatMap：将元素扩充，所以为flat
- map：将列表中的每个元素按照一定的规则映射为另一个元素，前后的列表可以进行一一对应。

### 将词频统计结果可视化
上面的demo已经统计好了词频，但是单看数据很乏味，需要将结果进行可视化。

```python
import matplotlib.pyplot as plt

# 这是统计好的数据
data = [('Learn', 1), ('is', 1), ('spark', 2), ('This', 1), ('time', 1)]

plt.xlabel(u"词频")
plt.ylabel(u"单词")
plt.title(u"词频统计")

x = [i[0] for i in data]
y = [i[1] for i in data]
index = [i for i in range(len(data))]

plt.xticks(index, x)
plt.bar(left=index, height=y, align="center")
plt.show()
```

### 过滤特殊单词
例如词频统计时，需要过滤掉一些如is, am, are之类的高频词。实现也很简单，就是使用`filter`函数，如下：

```python
text_map = text.flatMap(lambda line: line.split())
    .filter(lambda word: word not in ["is","are", "am"])
    .map(lambda word: (word, 1))
```

## 一个实际的例子


## 扩展

- API：http://spark.apache.org/docs/latest/api/python/pyspark.html
- groupByKey,reduceByKey,sortByKey算子：http://www.cnblogs.com/LgyBean/p/6262481.html
- Logistic回归及Binary分类（二分问题）结果评估: http://lib.csdn.net/article/machinelearning/40643
- Spark数据ETL: http://blog.csdn.net/u011204847/article/details/51247306
- PySpark处理数据并图表分析: http://blog.csdn.net/u011204847/article/details/51224383
