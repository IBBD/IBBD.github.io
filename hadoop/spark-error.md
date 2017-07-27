# Spark使用问题集合

- 内存溢出问题: OOM
- 未正常关闭sc
- Too many open files
- Container killed by YARN for exceeding memory limits

## 内存溢出问题: OOM
内存不够，数据太多就会抛出OOM的Exception，主要有Driver OOm和Executor OOM两种

- Driver OOM: 一般是使用了collect操作将所有executor的数据聚合到dirver端导致，尽量不要使用collect操作即可
- Executor OOM: 可以按下面的内存优化的方法增加code使用内存空间

```
17/07/19 16:12:30 ERROR Executor: Exception in task 1310.0 in stage 0.0 (TID 1310)
java.lang.OutOfMemoryError: Unable to acquire 138448274 bytes of memory, got 47927922
	at org.apache.spark.memory.MemoryConsumer.allocatePage(MemoryConsumer.java:129)
	at org.apache.spark.shuffle.sort.ShuffleExternalSorter.acquireNewPageIfNecessary(ShuffleExternalSorter.java:359)
	at org.apache.spark.shuffle.sort.ShuffleExternalSorter.insertRecord(ShuffleExternalSorter.java:382)
	at org.apache.spark.shuffle.sort.UnsafeShuffleWriter.insertRecordIntoSorter(UnsafeShuffleWriter.java:246)
	at org.apache.spark.shuffle.sort.UnsafeShuffleWriter.write(UnsafeShuffleWriter.java:167)
	at org.apache.spark.scheduler.ShuffleMapTask.runTask(ShuffleMapTask.scala:96)
	at org.apache.spark.scheduler.ShuffleMapTask.runTask(ShuffleMapTask.scala:53)
	at org.apache.spark.scheduler.Task.run(Task.scala:99)
	at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:322)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1142)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
	at java.lang.Thread.run(Thread.java:745)
```

解决方法：

- 增加executor内存总量，也就是说增加spark.executor.memory 的值
- 增加任务并行度（大任务就被分割成小任务了），可以参考优化并行度的方法

启动时增加了`--driver-memory`参数，如下：

```sh
spark-submit \
    --master local[*] \
    --driver-memory 12g \
    --conf "spark.executor.memory=2g" \
    --conf "spark.executor.cores=100" \
    road_etl.py "$source_filename" "$target_path"
```

## 未正常关闭sc

```
17/07/19 21:28:25 WARN NettyRpcEndpointRef: Error sending message [message = Heartbeat(driver,[Lscala.Tuple2;@8ddb44d,BlockManagerId(driver, 192.168.80.27, 41572, None))] in 1 attempts
org.apache.spark.rpc.RpcTimeoutException: Futures timed out after [10 seconds]. This timeout is controlled by spark.executor.heartbeatInterval

17/07/19 21:37:30 ERROR LiveListenerBus: Listener EventLoggingListener threw an exception
java.io.IOException: All datanodes DatanodeInfoWithStorage[192.168.80.27:50010,DS-4c3c9b2a-86ff-4545-9f3d-a577d3c9e30e,DISK] are bad. Aborting...
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.setupPipelineForAppendOrRecovery(DFSOutputStream.java:1221)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.processDatanodeError(DFSOutputStream.java:993)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.run(DFSOutputStream.java:500)

17/07/19 21:37:35 ERROR TaskSchedulerImpl: Ignoring update with state FINISHED for TID 5163 because its task set is gone (this is likely the result of receiving duplicate task finished status updates) or its executor has been marked as failed.

17/07/19 21:37:39 INFO BlockManagerInfo: Added broadcast_1_piece0 in memory on 192.168.80.27:41572 (size: 7.0 KB, free: 6.2 GB)
Traceback (most recent call last):
  File "/var/www/spark-etl/jm-city/road_etl.py", line 354, in <module>
    main()
  File "/var/www/spark-etl/jm-city/road_etl.py", line 78, in main
    road_data.map(save_map).saveAsTextFile(target_path)
  File "/usr/hdp/current/spark2-client/python/lib/pyspark.zip/pyspark/rdd.py", line 1552, in saveAsTextFile
  File "/usr/hdp/current/spark2-client/python/lib/py4j-0.10.4-src.zip/py4j/java_gateway.py", line 1133, in __call__
  File "/usr/hdp/current/spark2-client/python/lib/py4j-0.10.4-src.zip/py4j/protocol.py", line 319, in get_return_value
py4j.protocol.Py4JJavaError: An error occurred while calling o57.saveAsTextFile.
: org.apache.spark.SparkException: Job aborted due to stage failure: Task 5164 in stage 0.0 failed 1 times, most recent failure: Lost task 5164.0 in stage 0.0 (TID 5164, localhost, executor driver): ExecutorLostFailure (executor driver exited caused by one of the running tasks) Reason: Executor heartbeat timed out after 190006 ms
```

