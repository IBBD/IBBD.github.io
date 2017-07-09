# Pyspark处理csv文件
[前一篇](/hadoop/pyspark-base.md)

扩展阅读：https://github.com/databricks/spark-csv

## 从csv读入数据

```sh
csvFile = spark.read.csv("/hello.csv", header=True)

# 查看读入的数据
csvFile.show()

# 类型
print(type(csvFile))  # 输出：<class 'pyspark.sql.dataframe.DataFrame'>
print(type(csvFile['name']))  # 输出：Column<b'name'>

print(csvFile.columns)
print(csvFile.dtypes)
print(csvFile.printSchema())

# 常用函数
csvFile.first()
csvFile.head()
csvFile.count()
csvFile.take(1)  # [Row(name='hello', age='20')]
csvFile.collect()

# 选择列
csv.select('name').show()
csv.select('name', 'age').show()
```

### 读入的数据格式问题
上面读入csv时，字段都是默认类型，也就是都是字符串类型，这样可能会对处理过程造成一些麻烦。也不复杂：

```sh
# 定义模式
schema = StructType([StructField('name', StringType, True), \
    StructField('age', IntegerType(), True)])
csvFile = spark.read.csv("/hello.csv", header=True, schema=schema)
print(csvFile.printSchema())
"""输出结果
root
 |-- name: string (nullable = true)
 |-- age: integer (nullable = true)
"""

# 将某个值都加1
csvFile.select("name", csvFile['age']+1).show()

# 将满足条件的结果筛选出来
csvFile.filter(csvFile['age']>22).show()
```


### 将DataFrame转化为RDD
很简单，例如：

```sh
csvRdd = csvFile.rdd

# 然后就可以使用rdd的方式去处理数据了
csvRdd.filter(lambda r: r.age > '20').collect()
```

### 读入多个文件
也是非常简单，例如：

```sh
# 可以利用通配符
csvFile = spark.read.csv("/hello_*.csv", header=True, schema=schema)
```


