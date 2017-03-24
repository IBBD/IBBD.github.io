# HBase基础命令
基于版本1.2.4

- 官网首页：https://hbase.apache.org/
- 中文文档（版本比较旧）：http://abloz.com/hbase/book.html

## 为什么需要HBase

- 半结构化或非结构化数据
对于数据结构字段不够确定或杂乱无章很难按一个概念去进行抽取的数据适合用HBase。当业务发展需要增加存储比如一个用户的email，phone，address信息时RDBMS需要停机维护，而HBase支持动态增加.
- 记录非常稀疏
RDBMS的行有多少列是固定的，为null的列浪费了存储空间。而如上文提到的，HBase为null的Column不会被存储，这样既节省了空间又提高了读性能。
- 多版本数据
根据Row key和Column key定位到的Value可以有任意数量的版本值，因此对于需要存储变动历史记录的数据，用HBase就非常方便了。对于某一值，业务上一般只需要最新的值，但有时可能需要查询到历史值。
- 超大数据量
当数据量越来越大，RDBMS数据库撑不住了，就出现了读写分离策略，通过一个Master专门负责写操作，多个Slave负责读操作，服务器成本倍增。随着压力增加，Master撑不住了，这时就要分库了，把关联不大的数据分开部署，一些join查询不能用了，需要借助中间层。随着数据量的进一步增加，一个表的记录越来越大，查询就变得很慢，于是又得搞分表，比如按ID取模分成多个表以减少单个表的记录数。经历过这些事的人都知道过程是多么的折腾。采用HBase就简单了，只需要加机器即可，HBase会自动水平切分扩展，跟Hadoop的无缝集成保障了其数据可靠性（HDFS）和海量数据分析的高性能（MapReduce）

## 逻辑视图及基础概念

![hbase表结构](/_img/hbase-tables.png)

- RowKey：是Byte array，是表中每条记录的“主键”，方便快速查找，Rowkey的设计非常重要。
- Column Family：列族，拥有一个名称(string)，包含一个或者多个相关列
- Column：属于某一个columnfamily，familyName:columnName，每条记录可动态添加
- Timestamp: HBase通过row和column确定一份数据，这份数据的值可能有多个版本，不同版本的值按照时间倒序排序，即最新的数据排在最前面，查询时默认返回最新版本。Timestamp默认为系统当前时间（精确到毫秒），也可以在写入数据时指定该值。
- Version Number：类型为Long，默认值是系统时间戳，可由用户自定义
- Value(Cell)：Byte array。每个值通过4个键唯一索引，tableName+RowKey+ColumnKey+Timestamp=>value

下面这个图可能看得更清楚一点：

![hbase逻辑视图](/_img/hbase-logistic-vis.png)

## 物理视图
- 每个column family存储在HDFS上的一个单独文件中，空值不会被保存。
- Key 和 Version number在每个 column family中均有一份；
- HBase 为每个值维护了多级索引，即：<key, column family, column name, timestamp>

物理存储:

1. Table中所有行都按照row key的字典序排列；
2. Table在行的方向上分割为多个Region；
3. Region按大小分割的，每个表开始只有一个region，随着数据增多，region不断增大，当增大到一个阀值的时候，region就会等分会两个新的region，之后会有越来越多的region；
4. Region是Hbase中分布式存储和负载均衡的最小单元，不同Region分布到不同RegionServer上。

![hbase逻辑视图](/_img/hbase-ph-vis1.png)

Region虽然是分布式存储的最小单元，但并不是存储的最小单元。Region由一个或者多个Store组成，每个store保存一个columns family；每个Strore又由一个memStore和0至多个StoreFile组成，StoreFile包含HFile；memStore存储在内存中，StoreFile存储在HDFS上。

![hbase逻辑视图](/_img/hbase-ph-vis2.png)

## 查看版本号和帮助文档

