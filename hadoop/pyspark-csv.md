# Pyspark处理csv文件

- [前一篇](/hadoop/pyspark-base.md)
- 扩展阅读：https://github.com/databricks/spark-csv
- DataFrame操作：https://www.analyticsvidhya.com/blog/2016/10/spark-dataframe-and-operations/

## 1. spark.read.csv方式
这种方式也可以读入json等格式

```python
# 这个不会实际加载数据
df = spark.read.csv("/hello.csv", header=True)

# 查看读入的数据
df.show()

# 类型
print(type(df))  # 输出：<class 'pyspark.sql.dataframe.DataFrame'>
print(type(df['name']))  # 输出：Column<b'name'>

print(df.columns)
print(df.dtypes)
print(df.printSchema())

# 常用函数
df.first()
df.head()
df.count()
df.take(1)  # [Row(name='hello', age='20')]
df.collect()

# 选择列
csv.select('name').show()
csv.select('name', 'age').show()
```

### 1.1 读入的数据格式问题
上面读入csv时，字段都是默认类型，也就是都是字符串类型，这样可能会对处理过程造成一些麻烦。也不复杂：

```python
from pyspark.sql.types import *

# 定义模式
schema = StructType([StructField('name', StringType(), True), \
    StructField('age', IntegerType(), True)])
df = spark.read.csv("/hello.csv", header=True, schema=schema)
print(df.printSchema())
"""输出结果
root
 |-- name: string (nullable = true)
 |-- age: integer (nullable = true)
"""

# 将某个值都加1
df.select("name", df['age']+1).show()

# 将满足条件的结果筛选出来
df.filter(df['age']>22).show()
```


### 1.2 将DataFrame转化为RDD
很简单，例如：

```python
rdd = df.rdd

# 然后就可以使用rdd的方式去处理数据了
rdd.filter(lambda r: r.age > '20').collect()
```

### 1.3 读入多个文件
也是非常简单，例如：

```python
# 可以利用通配符
df = spark.read.csv("/hello_*.csv", header=True, schema=schema)
```

## 2. 使用sqlContext读入数据
官方文档上用的就是这种方式。

```python
from pyspark.sql import SQLContext
from pyspark.sql.types import *

# 定义模式
schema = StructType([StructField('name', StringType(), True), \
    StructField('age', IntegerType(), True)])

# 读入数据
sqlContext = SQLContext(sc)
df = sqlContext.read \
    .format('com.databricks.spark.csv') \
    .options(header='true') \
    .load('/hello.csv', schema=schema)
print(df.printSchema())
```

## 3. DataFrame操作
DataFrame 是 Spark 在 RDD 之后新推出的一个数据集，从属于 Spark SQL 模块，适用于结构化数据。

- API文档：http://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame

```python
# 查看数据的字段类型
df.columns

# 显示前面的N条数据
df.first()
df.head(3)

# 统计记录的行数
df.count()

# 字段的描述性统计：count, mean, avg, sum, min, max
df.summary('age').show
"""输出结果如下：
+-------+-----------------+
|summary|              age|
+-------+-----------------+
|  count|                4|
|   mean|            26.25|
| stddev|5.795112883571237|
|    min|               20|
|    max|               34|
+-------+-----------------+
"""

# 选择若干列数据
df.select('name','age').show(5)

# 选择某列的唯一值
df.select('name').distinct().show()

# 缺失值填充
# 使用-1来填充
df.fillna(-1).show(2)

# 根据条件过滤满足条件的行
df.filter(df['age']>22).show()
df.filter(df.age>22).show()

# 数据透视
# 可以进行的计算有：sum, min, max, count, mean
df.groupby('name').agg({'age': 'mean'}).show()

# 排序
df.orderBy(df.age.desc()).show()

# 对单个字段进行统计
df..groupby('id').count().show()
"""
+---------------+-----+
|            _c4|count|
+---------------+-----+
|811002608346736|23944|
|811002443262645|27255|
|811078167875023|29790|
|811078025544915| 9787|
+---------------+-----+
"""

# 交叉表
df.crosstab('name', 'age').show()
"""
+--------+---+---+---+---+
|name_age| 20| 25| 26| 34|
+--------+---+---+---+---+
|    alex|  0|  1|  0|  0|
|   world|  0|  0|  1|  1|
|   hello|  1|  0|  0|  0|
+--------+---+---+---+---+
"""

# 增加字段
df2 = df.withColumn('label', df.age/2.0).show()
df2.show()

# 删除字段
# 可以同时删除多个字段
df2.drop('label').columns
df2.drop("age", "label").show()

# 把DataFrame注册成临时表，用SQL进行查询
df.createOrReplaceTempView('df_table')
sqlContext.sql('select name, age from df_table').show(5)

# 结果写入csv文件
df.write.csv("/hello2.csv")
```

在使用withColumn增加字段的时候，有一个相应的函数库pyspark.sql.functions，例如计算绝对值的abs等。不过在实际使用时，可能需要自定义函数，例如：

```python
import pyspark.sql.functions as F
import pyspark.sql.types as T

# 注意在lambda中的age参数的类型是：<class 'int'>
# 注意传入的参数和输出的参数类型需要保持一致
user_func = F.UserDefinedFunction(lambda age: 1 if int(age)<30 else 2, T.StringType())
df2 = df.withColumn('label', user_func(df.age))
df2.show()
```

### 3.1 Pandas和PySpark DataFrame的区别

- 在PySpark中，计算是延迟的。
- 在Pyspark中，不能修改DataFrame，只能转换（Transform）
- Pandas支持更多的API
- 复杂运算在Pandas上也更加容易实现。

如果需要，也可以转化为Pandas：`df.toPandas()`

## 4. RDD操作

- API文档：http://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.RDD

```python
# 保存到csv文件
rdd.map(lambda x: ','.join((str(w) for w in x))).saveAsTextFile('/hello_target.csv')
```
