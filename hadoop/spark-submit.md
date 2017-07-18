# Spark-submit及参数说明
下面的说明主要针对python

- 官方文档：http://spark.apache.org/docs/latest/submitting-applications.html
- 相关中文文档：http://ifeve.com/spark-submit/

## 提交Spark应用
spark-submit脚本在Spark的bin目录下，可以利用此脚本向集群提交Spark应用。该脚本为所有Spark所支持的集群管理器（ cluster managers）提供了统一的接口，因此，你基本上可以用同样的配置和脚本，向不同类型的集群管理器提交你的应用。


## 打包应用程序依赖
如果你的代码依赖于其他工程，那么你需要把依赖项也打包进来，并发布给Spark集群。

对于Python，你可以使用spark-submit的–py-files参数，将你的程序以.py、.zip 或.egg文件格式提交给集群。如果你需要依赖很多Python文件，我们推荐你使用.zip或者.egg来打包。

## 利用spark-submit启动应用
一旦打包好一个应用程序，你就可以用bin/spark-submit来提交之。这个脚本会自动设置Spark及其依赖的classpath，同时可以支持多种不同类型的集群管理器、以及不同的部署模式：

```sh
./bin/spark-submit \
  --class <main-class> \
  --master <master-url> \
  --deploy-mode <deploy-mode> \
  --conf <key>=<value> \
  ... # other options
  <application-jar> \
  [application-arguments]
```

一些常用的选项如下：

- `--class`: 应用入口类（例如：org.apache.spark.examples.SparkPi）
- `--master`: 集群的master URL （如：spark://23.195.26.187:7077）
- `--deploy-mode`: 驱动器进程是在集群上工作节点运行（cluster），还是在集群之外客户端运行（client）（默认：client）
- `--conf`: 可以设置任意的Spark配置属性，键值对（key=value）格式。如果值中包含空白字符，可以用双引号括起来（”key=value“）。
- `application-jar`: 应用程序jar包路径，该jar包必须包括你自己的代码及其所有的依赖项。如果是URL，那么该路径URL必须是对整个集群可见且一致的，如：hdfs://path 或者 file://path （要求对所有节点都一致）
- `application-arguments`: 传给入口类main函数的启动参数，如果有的话。

一种常见的部署策略是，在一台网关机器上提交你的应用，这样距离工作节点的物理距离比较近。这种情况下，client模式会比较适合。client模式下，驱动器直接运行在spark-submit的进程中，同时驱动器对于集群来说就像是一个客户端。应用程序的输入输出也被绑定到控制台上。因此，这种模式特别适用于交互式执行（REPL），spark-shell就是这种模式。

当然，你也可以从距离工作节点很远的机器（如：你的笔记本）上提交应用，这种情况下，通常适用cluster模式，以减少网络驱动器和执行器之间的网络通信延迟。注意：对于Mesos集群管理器，Spark还不支持cluster模式。目前，只有YARN上Python应用支持cluster模式。

对于Python应用，只要把`<application-jar>`换成一个.py文件，再把.zip、.egg或者.py文件传给–py-files参数即可。

有一些参数是专门用于设置集群管理器的（cluster manager）。例如，在独立部署（ Spark standalone cluster ）时，并且使用cluster模式，你可以用–supervise参数来确保驱动器在异常退出情况下（退出并返回非0值）自动重启。spark-submit –help可查看完整的选项列表。这里有几个常见的示例：

