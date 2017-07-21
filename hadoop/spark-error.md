# Spark使用问题集合

- 内存溢出问题
- 未正常关闭sc
- Too many open files


## 内存溢出问题

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





