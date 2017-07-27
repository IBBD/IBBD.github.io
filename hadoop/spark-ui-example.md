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