这种情况出现的原因是由于代码当中对于SparkContext并没有关闭资源所导致的。

正确的做法：在代码的末尾加上：sc.stop()即可。

## Too many open files
执行该命令`res.groupby('_c0').count().show()`时，报错如下：

```
17/07/20 11:41:43 ERROR BypassMergeSortShuffleWriter: Error while deleting file /tmp/blockmgr-5d18893e-84e8-4753-b4e9-1bf335560022/1d/temp_shuffle_5aae96fd-b68e-4c6b-bb5d-89a78b9887a8
17/07/20 11:41:43 ERROR DiskBlockObjectWriter: Uncaught exception while reverting partial writes to file /tmp/blockmgr-5d18893e-84e8-4753-b4e9-1bf335560022/0c/temp_shuffle_724d8731-aa4c-49a7-afda-7fd19498d546
java.io.FileNotFoundException: /tmp/blockmgr-5d18893e-84e8-4753-b4e9-1bf335560022/0c/temp_shuffle_724d8731-aa4c-49a7-afda-7fd19498d546 (Too many open files)

Py4JJavaError: An error occurred while calling o47.showString.
: org.apache.spark.SparkException: Job aborted due to stage failure: Task 67 in stage 4.0 failed 1 times, most recent failure: Lost task 67.0 in stage 4.0 (TID 10887, localhost, executor driver): java.io.FileNotFoundException: /tmp/blockmgr-5d18893e-84e8-4753-b4e9-1bf335560022/01/temp_shuffle_511a8f77-46e8-405a-96d6-ffea2f23ac98 (Too many open files)

17/07/20 11:41:43 ERROR Executor: Exception in task 66.0 in stage 4.0 (TID 10886)
java.io.FileNotFoundException: /tmp/blockmgr-5d18893e-84e8-4753-b4e9-1bf335560022/27/temp_shuf)

17/07/20 12:00:39 ERROR Executor: Exception in task 6.0 in stage 5.0 (TID 10903)
java.io.IOException: Cannot run program "python3": error=24, Too many open files
```

这是由于程序打开的文件句柄数超过了 Linux 系统的限制

修复上述错误的建议：

- 使用命令 ulimit -a 查看限制打开文件数据的设置。
- 在 spark-env.sh 上设置一个较大的文件打开限制，像这样：ulimit -n 10240 （貌似不需要设置也可以有效）
- 在 /etc/security/limits.conf 设置一个较大的文件打开限制，像这样：

```
* soft  nofile  10240
* hard  nofile  10240
* soft  nproc   10240
* hard  nproc   10240
```

注意：

- 注意前面的星号
- 使用设置 /etc/security/limits.conf 改变打开文件限制时需要退出登录然后重新登录才有效。
- 在处理文件时，不应该生成太多的文件

详见：http://www.cnblogs.com/ibook360/archive/2012/05/11/2495405.html

## Yarn集群方式运行的问题
错误信息如下：