```
hbase(main):013:0> version
1.2.4, r67592f3d062743907f8c5ae00dbbe1ae4f69e5af, Tue Oct 25 18:10:20 CDT 2016

hbase(main):014:0> help "create"
Creates a table. Pass a table name, and a set of column family
specifications (at least one), and, optionally, table configuration.
Column specification can be a simple string (name), or a dictionary
(dictionaries are described below in main help output), necessarily 
including NAME attribute. 
Examples:

Create a table with namespace=ns1 and table qualifier=t1
  hbase> create 'ns1:t1', {NAME => 'f1', VERSIONS => 5}

Create a table with namespace=default and table qualifier=t1
  hbase> create 't1', {NAME => 'f1'}, {NAME => 'f2'}, {NAME => 'f3'}
  hbase> # The above in shorthand would be the following:
  hbase> create 't1', 'f1', 'f2', 'f3'
  hbase> create 't1', {NAME => 'f1', VERSIONS => 1, TTL => 2592000, BLOCKCACHE => true}
  hbase> create 't1', {NAME => 'f1', CONFIGURATION => {'hbase.hstore.blockingStoreFiles' => '10'}}
  
Table configuration options can be put at the end.
Examples:

  hbase> create 'ns1:t1', 'f1', SPLITS => ['10', '20', '30', '40']
  hbase> create 't1', 'f1', SPLITS => ['10', '20', '30', '40']
  hbase> create 't1', 'f1', SPLITS_FILE => 'splits.txt', OWNER => 'johndoe'
  hbase> create 't1', {NAME => 'f1', VERSIONS => 5}, METADATA => { 'mykey' => 'myvalue' }
  hbase> # Optionally pre-split the table into NUMREGIONS, using
  hbase> # SPLITALGO ("HexStringSplit", "UniformSplit" or classname)
  hbase> create 't1', 'f1', {NUMREGIONS => 15, SPLITALGO => 'HexStringSplit'}
  hbase> create 't1', 'f1', {NUMREGIONS => 15, SPLITALGO => 'HexStringSplit', REGION_REPLICATION => 2, CONFIGURATION => {'hbase.hregion.scan.loadColumnFamiliesOnDemand' => 'true'}}
  hbase> create 't1', {NAME => 'f1', DFS_REPLICATION => 1}

You can also keep around a reference to the created table:

  hbase> t1 = create 't1', 'f1'

Which gives you a reference to the table named 't1', on which you can then
call methods.
```

## 基础命令
![hbase shell基础命令](/_img/hbase-shell.png)

这里 grad 对于表来说是一个列,course 对于表来说是一个列族,这个列族由三个列组成 china、math 和 english,当然我们可以根据我们的需要在 course 中建立更多的列族,如computer,physics 等相应的列添加入 course 列族。(备注:列族下面的列也是可以没有名字的。)
### 1). create 命令
创建一个具有三个列族“name”，“grad”和“course”的表“scores”。其中表名、行和列都要用单引号括起来,并以逗号隔开。
```
hbase(main):012:0> create 'scores', 'name', 'grad', 'course'
```

### 2). list 命令
查看当前 HBase 中具有哪些表。
```
hbase(main):012:0> list
```

### 3). describe 命令
查看表“scores”的构造。
```
hbase(main):012:0> describe 'scores'
```

### 4). put 命令
使用 put 命令向表中插入数据,参数分别为表名、行名、列名和值,其中列名前需要列族最为前缀,时间戳由系统自动生成。
格式: put 表名,行名,列名([列族:列名]),值
例子：

a. 加入一行数据,行名称为“xiapi”,列族“grad”的列名为”(空字符串)”,值位 1。

```
hbase(main):012:0> put 'scores', 'xiapi', 'grad:', '1'
hbase(main):012:0> put 'scores', 'xiapi', 'grad:', '2' --修改操作(update)
```

b. 给“xiapi”这一行的数据的列族“course”添加一列“<china,97>”。

