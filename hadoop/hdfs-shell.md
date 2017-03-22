# HDFS shell基本命令
该文档介绍hdfs基础的增删改查及与文件系统的交互等基本操作。以下命令是基于`Hadoop 2.7.3`.

## HDFS的读写流程

![HDFS读取文件](/_img/hdfs-read.png)

如图所示，读取文件的时候会先从NameNode读取元数据，然后根据元数据去DataNode读取具体的文件内容。

![HDFS写入文件](/_img/hdfs-write.png)

写入文件的时候，会先将文件分拆成Block，由NameNode决定每个块应该保存在哪些DataNode上，在DataNode上自动生成相应的副本，最后更新NameNode中的元数据信息。

## 帮助命令
帮助命令是最基础也是最重要的命令之一。

hdfs的命令如下：

```
root@dsp-dev:/home/hadoop# app/hadoop/bin/hdfs 
Usage: hdfs [--config confdir] [--loglevel loglevel] COMMAND
       where COMMAND is one of:
  dfs                  run a filesystem command on the file systems supported in Hadoop.
  classpath            prints the classpath
  namenode -format     format the DFS filesystem
  secondarynamenode    run the DFS secondary namenode
  namenode             run the DFS namenode
  journalnode          run the DFS journalnode
  zkfc                 run the ZK Failover Controller daemon
  datanode             run a DFS datanode
  dfsadmin             run a DFS admin client
  haadmin              run a DFS HA admin client
  fsck                 run a DFS filesystem checking utility
  balancer             run a cluster balancing utility
  jmxget               get JMX exported values from NameNode or DataNode.
  mover                run a utility to move block replicas across
                       storage types
  oiv                  apply the offline fsimage viewer to an fsimage
  oiv_legacy           apply the offline fsimage viewer to an legacy fsimage
  oev                  apply the offline edits viewer to an edits file
  fetchdt              fetch a delegation token from the NameNode
  getconf              get config values from configuration
  groups               get the groups which users belong to
  snapshotDiff         diff two snapshots of a directory or diff the
                       current directory contents with a snapshot
  lsSnapshottableDir   list all snapshottable dirs owned by the current user
						Use -help to see options
  portmap              run a portmap service
  nfs3                 run an NFS version 3 gateway
  cacheadmin           configure the HDFS cache
  crypto               configure HDFS encryption zones
  storagepolicies      list/get/set block storage policies
  version              print the version
```

其中`dfs`是文件系统的相关命令，类似shell中的文件系统的。其帮助如下：

```
root@dsp-dev:/home/hadoop# app/hadoop/bin/hdfs dfs
Usage: hadoop fs [generic options]
	[-appendToFile <localsrc> ... <dst>]
	[-cat [-ignoreCrc] <src> ...]
	[-checksum <src> ...]
	[-chgrp [-R] GROUP PATH...]
	[-chmod [-R] <MODE[,MODE]... | OCTALMODE> PATH...]
	[-chown [-R] [OWNER][:[GROUP]] PATH...]
	[-copyFromLocal [-f] [-p] [-l] <localsrc> ... <dst>]
	[-copyToLocal [-p] [-ignoreCrc] [-crc] <src> ... <localdst>]
	[-count [-q] [-h] <path> ...]
	[-cp [-f] [-p | -p[topax]] <src> ... <dst>]
	[-createSnapshot <snapshotDir> [<snapshotName>]]
	[-deleteSnapshot <snapshotDir> <snapshotName>]
	[-df [-h] [<path> ...]]
	[-du [-s] [-h] <path> ...]
	[-expunge]
	[-find <path> ... <expression> ...]
	[-get [-p] [-ignoreCrc] [-crc] <src> ... <localdst>]
	[-getfacl [-R] <path>]
	[-getfattr [-R] {-n name | -d} [-e en] <path>]
	[-getmerge [-nl] <src> <localdst>]
	[-help [cmd ...]]
	[-ls [-d] [-h] [-R] [<path> ...]]
	[-mkdir [-p] <path> ...]
	[-moveFromLocal <localsrc> ... <dst>]
	[-moveToLocal <src> <localdst>]
	[-mv <src> ... <dst>]
	[-put [-f] [-p] [-l] <localsrc> ... <dst>]
	[-renameSnapshot <snapshotDir> <oldName> <newName>]
	[-rm [-f] [-r|-R] [-skipTrash] <src> ...]
	[-rmdir [--ignore-fail-on-non-empty] <dir> ...]
	[-setfacl [-R] [{-b|-k} {-m|-x <acl_spec>} <path>]|[--set <acl_spec> <path>]]
	[-setfattr {-n name [-v value] | -x name} <path>]
	[-setrep [-R] [-w] <rep> <path> ...]
	[-stat [format] <path> ...]
	[-tail [-f] <file>]
	[-test -[defsz] <path>]
	[-text [-ignoreCrc] <src> ...]
	[-touchz <path> ...]
	[-truncate [-w] <length> <path> ...]
	[-usage [cmd ...]]
```