```
17/07/21 20:54:22 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
17/07/21 20:54:28 WARN DomainSocketFactory: The short-circuit local reads feature cannot be used because libhadoop cannot be loaded.
17/07/21 20:54:31 INFO Client: Verifying our application has not requested more than the maximum memory capability of the cluster (12288 MB per container)
Exception in thread "main" java.lang.IllegalArgumentException: Required AM memory (12288+1228 MB) is above the max threshold (12288 MB) of this cluster! Please increase the value of 'yarn.scheduler.maximum-allocation-mb'.
```

先看这个：`Required AM memory (12288+1228 MB) is above the max threshold (12288 MB) of this cluster!`，这个是因为内存使用超过了阀值。将`--driver-memory 12g`修改为`--driver-memory 10g`即可：

```sh
yarn_run() {
    spark-submit \
        --master yarn \
        --deploy-mode cluster \
        --driver-memory 10g \
        --conf "spark.executor.memory=512m" \
        --conf "spark.executor.cores=100" \
        road_etl.py "$source_filename" "$target_path"
}

yarn_run
```

重新运行，还是报错如下：

```
17/07/21 21:34:58 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
17/07/21 21:35:03 WARN DomainSocketFactory: The short-circuit local reads feature cannot be used because libhadoop cannot be loaded.
```

在UI上查看应用的运行情况，YarnApplicationState的值是：`ACCEPTED: waiting for AM container to be allocated, launched and register with RM.`，而Log Aggregation Status的值是：`NOT_START`, Application Node Label expression的值是`<Not set>`

将`--deploy-mode`的值修改为`client`之后，没有上面的错误，不过出现新的错误：

```
17/07/21 22:17:02 ERROR YarnClientSchedulerBackend: Yarn application has already exited with state FINISHED!
17/07/21 22:17:02 ERROR SparkContext: Error initializing SparkContext.

	 diagnostics: Uncaught exception: org.apache.hadoop.yarn.exceptions.InvalidResourceRequestException: Invalid resource request, requested virtual cores < 0, or requested virtual cores > max configured, requestedVirtualCores=100, maxVirtualCores=6

/var/www/spark-etl/jm-city/road_etl.py in main()
     65     # 格式化数据
     66     conf = SparkConf().setAppName('JM City ETL')
---> 67     sc = SparkContext(conf=conf)
     68     source = sc.textFile(source_filename)
     69     mapped_data = source.map(init_map)

Py4JJavaError: An error occurred while calling None.org.apache.spark.api.java.JavaSparkContext.
: java.lang.IllegalStateException: Spark context stopped while waiting for backend

17/07/21 22:17:02 ERROR Utils: Uncaught exception in thread Yarn application state monitor
org.apache.spark.SparkException: Exception thrown in awaitResult
```

但是这些代码在local的方式运行时是正常的。修改为如下就ok了：

```sh
# 注释掉下面的一个参数设置
# --conf "spark.executor.cores=100" \
yarn_run() {
    spark-submit \
        --master yarn \
        --deploy-mode client \
        --driver-memory 10g \
        --conf "spark.executor.memory=512m" \
        road_etl.py "$source_filename" "$target_path"
}
```

报错如下：

```
Caused by: java.io.IOException: Cannot run program "python3": error=2, 没有那个文件或目录
```

在所有节点上安装python3.

### Lost task

```
17/07/21 23:32:46 WARN TaskSetManager: Lost task 1.0 in stage 0.0 (TID 1, hd-s1.ibbd.net, executor 1): org.apache.spark.api.python.PythonException: Traceback (most recent call last):

raise Exception("Randomness of hash of string should be disabled via PYTHONHASHSEED")
Exception: Randomness of hash of string should be disabled via PYTHONHASHSEED
```

在`spark2-defaults.conf`中配置`spark.executorEnv.PYTHONHASHSEED=0`，即可。

## Container killed by YARN for exceeding memory limits

```
17/07/25 15:31:01 INFO ShuffleMapStage: ShuffleMapStage 0 is now unavailable on executor 1 (657/5408, false)
17/07/25 15:31:01 WARN YarnSchedulerBackend$YarnSchedulerEndpoint: Container killed by YARN for exceeding memory limits. 1.4 GB of 1 GB physical memory used. Consider boosting spark.yarn.executor.memoryOverhead.
17/07/25 15:31:01 ERROR YarnScheduler: Lost executor 1 on hd-master.ibbd.net: Container killed by YARN for exceeding memory limits. 1.4 GB of 1 GB physical memory used. Consider boosting spark.yarn.executor.memoryOverhead.
17/07/25 15:31:01 INFO DAGScheduler: Resubmitted ShuffleMapTask(0, 137), so marking it as still
```

