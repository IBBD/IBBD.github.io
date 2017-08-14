# Spark 简介

## 背景

Spark 诞生于2009年，加州大学伯克利分校 AMP 实验室一个研究项目。

最初是基于 Hadoop MapReduce 的，发现 Hadoop 在迭代式计算和交互式上低效，引入了内存计算


### 什么是 Hadoop

Hadoop 是分布式计算、存储、管理的生态系统。

### Hadoop 解决了什么问题

1. Hadoop 实现了一个分布式文件系统（Hadoop Distributed File System），简称HDFS，为海量的数据提供了存储。

2. 而 MapReduce 则提供 map 和 reduce 简单的抽象编程模型，用户可以在不了解分布式底层细节的情况下，开发分布式程序。分布式地处理大量的数据集，而把并发、分布式（如机器间通信）和故障恢复等计算细节隐藏起来。

### Hadoop的局限和不足

但是，MapRecue存在以下局限，使用起来比较困难。

1. 抽象层次低，只提供两个操作，Map和Reduce，复杂的计算需要大量的Job完成，Job之间的依赖关系是由开发者自己管理的。

2. 中间结果放在HDFS文件系统中，每步操作都要重复读取和写入磁盘，占用了大量的IO，导致性能受限。

3. 时延高，只适用批量数据处理，对于交互式数据处理，实时数据处理的支持不够

4. 对于迭代式数据处理性能比较差。


## Spark 与 Hadoop 对比

### 更快

Spark 的中间运算输出结果可以保存在内存中，在内存中对数据进行迭代计算下，Spark 比 Hadoop 快100倍。


### 易用性

Spark 提供了80多个高级运算符。相比与MapReduce编程模型，Spark 提供不仅包含传统的map、reduce接口， 还增加了filter、flatMap、groupBy、join、distinct等操作接口，使得编写Spark程序更加灵活方便。

### Spark 生态

Spark 提供了Spark Core、Spark SQL、Spark Streaming、MLib、GraphX 等组件， 提供一个统一的数据处理平台，开发者可以在同一个应用程序中无缝组合使用这些库，大大减少了使用和部署的时间。

![Spark 组件](/_img/spark/spark-parts.jpg)

1. Spark Croe

- 包含任务调度、内存管理、容错机制等基本功能

- 引入了弹性分布式数据集 RDD (Resilient Distributed Dataset)

- 并提供很多 API 来创建和操作 RDD

- 为其它组件提供了底层的服务

2. Spark SQL

- 处理结构化数据的库。兼容 Hive，性能比Hive有了10-100倍的提高

- 引入了 Spark DataFrame API，提供了与 R 和 Python Pandas 类似的接口

- 应用场景：用来做报表统计

3. Spark Streaming

- Spark Streaming 是实时数据流处理组件

- 提供 API 对多种数据源（如Kdfka、Flume、Twitter、Zero和TCP 套接字）进行类似Map、Reduce和Join等复杂操作

- 应用场景：用来做实时统计

4. MLib （Machine Learning Lib）

- MLib 包含通用机器学期功能的包

- 包含分类、聚类、回归等

- 应用场景：机器学习

5. GraphX

- 提供了各种图的操作，和常用图的算法，例如 PageRank

- 应用场景：图计算




