# Spark RDD方法集合
说明：截图主要来自《Spark快速数据分析》

- RDD
- Pair RDD
- 优化RDD
- examples

## RDD

### Translation
转化操作

![RDD Translation methods](/_img/spark/spark-rdd-translation-methods.jpg)

### Action
行动操作

![RDD Action methods](/_img/spark/spark-rdd-action-methods.jpg)

## Pair RDD （键值对RDD）
所谓键值对RDD，即其值形如`(key, value)`这种格式的RDD。

普通的RDD需要转化为键值RDD也简单，例如：

```python
# 这里这里设置每个key的初始值都是1
rdd.map(lambda x: (x, 1))
```

### Translation

![Pair RDD Translation methods](/_img/spark/spark-pair-rdd-translation-methods.jpg)

![Two Pair RDD Translation methods](/_img/spark/spark-two-pair-rdd-translation-methods.jpg)

### Action

![Pair RDD Action methods](/_img/spark/spark-pair-rdd-action-methods.jpg)

## 优化RDD

### 缓存
Spark RDD 是惰性求值的,而有时我们希望能多次使用同一个 RDD。如果简单地对 RDD 调用行动操作,Spark 每次都会重算 RDD 以及它的所有依赖。这在迭代算法中消耗格外大,因为迭代算法常常会多次使用同一组数据。例:

```python
result = input.map(lambda x: x*x)
print(result.count())
print(result.collect())
```

上面的map将会被重复计算，应该改成如下：

```python
result = input.map(lambda x: x*x).cache(MEMORY_ONLY)
print(result.count())
print(result.collect())
```

注意：存储的级别有多种，选择合适的级别也很重要。默认是`MEMORY_ONLY`

### 数据分区
在分布式程序中, 通信的代价是很大的,因此控制数据分布以获得最少的网络传输可以极大地提升整体性能。和单节点的程序需要为记录集合选择合适的数据结构一样,Spark 程序可以通过控制 RDD 分区方式来减少通信开销。分区并不是对所有应用都有好处的——比如,如果给定 RDD 只需要被扫描一次,我们完全没有必要对其预先进行分区处理。只有当数据集多次在诸如连接这种基于键的操作中使用时,分区才会有帮助。