当executor的内存使用大于executor-memory与executor.memoryOverhead的加和时，Yarn会干掉这些executor，将配置变量`spark.yarn.executor.memoryOverhead`的值加大。之后错误变成如下：

```
17/07/25 15:54:36 INFO Client: Verifying our application has not requested more than the maximum memory capability of the cluster (12288 MB per container)
```

## Lost executor
在yarn的cluster模式运行时，有时任务就会报错，在ui界面上会提示`CANNOT FIND ADDRESS`（出现这样的问题，所有任务好像就全部重启了，这非常耗费时间），但是这是的log查起来并不方便，所以最好使用client模式运行，使用`nohup`运行即可，这样日志都会在`nohup.out`中，有很多的工具可以方便地查看了。查看日志如下：

```
17/07/26 19:43:48 INFO YarnSchedulerBackend$YarnDriverEndpoint: Disabling executor 2.
17/07/26 19:43:48 INFO DAGScheduler: Executor lost: 2 (epoch 0)
17/07/26 19:43:48 INFO BlockManagerMasterEndpoint: Trying to remove executor 2 from BlockManagerMaster.
17/07/26 19:43:48 INFO BlockManagerMasterEndpoint: Removing block manager BlockManagerId(2, hd-master.ibbd.net, 37716, None)
17/07/26 19:43:48 INFO BlockManagerMaster: Removed 2 successfully in removeExecutor
17/07/26 19:43:48 INFO DAGScheduler: Shuffle files lost for executor: 2 (epoch 0)
17/07/26 19:43:48 INFO ShuffleMapStage: ShuffleMapStage 0 is now unavailable on executor 2 (1288/5408, false)
17/07/26 19:43:49 WARN YarnSchedulerBackend$YarnSchedulerEndpoint: Container killed by YARN for exceeding memory limits. 9.2 GB of 9 GB physical memory used. Consider boosting spark.yarn.executor.memoryOverhead.
17/07/26 19:43:49 ERROR YarnScheduler: Lost executor 2 on hd-master.ibbd.net: Container killed by YARN for exceeding memory limits. 9.2 GB of 9 GB physical memory used. Consider boosting spark.yarn.executor.memoryOverhead.
17/07/26 19:43:49 INFO DAGScheduler: Resubmitted ShuffleMapTask(0, 137), so marking it as still running
17/07/26 19:43:49 INFO DAGScheduler: Resubmitted ShuffleMapTask(0, 2021), so marking it as still running
```

注意这里：`WARN YarnSchedulerBackend$YarnSchedulerEndpoint: Container killed by YARN for exceeding memory limits. 9.2 GB of 9 GB physical memory used. Consider boosting spark.yarn.executor.memoryOverhead.`

又是内存超过了。。。


```
# 执行步骤0.0
17/07/25 16:05:51 INFO TaskSetManager: Starting task 38.0 in stage 0.0 (TID 38, hd-master.ibbd.net, executor 2, partition 38, RACK_LOCAL, 6026 bytes)
17/07/25 16:06:10 INFO TaskSetManager: Finished task 38.0 in stage 0.0 (TID 38) in 18673 ms on hd-master.ibbd.net (executor 2) (39/5408)

# 执行步骤1.0
17/07/26 12:06:41 INFO TaskSetManager: Starting task 3126.0 in stage 1.0 (TID 8534, hd-master.ibbd.net, executor 2, partition 3126, PROCESS_LOCAL, 5768 bytes)
17/07/26 12:06:57 INFO TaskSetManager: Finished task 3126.0 in stage 1.0 (TID 8534) in 15437 ms on hd-master.ibbd.net (executor 2) (3127/5408)
```