```sh
# Run application locally on 8 cores
./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master local[8] \
  /path/to/examples.jar \
  100

# Run on a Spark standalone cluster in client deploy mode
./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://207.184.161.138:7077 \
  --executor-memory 20G \
  --total-executor-cores 100 \
  /path/to/examples.jar \
  1000

# Run on a Spark standalone cluster in cluster deploy mode with supervise
./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://207.184.161.138:7077 \
  --deploy-mode cluster \
  --supervise \
  --executor-memory 20G \
  --total-executor-cores 100 \
  /path/to/examples.jar \
  1000

# Run on a YARN cluster
export HADOOP_CONF_DIR=XXX
./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master yarn \
  --deploy-mode cluster \  # can be client for client mode
  --executor-memory 20G \
  --num-executors 50 \
  /path/to/examples.jar \
  1000

# Run a Python application on a Spark standalone cluster
./bin/spark-submit \
  --master spark://207.184.161.138:7077 \
  examples/src/main/python/pi.py \
  1000

# Run on a Mesos cluster in cluster deploy mode with supervise
./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master mesos://207.184.161.138:7077 \
  --deploy-mode cluster \
  --supervise \
  --executor-memory 20G \
  --total-executor-cores 100 \
  http://path/to/examples.jar \
  1000
```

## Master URLs
传给Spark的master URL可以是以下几种格式：

Master URL                      | 说明
------------------------------- | ---------
local                           | 本地运行Spark，只用1个worker线程（没有并行计算）
local[K]                        | 本地运行Spark，使用K个worker线程（理论上，最好将这个值设为你机器上CPU core的个数）
local[K,F]                      | 本地运行Spark，使用K个worker线程 and F maxFailures (see spark.task.maxFailures for an explanation of this variable)
local[*]                        | 本地运行Spark，使用worker线程数同你机器上逻辑CPU core个数
local[*,F]                      | 本地运行Spark，使用worker线程数同你机器上逻辑CPU core个数 and F maxFailures
spark://HOST:PORT               | 连接到指定的Spark独立部署的集群管理器（Spark standalone cluster）。端口是可以配置的，默认7077。
spark://HOST1:PORT1,HOST2:PORT2 | 
mesos://HOST:PORT               | 连接到指定的Mesos集群。端口号可以配置，默认5050。如果Mesos集群依赖于ZooKeeper，可以使用 mesos://zk://… 来提交，注意 –deploy-mode需要设置为cluster，同时，HOST:PORT应指向 MesosClusterDispatcher.
yarn                            | 连接到指定的 YARN  集群，使用–deploy-mode来指定 client模式 或是 cluster 模式。YARN集群位置需要通过 $HADOOP_CONF_DIR 或者 $YARN_CONF_DIR 变量来查找。

注意：Cluster deploy mode is currently not supported for python applications on standalone clusters.

## 高级依赖管理
通过spark-submit提交应用时，application jar和–jars选项中的jar包都会被自动传到集群上。Spark支持以下URL协议，并采用不同的分发策略：

- file: 文件绝对路径，并且file:/URI是通过驱动器的HTTP文件服务器来下载的，每个执行器都从驱动器的HTTP server拉取这些文件。
- hdfs:, http:, https:, ftp: – 设置这些参数后，Spark将会从指定的URI位置下载所需的文件和jar包。
- local: local:/ 打头的URI用于指定在每个工作节点上都能访问到的本地或共享文件。这意味着，不会占用网络IO，特别是对一些大文件或jar包，最好使用这种方式，当然，你需要把文件推送到每个工作节点上，或者通过NFS和GlusterFS共享文件。

注意，每个SparkContext对应的jar包和文件都需要拷贝到所对应执行器的工作目录下。一段时间之后，这些文件可能会占用相当多的磁盘。在YARN上，这些清理工作是自动完成的；而在Spark独立部署时，这种自动清理需要配置 spark.worker.cleanup.appDataTtl 属性。

用户还可以用–packages参数，通过给定一个逗号分隔的maven坐标，来指定其他依赖项。这个命令会自动处理依赖树。额外的maven库（或者SBT resolver）可以通过–repositories参数来指定。Spark命令（pyspark，spark-shell，spark-submit）都支持这些参数。

对于Python，也可以使用等价的–py-files选项来分发.egg、.zip以及.py文件到执行器上。

## 附录
查看cpu数量的命令：

```sh
cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c
```