这里的命令和shell中的相当类似。下面会逐一讲解一些基础的命令。

查看具体某个命令的帮助文档：

```
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -help appendToFile
-appendToFile <localsrc> ... <dst> :
  Appends the contents of all the given local files to the given dst file. The dst
  file will be created if it does not exist. If <localSrc> is -, then the input is
  read from stdin.
```

## 增
将文件添加到HDFS中。

```sh
# 准备一个文件
echo "hello world" > hello.txt

# 将该文件添加到HDFS系统的跟目录中
# 如果找不到hdfs命令，就需要先知道hadoop的安装目录
hdfs dfs -put hello.txt hdfs:/

# 创建一个新文件
hdfs dfs -touchz /hello2.txt

# 新建目录
hdfs dfs -mkdir /hello

# 删除目录
hdfs dfs -rmdir /hello
```

## 查
查询HDFS中的文件，以及查看文件的内容。

```sh
# 查看HDFS系统中根目录的文件
hdfs dfs -ls /

# 下面的命令也会输出相同的结果
# 其中ibbd是集群名
hdfs dfs -ls hdfs://ibbd/

# 下面几个的结果也是一样的
hdfs dfs -ls hdfs:///
hdfs dfs -ls hdfs:/

```

该命令输出如下：

```
Found 3 items
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 15:27 /hbase
-rw-r--r--   2 root   supergroup         12 2017-03-18 22:26 /hello.txt
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 14:14 /home
```

其中的hello.txt就是刚才添加的。`在集群的其他服务器执行该命令也能得到相同的结果。`
如果想查看某个文件的内容，如下：

```sh
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -cat /hello.txt
hello world
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -tail /hello.txt
hello world

```

用过linux系统的人，应该很熟悉`cat`, `tail`和`ls`等这些命令了。

## 改
包括修改文件名，修改文件内容等。

```
# 这是将一个文件的内容增加的hdfs原有的文件之中
root@s1:/home/hadoop# echo "hello world 2" > hello2.txt
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -appendToFile hello2.txt hdfs:/hello.txt
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -tail /hello.txt
hello world
hello world 2

# 这是将一个move到另一个位置
# mv这个命令应该也是非常熟悉的了
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -mv hdfs:/hello.txt hdfs:/hello2.txt
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -ls /
Found 3 items
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 15:27 /hbase
-rw-r--r--   2 root   supergroup         26 2017-03-18 23:02 /hello2.txt
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 14:14 /home
```

## 删
最后就是删除文件了，其实就是一个`rm`命令。

```
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -rm /hello2.txt
17/03/18 23:08:04 INFO fs.TrashPolicyDefault: Namenode trash configuration: Deletion interval = 0 minutes, Emptier interval = 0 minutes.
Deleted /hello2.txt
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -ls /
Found 2 items
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 15:27 /hbase
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 14:14 /home
```

## 与文件系统的交互
与文件系统进行交互的基础命令。

```
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -copyFromLocal hello2.txt hdfs:/hello.txt
root@s1:/home/hadoop# app/hadoop/bin/hdfs dfs -ls /
Found 3 items
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 15:27 /hbase
-rw-r--r--   2 root   supergroup         14 2017-03-18 23:12 /hello.txt
drwxr-xr-x   - hadoop supergroup          0 2017-03-17 14:14 /home
```

除了`-copyFromLocal`，还有`-copyToLocal`，另外，复制文件也可以这样：`hdfs dfs -cp file:/home/hadoop/hello.txt hdfs:/hello.txt`

此外，还有：

- -moveFromLocal
- -moveToLocal
- -df: 查看文件系统的空间使用情况
- -mkdir: 创建目录




