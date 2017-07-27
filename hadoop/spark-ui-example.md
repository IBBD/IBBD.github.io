# Spark UI界面数据解读
spark任务以以下方式执行：

```sh
yarn_run() {
    spark-submit \
        --master yarn \
        --deploy-mode client \
        --driver-memory 6g \
        --num-executors 10 \
        --executor-cores 4 \
        --executor-memory 10G \
        --conf "spark.yarn.executor.memoryOverhead=2g" \
        --conf "spark.locality.wait.process=100" \
        --conf "spark.locality.wait.node=1000" \
        road_etl.py "$source_filename" "$target_path"
}

#local_run
yarn_run
```

## 重要名词

- Job: 作业
- Stage: 步骤
- Task: 任务

## 1. 作业界面
任务成功提交之后，查看Job信息：http://hd-s1.ibbd.net:8088/proxy/application_1500521063803_0045/jobs/

### 1.1 基础信息

- User: root
- Total Uptime: 10.0 h
- Scheduling Mode: FIFO  （Job调度方式）
- Active Jobs: 1

### 1.2 作业列表

Id  | Description                                       | Submitted           | Duration | Stages | Tasks
--- | ------                                            | --------            | -------  | ----   | -----
0   | saveAsTextFile at NativeMethodAccessorImpl.java:0 | 2017/07/27 01:34:41 | 8.3 h    | 1/2    | 8644/10816


这个表格的信息包括：job链接（在这里可以kill掉整个job），成功提交时间，已经执行时间，阶段进度（1/2表示有两个阶段，其中一个已经完成），任务进度（完成数/总数）

从这里，梳理一下几个重要的概念：

- Application：我们提交的程序就是一个app
- Job: 一个app会分成多个Job
- Stage: 一个Job分为多个Stage执行
- Task: 一个Stage分为多个Task

总的划分关系：`App > Job > Stage > Task`

## 2. Stages界面
在Job列表，点击Job的链接，即进入Stages列表界面，会分成已经完成列表和正在执行的列表。

Id | Description                                       | Submitted           | Duration | Tasks     | Input | Output | Shuffle Read | Shuffle Write
-- | -------                                           | -------             | -----    | ---       | ---   | ---    | ---          | -----
1  | saveAsTextFile at NativeMethodAccessorImpl.java:0 | 2017/07/27 05:50:04 | 5.0 h    | 4018/5408 |       | 5.7 GB | 341.1 GB     |

输入输出说明：

- Input:
- Output:

Shuffle读写说明：

- Read:
- Write:

### 2.1 Shuffle
在MapReduce框架中，shuffle是连接Map和Reduce之间的桥梁，Map的输出要用到Reduce中必须经过shuffle这个环节，shuffle的性能高低直接影响了整个程序的性能和吞吐量。

Shuffle是MapReduce框架中的一个特定的phase，介于Map phase和Reduce phase之间，当Map的输出结果要被Reduce使用时，输出结果需要按key哈希，并且分发到每一个Reducer上去，这个过程就是shuffle。由于shuffle涉及到了磁盘的读写和网络的传输，因此shuffle性能的高低直接影响到了整个程序的运行效率。

下面这幅图清晰地描述了MapReduce算法的整个流程，其中shuffle phase是介于Map phase和Reduce phase之间。

![Shuffle](/_img/spark/mapreduce-process-shuffle.jpg)

相关文章：http://jerryshao.me/architecture/2014/01/04/spark-shuffle-detail-investigation/

#### 2.1.1 什么决定需要Shuffle
每个stage包含不需要Shuffle的RDD。

RDD 包含固定数目的 partition， 每个 partiton 包含若干的 record。对于那些通过narrow tansformation（比如 map 和 filter）返回的 RDD，一个 partition 中的 record 只需要从父 RDD 对应的partition 中的 record 计算得到。每个对象只依赖于父 RDD 的一个对象。有些操作（比如 coalesce）可能导致一个 task处理多个输入 partition ，但是这种 transformation 仍然被认为是 narrow 的，因为用于计算的多个输入 record 始终是来自有限个数的 partition。

然而 Spark 也支持需要 wide 依赖的 transformation，比如 groupByKey，reduceByKey。在这种依赖中，计算得到一个 partition 中的数据需要从父 RDD 中的多个 partition 中读取数据。所有拥有相同 key 的元组最终会被聚合到同一个partition 中，被同一个 stage 处理。为了完成这种操作， Spark需要对数据进行 shuffle，意味着数据需要在集群内传递，最终生成由新的 partition 集合组成的新的 stage。

