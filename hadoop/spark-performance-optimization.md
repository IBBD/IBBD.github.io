# Spark性能优化

## 问题背景

3台8核16G内存的Hadoop集群:

- hd-master.ibbd.net: 主节点
- hd-s1.ibbd.net， hd-s2.ibbd.net: 数据节点

需要分析的源csv数据文件大小约为650G，记录数约100亿条。在其中一台数据节点s2，以下面的方式运行：

```sh
yarn_run() {
    spark-submit \
        --master yarn \
        --deploy-mode client \
        --driver-memory 10g \
        --conf "spark.executor.memory=512m" \
        road_etl.py "$source_filename" "$target_path"
}

#local_run
yarn_run
```

服务器负载情况如下：

- 本地数据节点s2的cpu和内存都很低
- 主节点和另一台数据节点s1只有一个cpu用满，其他很低，内存的使用量也很低

输出日志如下：

```
17/07/25 15:25:48 INFO TaskSetManager: Starting task 1198.0 in stage 0.0 (TID 1198, hd-master.ibbd.net, executor 1, partition 1198, RACK_LOCAL, 6026 bytes)
17/07/25 15:25:48 INFO TaskSetManager: Finished task 1196.0 in stage 0.0 (TID 1196) in 5350 ms on hd-master.ibbd.net (executor 1) (1197/5408)
17/07/25 15:25:50 INFO TaskSetManager: Starting task 1199.0 in stage 0.0 (TID 1199, hd-s1.ibbd.net, executor 2, partition 1199, NODE_LOCAL, 6026 bytes)
17/07/25 15:25:50 INFO TaskSetManager: Finished task 1197.0 in stage 0.0 (TID 1197) in 5634 ms on hd-s1.ibbd.net (executor 2) (1198/5408)
17/07/25 15:25:54 INFO TaskSetManager: Starting task 1200.0 in stage 0.0 (TID 1200, hd-master.ibbd.net, executor 1, partition 1200, RACK_LOCAL, 6026 bytes)
17/07/25 15:25:54 INFO TaskSetManager: Finished task 1198.0 in stage 0.0 (TID 1198) in 5807 ms on hd-master.ibbd.net (executor 1) (1199/5408)
17/07/25 15:25:56 INFO TaskSetManager: Starting task 1201.0 in stage 0.0 (TID 1201, hd-s1.ibbd.net, executor 2, partition 1201, NODE_LOCAL, 6026 bytes)
17/07/25 15:25:56 INFO TaskSetManager: Finished task 1199.0 in stage 0.0 (TID 1199) in 5902 ms on hd-s1.ibbd.net (executor 2) (1200/5408)
```

## 问题分析





