# 利用 Spark 进行数据处理

### RDD

弹性分布式数据集 RDD（Resilient Distributed Dataset），RDD就是一个不可变的带分区的记录集合，RDD也是Spark中的编程模型。
Spark提供了RDD上的两类操作，转换（transformations） 和 动作（actions）

- 转换是用来定义一个新的RDD，包括map, flatMap, filter, union, sample, join, groupByKey, cogroup, ReduceByKey, cros, sortByKey, mapValues等。

- 动作是返回一个结果，包括collect, reduce, count, save, lookup等。

在Spark中，所有RDD的转换都是是惰性求值的，它们不会马上计算它们的结果。相反的，它们仅仅记录转换操作是应用到哪些基础数据集(例如一个文件)上的。当执行动作(action)操作时才计算，将结果返回给驱动程序。

默认情况下，每一个转换过的 RDD 会在每次执行动作(action)的时候重新计算一次。然而，你也可以使用 persist (或 cache)方法持久化(persist)一个 RDD 到内存中。

为了说明 RDD 基本知识，Spark的WordCount的示例如下所示：

```python
from pyspark import SparkContext, SparkConf

conf = SparkConf().setMaster('local[*]').setAppName('TestApp')
sc = SparkContext(conf=conf)

lines_rdd = sc.textFile("./spark/README.md")

word_count_rdd = lines_rdd.flatMap(lambda line:line.split(' '))\
                    .map(lambda word: (word,1))\
                    .reduceByKey(lambda a,b: a+b)
word_count_rdd.persist()
word_count_rdd.saveAsTextFile("./word_count.txt")
```

### 转换操作
| 转换操作 | 含义 |
| ------ | ------ |
| map(func) | 对RDD中的每个元素调用func函数，然后返回结果构成新的RDD |
| filter(func) | 返回一个由通过传给filter的函数的元素组成的RDD |
| flatMap(func) | 将函数应用于RDD中的每一个元素，将返回的迭代器的所有内容构成新的RDD |
| mapPartitions(func) | 和map类似，不过运行在RDD的不同分块上，因此func的类型必须是Iterator<T>=>Iterator<U> |
| mapPartitionsWithIndex(func) | 和mapPartitions类似，不过func函数提供一个整数值表示分块的下标，所以函数的类型是(Int,Iterator<T>=>Iterator<U>) |
| sample(withReplacement,fraction,seed) | 对RDD采样，以及是否替换 |
| union(otherDataset) | 生成一个包含两个RDD中所有元素的RDD |
| intersection(otherDataset) | 返回由两个RDD中共同元素组成的RDD |
| distinct([numTasks]) | 返回去除原RDD中重复元素的新的RDD |
| groupByKey([numTasks]) | 对具有相同键的值进行分组。注意如果仅仅是为了聚合，使用reduceByKey或aggregateByKey性能更好 |
| reduceByKey(func,[numTasks]) | 合并既有相同键的值 |
| aggregateByKey(zeroValue)(seqOp,combOp,[numTasks]) | 和reduceByKey类似，不过需要提供一个初始值 |
| sortByKey([ascending],[numTasks]) | 返回一个根据键排序的RDD |
| join(otherDataset,[numTasks]) | 对两个RDD进行内连接。其它的连接操作还有leftOuterJoin，rightOuterJoin和fullOuterJoin |
| cogroup(otherDataset,[numTasks]) | 也叫groupWith，对类型(K,V)和(K,W)的RDD进行操作，返回(K,(Iterable<V>,Iterable<W>))类型的RDD |
| cartesian(otherDataset) | 对类型T和U的RDD进行操作，返回(T,U)类型的RDD |
| pipe(command,[envVars]) | 将RDD的每个分区通过管道传给一个shell脚本 |
| coalesce(numPartitions) | 减少RDD的分区数量。当对一个大的RDD执行filter操作后使用会有效 |
| repartition(numPartitions) | 对RDD重新分区 |
| repartitionAndSortWithinPartitions(partitioner) | 根据给定的partitioner对RDD重新分区，在每个分区再根据键排序


### 行动操作
| 行动操作 | 含义 |
| ------| ------|
| reduce(func) | 使用func函数并行整合RDD中的所有元素 |
| collect() | 返回RDD中的所有元素 |
| count() | 返回RDD中的元素个数 |
| first() | 返回RDD中的第一个元素 |
| take(n) | 返回RDD中的n个元素 |
| takeSample(withReplacement,num,[seed]) | 从RDD中返回任意一些元素，结果不确定 |
| takeOrdered(n,[ordering]) | 从RDD中按照提供的顺序返回最前面的n个元素 |
| saveAsTextFile(path) | 将RDD中的元素写入文本文件，Spark会调用元素的toString方法 |
| saveAsSequenceFile(path) | 将RDD中的元素保存为Hadoop的SequenceFile文件 |
| saveAsObjectFile(path) | 将RDD中的元素使用Java中的序列化保存为对象文件，可以使用SparkContext.objectFile()读取 |
| countByKey() | 操作键值对RDD，根据键值分别计数 |
| foreach(func) | 对RDD中的每个元素调用给定的函数func |


### DataFrame

与RDD类似，DataFrame也是一个分布式数据容器。然而DataFrame更像传统数据库的二维表格，除了数据以外，还掌握数据的结构信息，即schema。同时，与Hive类似，DataFrame也支持嵌套数据类型（struct、array和map）。从API易用性的角度上 看，DataFrame API提供的是一套高层的关系操作，比函数式的RDD API要更加友好，门槛更低。由于与R和Pandas的DataFrame类似，Spark DataFrame很好地继承了传统单机数据分析的开发体验。

![DataFrame和 RDD的区别](/_img/spark/DataFrame-RDD-different.png)


```python
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql.types import StructField, StringType, IntegerType

conf = SparkConf().setMaster('local[*]').setAppName('TestApp')
sc = SparkContext(conf = conf)
spark = SparkSession(sc)

schema = StructType([StructField("user_id", StringType(), True),
                     StructField("name", StringType(), True),
                     StructField("age", IntegerType(), True),
                     StructField("email", StringType(), True),
                     ])
df = spark.read.csv('user.csv', schema=schema, header=False)
df.show()
```

|  user_id  |  name  |  age  |  email  |
| ------------ | ------------ | ------------ | ------------ |
|  1  |  Key  |  20 |  key@key.com  |
|  2  |  Alice  |  18  |  alice@al.com  |
|  3  |  Jack |  22  |  jack@jj.com  |

我们可以很方便查看一些统计类的信息
```
df.select(df.age).describe().show()
```
|  summary  |  age  |
| ------------ | ------------ |
|  count  |   3  |
|   mean  |  20.0  |
| stddev  |  1.0  |
|    min  |  19  |
|    max  |  21  |

```