```
hbase(main):012:0> put 'scores', 'xiapi',  'course:china', '97'
hbase(main):012:0> put 'scores', 'xiapi',  'course:math', '128'
hbase(main):012:0> put 'scores', 'xiapi',  'course:english', '85'
```

### 5). get 命令
a.查看表“scores”中的行“xiapi”的相关数据。

```
hbase(main):012:0> get 'scores', 'xiapi'
COLUMN                   CELL                                                                  
 course:china            timestamp=1490181754907, value=97                                     
 course:english          timestamp=1490181771805, value=85                                     
 course:math             timestamp=1490181763773, value=128                                    
 grad:                   timestamp=1490186456036, value=2                                      
```
注意这里的结构，和普通的关系型数据库非常大的区别。

b.查看表“scores”中行“xiapi”列“course :math”的值。

```
hbase(main):012:0> get 'scores', 'xiapi', 'course:math'
```
或者
```
hbase(main):012:0> get 'scores', 'xiapi', {COLUMN=>'course:math'}
hbase(main):012:0> get 'scores', 'xiapi', {COLUMNS=>'course:math'}
```
备注:COLUMN 和 COLUMNS 是不同的,scan 操作中的 COLUMNS 指定的是表的列族, get操作中的 COLUMN 指定的是特定的列,COLUMNS 的值实质上为“列族:列修饰符”。COLUMN 和 COLUMNS 必须为大写。

### 6). scan 命令
a. 查看表“scores”中的所有数据。
```
hbase(main):012:0> scan 'scores'
```
注意:
scan 命令可以指定 startrow,stoprow 来 scan 多个 row。
例如:
scan 'user_test',{COLUMNS =>'info:username',LIMIT =>10, STARTROW => 'test', STOPROW=>'test2'}
b.查看表“scores”中列族“course”的所有数据。
```
hbase(main):012:0> scan  'scores', {COLUMN => 'grad'}
hbase(main):012:0> scan  'scores', {COLUMN=>'course:math'}
hbase(main):012:0> scan  'scores', {COLUMNS => 'course'}
hbase(main):012:0> scan  'scores', {COLUMNS => 'course'}
```

### 7). count 命令
```
hbase(main):068:0> count 'scores'
```

### 8). exists 命令
```
hbase(main):071:0> exists 'scores'
```

### 9). incr 命令(赋值)
计数器

```
# 使用了put去修改计数器 会导致后面的错误 原因是'1'会转换成Bytes.toBytes()
hbase(main):069:0> incr 'scores', 'xiapi', 'grad:', 1
ERROR: org.apache.hadoop.hbase.DoNotRetryIOException: Field is not a long, it's 1 bytes wide

# 直接新增一个计数器
hbase(main):079:0> incr 'scores', 'xiapi', 'grad:hello', 2
COUNTER VALUE = 2

# 注意其结构的不同
hbase(main):081:0> scan "scores"
ROW                      COLUMN+CELL                                                           
 xiapi                   column=course:math, timestamp=1490181763773, value=128                
 xiapi                   column=grad:hello, timestamp=1490187028068, value=\x00\x00\x00\x00\x00
                         \x00\x00\x02 
```

### 10). delete 命令
删除表“scores”中行为“xiaoxue”, 列族“course”中的“math”。
```
hbase(main):012:0>  delete 'scores', 'xiapi', 'course:math'
```

### 11). truncate 命令
```
hbase(main):012:0>  truncate 'scores'
```

### 12). disbale、drop 命令
通过“disable”和“drop”命令删除“scores”表。
```
hbase(main):012:0>  disable 'scores' --enable 'scores' 
hbase(main):012:0>  drop 'scores'
```

注意：drop之前一定要先disable。

### 13).  status命令
```
hbase(main):072:0> status
```

### 14).  version命令
```
hbase(main):073:0> version
```

