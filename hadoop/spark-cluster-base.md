# Spark集群基础
原文见：https://segmentfault.com/a/1190000003889102

## 概述
Spark 的"集群"不是提供运算服务的，而是一种资源分配的调度器。
执行任务的 Spark 进程作为客户端向"集群"申请资源(运算节点), "集群"分配资源以后，
这个 Spark 进程会分解一些计算工作，并把他们放到这些申请来的资源中运行。

提交给 Spark 执行的工作称做 application(应用)，对应的主程序称作：driver program。
driver program 通过一个叫做 SparkContext 的对象来协调 Spark 集群中不同进程的任务。

具体来说：

- driver program 向"集群"申请到得运算节点称作 worker node；
- 一旦申请到 worker node，driver program 会连接这些 worker node, 并在 worker node 上创建(acquire)执行计算的进程(executor);
- 接下来 driver program 将计算需要的代码和数据发给 executor；
- 最后 SparkContext 将分解出来的 task(任务) 发送给各个 executor 去执行。

过程如下图所示：

![Spark Cluster](/_img/spark-cluster-base.jpg)

这里有一些注意点：

- 每个 application 都获得自己独立的 executor 进程，这个executor进程利用多个线程运行多个 task。这样可以保证不同application的隔离性，无论是调度端(driver program 分解各自的 task)，还是执行端(每个executor只跑来自同一个 application 的 task)。不过这也意味着，不同的 application 之间除非借助外部存储系统(例如数据库)，否则是不可以共享数据的。
- Spark 是不需要知道运行在什么样的 "集群" 上的。Spark 只需要可以创建进程，并且和这些进程通信，无论是运行在什么样的集群上(eg. Mesos/YARN)都可以。
- driver program 必须在整个生命周期中可以从不同的 executor 接受连接。因此，driver program对于 executor 来说，
- 必须是网路可及的。
- 因为由driver program分解 task，它必须和 worker 节点很接近，最好在同一个局域网。
- 如果你不能做到这一点(例如从远程提交 application)，最好开一个 RPC，利用靠近 Spark 集群的机器来运行 driver program

## Spark 集群的类型
实现集群的程序称为：集群管理器。目前有三种集群管理器：

- Standalone - 这个集群管理器打包在 spark 的程序里，是最简单的集群管理器。
- Apache Mesos - 一个非常成熟的分布式操作系统，可以用来运行除 Spark 以外的很多系统。
- Hadoop YARN - Hadoop 的 资源管理器。

## 术语表

术语            | 解释
-------         | ------
Application     | 在 Spark 上运行的工作， 由 driver program 和 executors 组成
Application jar | 包含 Application 代码的 jar 包。在一些应用场景中，jar 需要包含依赖的库。不过永远不要包含 Hadoop 和 Spark 的库
Driver program  | 运行 Application 的main() 函数的进程，并且 SparkContext 对象在此进程中创建
Cluster manager | (集群管理器)实现集群的资源调度分配的外部程序
Deploy mode     | 用于区分 driver program 进程在哪里运行。cluster 模式下，driver 在集群中的节点上运行。 client 模式下，driver 在集群以外的地方运行
Worker node     | 集群中运行程序的节点
Executor        | 在 worker node 中为 各 Application 创建的进程。它会执行 Application 相关的 task，将它们的数据保存在内存中或磁盘上。
Task            | 执行具体计算的单元，会被发送给特定的 executor 执行
Job             | 一个由多个 task 组成的并行计算集，它们生成 Spark 动作(eg. save, collect) 的结果。这个术语会出现在 driver 的日志中
Stage           | 每个 job 会被分解成更小的 task 的集合，这些集合被称作 stage。它们彼此依赖(就像 MapReduce 中的 map 和 reduce 两个 stage)；这个术语会出现在 driver 的日志中

