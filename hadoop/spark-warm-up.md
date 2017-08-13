### 利用 Spark 进行数据处理

#### RDD

弹性分布式数据集 RDD（Resilient Distributed Dataset），RDD就是一个不可变的带分区的记录集合，RDD也是Spark中的编程模型。

Spark提供了RDD上的两类操作，转换和动作。转换是用来定义一个新的RDD，包括map, flatMap, filter, union, sample, join, groupByKey, cogroup, ReduceByKey, cros, sortByKey, mapValues等。

动作是返回一个结果，包括collect, reduce, count, save, lookupKey。


Spark的API非常简单易用，Spark的WordCount的示例如下所示：

```python
from pyspark import SparkContext, SparkConf

conf = SparkConf().setMaster('local[*]').setAppName('TestApp')
sc = SparkContext(conf = conf)

rdd = sc.textFile("./spark/README.md")

word_count_rdd = rdd.flatMap(lambda line:line.split(' '))\
                    .map(lambda word:(word,1))\
                    .reduceByKey(lambda a,b:a+b)

word_count_rdd.saveAsTextFile("./word_count.txt")
```


在Spark中，所有RDD的转换都是是惰性求值的。RDD的转换操作会生成新的RDD，新的RDD的数据依赖于原来的RDD的数据，每个RDD又包含多个分区。那么一段程序实际上就构造了一个由相互依赖的多个RDD组成的有向无环图（DAG）。并通过在RDD上执行动作将这个有向无环图作为一个Job提交给Spark执行。



#### DataFrame

与RDD类似，DataFrame也是一个分布式数据容器。然而DataFrame更像传统数据库的二维表格，除了数据以外，还掌握数据的结构信息，即schema。同时，与Hive类似，DataFrame也支持嵌套数据类型（struct、array和map）。从API易用性的角度上 看，DataFrame API提供的是一套高层的关系操作，比函数式的RDD API要更加友好，门槛更低。由于与R和Pandas的DataFrame类似，Spark DataFrame很好地继承了传统单机数据分析的开发体验。