简单说：`一个partition的数据的处理结果只会出现在一个partition中时，就不需要shuffle`，也可以理解为`一对一`或者`多对一`的操作都不需要shuffle，而`一对多`或者`多对多`都是可能需要shuffle的（这里不一定是必须的），例如`groupByKey`操作，本来在同一个partition的记录就有可能被拆分到不同的partition上。

下面是一个比较复杂的RDD图：

![RDD](/_img/spark/shuffle01.png)

划分Stage的边界如下：

![Shuffle](/_img/spark/shuffle02.png)

**运行到每个 stage 的边界时，数据在父 stage 中按照 task 写到磁盘上，而在子 stage 中通过网络按照 task 去读取数据。**这些操作会导致很重的网络以及磁盘的I/O，所以 stage 的边界是非常占资源的，在编写 Spark 程序的时候需要尽量避免的。父 stage 中 partition 个数与子 stage 的 partition 个数可能不同，所以那些产生 stage 边界的 transformation 常常需要接受一个 numPartition 的参数来觉得子 stage 中的数据将被切分为多少个 partition。

正如在调试 MapReduce 是选择 reducor 的个数是一项非常重要的参数，调整在 stage 边届时的 partition 个数经常可以很大程度上影响程序的执行效率。

#### 2.1.2 Shuffle的生成逻辑
考虑如下的代码：

```python
rdd1 = someRdd.reduceByKey(...)
rdd2 = someOtherRdd.reduceByKey(...)
rdd3 = rdd1.join(rdd2)
```

因为没有 partitioner 传递给 reduceByKey，所以系统使用默认的 partitioner，所以 rdd1 和 rdd2 都会使用 hash 进行分 partition。代码中的两个 reduceByKey 会发生两次 shuffle 。如果 RDD 包含相同个数的 partition， join 的时候将不会发生额外的 shuffle。因为这里的 RDD 使用相同的 hash 方式进行 partition，所以全部 RDD 中同一个 partition 中的 key的集合都是相同的。因此，rdd3中一个 partiton 的输出只依赖rdd2和rdd1的同一个对应的 partition，所以第三次shuffle 是不必要的。

举个例子说，当 someRdd 有4个 partition， someOtherRdd 有两个 partition，两个 reduceByKey 都使用3个partiton，所有的 task 会按照如下的方式执行：

![Shuffle](/_img/spark/shuffle03.png)

改变一下：

![Shuffle](/_img/spark/shuffle04.png)



### 2.2 DAG可视化

![DAG可视化](/_img/spark/spark-job-stages.jpg)

可视化的蓝色阴影框对应到Spark操作，即用户调用的代码。每个框中的点代表对应操作下创建的RDDs。操作本身由每个流入的stages划分。

通过可视化我们可以发现很多有价值的地方。首先，根据显示我们可以看出Spark对流水线操作的优化——它们不会被分割。尤其是，从HDF S读取输入分区后，每个executor随后即对相同任务上的partion做flatMap和map，从而避免与下一个stage产生关联。

其次，RDDs在第一个stage中会进行缓存（用绿色突出表示），从而避免对HDFS（磁盘）相关读取工作。在这里，通过缓存和最小化文件读取可以获得更高的性能。

在每个Stage里可以查看每个Stage的DAG图：

![DAG可视化](/_img/spark/spark-stage0-dag.jpg)
![DAG可视化](/_img/spark/spark-stage1-dag.jpg)

### 2.3 每个Stage的详情
DAG图在上面已经有，这里只说明表格上的指标, 主要有三个表格：

#### 2.3.1 已完成任务的描述性指标

- Duration
- GC Time
- Input Size/Records
- Shuffle Write Size/Records
- Shuffle spill(memory)
- Shuffle spill(disk)

#### 2.3.2 执行器的Aggregated指标

- Task Time   
- Total Tasks 
- Failed Tasks    
- Killed Tasks    
- Succeeded Tasks 
- Input Size / Records    
- Shuffle Write Size / Records    
- Shuffle Spill (Memory)  
- Shuffle Spill (Disk)

#### 2.3.3 每个任务的指标


- Locality Level
- Launch Time
- Duration
- GC Time
- Input Size / Records
- Write Time
- Shuffle Write Size / Records
- Shuffle Spill (Memory)
- Shuffle Spill (Disk)