另外,在 shell 中,常量不需要用引号引起来,但二进制的值需要双引号引起来,而其他值则用单引号引起来。HBase Shell 的常量可以通过在 shell 中输入“Object.constants”。

### 15). 数据版本

```
# 创建表及列族
# 默认只会存储最新的版本
hbase(main):012:0> create 'member','address','info'
0 row(s) in 1.2450 seconds

# 更改info列族存储最新的2个版本的数据
hbase(main):015:0> alter 'member',{NAME=>'info',VERSIONS=>2}
Updating all regions with the new schema...
1/1 regions updated.
Done.
0 row(s) in 2.0320 seconds

hbase(main):016:0> put 'member','hello','info:age',26
0 row(s) in 0.0930 seconds

hbase(main):017:0> put 'member','hello','info:age',27
0 row(s) in 0.0150 seconds

hbase(main):018:0> put 'member','hello','info:age',29
0 row(s) in 0.0120 seconds

# 获取历史版本的数据
hbase(main):020:0> get 'member','hello',{COLUMN=>'info:age',VERSIONS=>3}
COLUMN                   CELL                                                                  
 info:age                timestamp=1490192145804, value=29                                     
 info:age                timestamp=1490192141569, value=27       

# 对时间戳做时间范围查询
hbase(main):001:0> get 'member','hello',{COLUMN=>'info:age',TIMERANGE=>[1490192141568,1490192141570],VERSIONS=>3}
COLUMN                   CELL                                                                  
 info:age                timestamp=1490192141569, value=27    
```

#### 自定义版本号
在使用的过程中，可能我们还经常需要自定义版本号，例如如果我们需要记录用户每天的点击数，那么我们就可以用日期做版本号，每天保留一个版本，这个非常有效：

```
hbase(main):016:0> put "member", "action", "info:clicks", 32, 20160322
0 row(s) in 0.0070 seconds

hbase(main):017:0> scan "member"
ROW                      COLUMN+CELL
 action                  column=info:clicks, timestamp=20160322, value=32
```

## 与HDFS的关系
按上面的操作创建了`scores`数据表之后，在hdfs中相应的位置为：

```
# 一个数据表对应在hdfs中就是一个目录
hadoop@dsp-dev:~$ hdfs dfs -ls /hbase/data/default/scores/
Found 3 items
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 17:59 /hbase/data/default/scores/.tabledesc
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 17:59 /hbase/data/default/scores/.tmp
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 20:25 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650

# 从这里很明显的看出hbase是按列族存储的
hadoop@dsp-dev:~$ hdfs dfs -ls /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650
Found 6 items
-rw-r--r--   1 hadoop supergroup         41 2017-03-22 17:59 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/.regioninfo
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 20:25 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/.tmp
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 20:25 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/course
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 20:25 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/grad
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 17:59 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/name
drwxr-xr-x   - hadoop supergroup          0 2017-03-22 17:59 /hbase/data/default/scores/82ac635c5e1fa7f84be3de98f41b9650/recovered.edits
```

## HBase架构及其基础组件

![hbase基础组件](/_img/hbase-components.png)

### Client

- 包含访问HBase的接口，并维护cache来加快对HBase的访问，比如region的位置信息

### Master

- 为Region server分配region
- 负责Region server的负载均衡
- 发现失效的Region server并重新分配其上的region
- 管理用户对table的增删改查操作

### Region Server

- Regionserver维护region，处理对这些region的IO请求
- Regionserver负责切分在运行过程中变得过大的region

### Zookeeper作用

- 通过选举，保证任何时候，集群中只有一个master，Master与RegionServers 启动时会向ZooKeeper注册
- 存贮所有Region的寻址入口
- 实时监控Region server的上线和下线信息。并实时通知给Master
- 存储HBase的schema和table元数据
- 默认情况下，HBase 管理ZooKeeper 实例，比如， 启动或者停止ZooKeeper
- Zookeeper的引入使得Master不再是单点故障


