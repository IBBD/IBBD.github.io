# Hive基础入门

```
hive> show databases;
OK
default
Time taken: 2.023 seconds, Fetched: 1 row(s)
hive> use default;
OK
Time taken: 0.038 seconds
hive> show tables;
OK
t_hive
Time taken: 0.043 seconds, Fetched: 1 row(s)
```

可见，默认是在一个default的数据库中。

## 1. Hive数据管理
Hive是建立在Hadoop上的数据仓库基础架构。它提供了一系列的工具，用来进行数据提取、转换、加载，这是一种可以存储、查询和分析存储在Hadoop中的大规模数据机制。可以把Hadoop下结构化数据文件映射为一张成Hive中的表，并提供类sql查询功能，除了不支持更新、索引和事务，sql其它功能都支持。可以将sql语句转换为MapReduce任务进行运行，作为sql到MapReduce的映射器。

### 1.1 元数据存储

Hive将元数据存储在RDBMS中，有三种方式可以连接到数据库：

- 内嵌模式：元数据保持在内嵌数据库的Derby，一般用于单元测试，只允许一个会话连接
- 多用户模式：在本地安装Mysql，把元数据放到Mysql内
- 远程模式：元数据放置在远程的Mysql数据库

### 1.2 数据存储

首先，Hive没有专门的数据存储格式，也没有为数据建立索引，用于可以非常自由的组织Hive中的表，只需要在创建表的时候告诉Hive数据中的列分隔符和行分隔符，这就可以解析数据了。

其次，Hive中所有的数据都存储在HDFS中，Hive中包含4中数据模型：Tabel、ExternalTable、Partition、Bucket。

- Table：类似与传统数据库中的Table，每一个Table在Hive中都有一个相应的目录来存储数据。例如：一个表zz，它在HDFS中的路径为：/wh/zz，其中wh是在hive-site.xml中由${hive.metastore.warehouse.dir}指定的数据仓库的目录，所有的Table数据（不含External Table）都保存在这个目录中。
- Partition：类似于传统数据库中划分列的索引。在Hive中，表中的一个Partition对应于表下的一个目录，所有的Partition数据都存储在对应的目录中。例如：zz表中包含ds和city两个Partition，则对应于ds=20140214，city=beijing的HDFS子目录为：/wh/zz/ds=20140214/city=Beijing;
- Buckets：对指定列计算的hash，根据hash值切分数据，目的是为了便于并行，每一个Buckets对应一个文件。将user列分数至32个Bucket上，首先对user列的值计算hash，比如，对应hash=0的HDFS目录为：/wh/zz/ds=20140214/city=Beijing/part-00000;对应hash=20的，目录为：/wh/zz/ds=20140214/city=Beijing/part-00020。
- ExternalTable指向已存在HDFS中的数据，可创建Partition。和Table在元数据组织结构相同，在实际存储上有较大差异。Table创建和数据加载过程，可以用统一语句实现，实际数据被转移到数据仓库目录中，之后对数据的访问将会直接在数据仓库的目录中完成。删除表时，表中的数据和元数据都会删除。ExternalTable只有一个过程，因为加载数据和创建表是同时完成。世界数据是存储在Location后面指定的HDFS路径中的，并不会移动到数据仓库中。

### 1.3 数据交换

- 用户接口：包括客户端、Web界面和数据库接口
- 元数据存储：通常是存储在关系数据库中的，如Mysql，Derby等
- Hadoop：用HDFS进行存储，利用MapReduce进行计算。
- 关键点：Hive将元数据存储在数据库中，如Mysql、Derby中。Hive中的元数据包括表的名字、表的列和分区及其属性、表的属性（是否为外部表）、表数据所在的目录等。

Hive的数据存储在HDFS中，大部分的查询由MapReduce完成。

## 2. 第一个demo

准备文件：

```
hive> dfs -cat file:/root/hive-test.log;
1,hello
2,world
```

创建表，导入数据，删表等：

```
# 创建测试数据表
hive> CREATE TABLE t_hive (a int, b string) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';
OK
Time taken: 2.366 seconds

# 导入数据
hive> LOAD DATA LOCAL INPATH '/root/hive-test.log' OVERWRITE INTO TABLE t_hive ;
Loading data to table default.t_hive
OK
Time taken: 0.97 seconds

# 查询数据
hive> select * from t_hive;
OK
1	hello
2	world
Time taken: 0.118 seconds, Fetched: 2 row(s)

# 查看表结构
hive> desc t_hive;
OK
a                   	int                 	                    
b                   	string              	                    
Time taken: 2.091 seconds, Fetched: 2 row(s)

# 查看数据库的信息
# 该命令可以查到我们创建的t_hive表所对应的的hdfs中的路径
hive> describe database default;
OK
default	Default Hive database	hdfs://ibbd/user/hive/warehouse	public	ROLE	
Time taken: 0.025 seconds, Fetched: 1 row(s)

# 查看hdfs中对应的文件的格式
# 从这里可以看到我们导入的文件
hive> dfs -ls hdfs://ibbd/user/hive/warehouse;
Found 1 items
drwxr-xr-x   - root supergroup          0 2017-03-19 23:04 hdfs://ibbd/user/hive/warehouse/t_hive
hive> dfs -cat hdfs://ibbd/user/hive/warehouse/t_hive/hive-test.log;
1,hello
2,world

# 删除数据表
drop table t_hive;
```

## 3. 数据结构

```sql
-- 扩展数据类型
data_type
  : primitive_type
  | array_type
  | map_type
  | struct_type
  | union_type  -- (Note: Available in Hive 0.7.0 and later)
array_type : ARRAY < data_type >
map_type : MAP < primitive_type, data_type >
struct_type : STRUCT < col_name : data_type [COMMENT col_comment], ...>
union_type : UNIONTYPE < data_type, data_type, ... >  -- (Note: Available in Hive 0.7.0 and later)

-- 基本数据类型 
primitive_type
  : TINYINT
  | SMALLINT
  | INT
  | BIGINT
  | BOOLEAN
  | FLOAT
  | DOUBLE
  | STRING
  | BINARY      -- (Note: Available in Hive 0.8.0 and later)
  | TIMESTAMP   -- (Note: Available in Hive 0.8.0 and later)
  | DECIMAL     -- (Note: Available in Hive 0.11.0 and later)
  | DECIMAL(precision, scale)  -- (Note: Available in Hive 0.13.0 and later)
  | DATE        -- (Note: Available in Hive 0.12.0 and later)
  | VARCHAR     -- (Note: Available in Hive 0.12.0 and later)
  | CHAR        -- (Note: Available in Hive 0.13.0 and later)
```

## 4. Hive  DDL
Hive DDL的语方法为类SQL语法，所以标准的SQL语法大多数在Hive中都可用。

```sql
-- Hive建表 语法
CREATE [EXTERNAL] TABLE [IF NOT EXISTS] table_name   
  [(col_name data_type [COMMENT col_comment], ...)]   
  [COMMENT table_comment]   
  [PARTITIONED BY (col_name data_type [COMMENT col_comment], ...)]   
  [CLUSTERED BY (col_name, col_name, ...)   
  [SORTED BY (col_name [ASC|DESC], ...)] INTO num_buckets BUCKETS]   
  [ROW FORMAT row_format]   
  [STORED AS file_format]   
  [LOCATION hdfs_path]  
-- CREATE TABLE 创建一个指定名字的表。如果相同名字的表已经存在，则抛出异常；用户可以用 IF NOT EXIST 选项来忽略这个异常  
-- EXTERNAL 关键字可以让用户创建一个外部表，在建表的同时指定一个指向实际数据的路径（LOCATION）  
-- LIKE 允许用户复制现有的表结构，但是不复制数据  
-- COMMENT可以为表与字段增加描述  

-- ROW FORMAT  
    DELIMITED [FIELDS TERMINATED BY char] [COLLECTION ITEMS TERMINATED BY char]  
        [MAP KEYS TERMINATED BY char] [LINES TERMINATED BY char]  
        | SERDE serde_name [WITH SERDEPROPERTIES (property_name=property_value, property_name=property_value, ...)]  
-- 用户在建表的时候可以自定义 SerDe 或者使用自带的 SerDe。如果没有指定 ROW FORMAT 或者 ROW FORMAT DELIMITED，将会使用自带的 SerDe。在建表的时候，用户还需要为表指定列，用户在指定表的列的同时也会指定自定义的 SerDe，Hive 通过 SerDe 确定表的具体的列的数据。  


create table person( 
    id int, 
    name string, 
    age int, 
    likes array<string>, 
    address map<string,string> 
) 
row format delimited  
-- 指定导入数据的列与列之间的分隔符
fields terminated by ','  
-- 指定Array类型的分隔符
collection ITEMS TERMINATED BY  '-' 
-- 指定map类型的分隔符
map keys terminated by ':'  
-- 指定行与行之间的分隔符
lines terminated by '\n'; 
```

数据格式例如：

```
# 三条数据，列与列之间用,号隔开；array之间用-号隔开；map之间用：号隔开；行与行用换行符隔开
1,tom,28,game-music-book,stu:henan-home:henan-work:beijing
2,jack,21,money-meinv,stu:wuhan-home:wuhan
3,lusi,18,shopping-music,stu:shanghai-home:beijing
```

## 5. 数据查询

```sql
-- 查询所有
select * from person;

-- 还可以这样查
select * from person where name='tom';

-- 或者这样
select * from person where likes[1]='music';

-- 还有这样
select * from person where address['stu']='shanghai'; 

-- 还有这样
select avg(age) from person;

-- ... 等标准的SQL语法大多都可以在Hive中使用包括一些函数，因为Hive是类SQL的；
```

但在Hive中`不推荐进行这些操作：Insert、Update、Delete等操作`，因为Hive的特性是对数据仓库的数据进行提取，针对的数据是批量的，`不适合行级的运算`。

## 6. 清空表

```sql
-- 使truncate清空表
TRUNCATE TABLE person;
-- 通过覆盖的方式清空表
insert overwrite table person select * from person where 1=2;
```

## 7. 加载数据

```
语法：LOAD DATA [LOCAL] INPATH 'filepath' [OVERWRITE] INTO TABLE tablename [PARTITION (partcol1=val1, partcol2=val2 ...)]
```

## 8. Hive的内表
Hive 的内表，就是正常创建的表。在删除时，既删除内表的元数据，也删除内表的数据。

## 9. Hive的外表
删除时，仅仅删除外表的元数据。创建Hive 的外表，需要使用关键字 External：

## 10. 分区表
分区表是通过关键字PARTITIONED BY来实现分区，一个表有一个或多个分区，分区是以字段的形式在表结构中存在，通过describe table命令可以查看到字段存在，但是该字段不存放实际的数据内容，仅仅是分区的表示（伪列）。

在HDFS中，分区每个分区的值都会产生相应的文件夹，然后在对应的文件夹下存放相应的表数据。

其实就是在数据的目录下, 用不同目录来区分, 比如, dt, 就是按日期(date)来区分, country 国家, hour 小时等等.对应的会在数据的目录下有分区目录. 可以建双分区, 就是子目录下再分区(其实就是一棵目录树).

参考: http://blog.csdn.net/dajuezhao/archive/2010/07/21/5753055.aspx

分区表的应用场景分析：假如针对全球的一家电子商务公司，现在有这样一个业务需求就是需要了解一下海外市场的情况，目的是进一步想拓展海外市场，但是公司对海外市场的拓展现在还没有任何的了解，那么怎么帮助公司管理层提供数据上的支撑呢？这个时候可以对之前公司针对全球销售的商品通过按“国家”来分区，在查询的时候，以国家为为纬度来进行分析海外的市场情况。

```sql
partitioned by (date string)

-- 修改分区的存储路径
-- 注意格式：dt='2008-08-08' ：dt表示分区名，'2008-08-08'表示对应分区值。注意格式。若是字符串的话就是“string”
-- "new location"就是对应存储路径，应该是绝对路径
ALTER TABLE table_name PARTITION (dt='2008-08-08') SET LOCATION "new location";

-- 修改分区名称
ALTER TABLE table_name PARTITION (dt='2008-08-08') RENAME TO PARTITION (dt='20080808');

-- 删除分区
ALTER TABLE login DROP IF EXISTS PARTITION (dt='2008-08-08'); 
ALTER TABLE page_view DROP IF EXISTS PARTITION (dt='2008-08-08', country='us');

-- 添加分区
ALTER TABLE table_name ADD PARTITION (partCol = 'value1') location 'loc1';
```

### 10.1 静态分区
hive中创建分区表没有什么复杂的分区类型(范围分区、列表分区、hash分区、混合分区等)。分区列也不是表中的一个实际的字段，而是一个或者多个伪列。意思是说在表的数据文件中实际上并不保存分区列的信息与数据。
下面的语句创建了一个简单的分区表：

```sql
create table partition_test(member_id string, name string)
partitioned by (stat_date string, province string)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';

-- 这个例子中创建了stat_date和province两个字段作为分区列。通常情况下需要先预先创建好分区，然后才能使用该分区，例如：
alter table partition_test add partition (stat_date='20110728',province='zhejiang');
```

这样我们就可以看到相应的目录: `/path/to/partition_test/stat_date=20110728/province=zhejiang`。这时就可以往分区表写入数据了：

```sql
insert overwrite table partition_test partition(stat_date='20110527',province='liaoning') 
  select member_id,name from partition_test_input;
```

这就是静态分区，写入数据时，需要指定分区。

### 10.2 动态分区
按照上面的方法向分区表中插入数据，如果源数据量很大，那么针对一个分区就要写一个insert，非常麻烦。况且在之前的版本中，必须先手动创建好所有的分区后才能插入，这就更麻烦了，你必须先要知道源数据中都有什么样的数据才能创建分区。

动态分区可以根据查询得到的数据自动匹配到相应的分区中去。 使用动态分区要先设置hive.exec.dynamic.partition参数值为true，默认值为false，即不允许使用：

```
hive> set hive.exec.dynamic.partition;
hive.exec.dynamic.partition=false
hive> set hive.exec.dynamic.partition=true;
hive> set hive.exec.dynamic.partition;
hive.exec.dynamic.partition=true
```

动态分区的使用方法很简单，假设我想向stat_date='20110728'这个分区下面插入数据，至于province插入到哪个子分区下面让数据库自己来判断，那可以这样写：

```sql
insert overwrite table partition_test partition(stat_date='20110728',province)
  select member_id,name,province from partition_test_input where stat_date='20110728';
```

stat_date叫做静态分区列，province叫做动态分区列。select子句中需要把动态分区列按照分区的顺序写出来，静态分区列不用写出来。这样stat_date='20110728'的所有数据，会根据province的不同分别插入到/user/hive/warehouse/partition_test/stat_date=20110728/下面的不同的子文件夹下，如果源数据对应的province子分区不存在，则会自动创建，非常方便，而且避免了人工控制插入数据与分区的映射关系存在的潜在风险。

注意，动态分区不允许主分区采用动态列而副分区采用静态列，这样将导致所有的主分区都要创建副分区静态列所定义的分区

动态分区可以允许所有的分区列都是动态分区列，但是要首先设置一个参数hive.exec.dynamic.partition.mode ：

```
hive> set hive.exec.dynamic.partition.mode;
hive.exec.dynamic.partition.mode=strict
```
它的默认值是strick，即不允许分区列全部是动态的，这是为了防止用户有可能原意是只在子分区内进行动态建分区，但是由于疏忽忘记为主分区列指定值了，这将导致一个dml语句在短时间内创建大量的新的分区（对应大量新的文件夹），对系统性能带来影响。
所以我们要设置：

```
hive> set hive.exec.dynamic.partition.mode=nostrick;
```

## 11. 元数据相关表说明
在hive中，元数据存储在关系数据库中（例如，我们使用的mysql）。

```
mysql> show tables;
+---------------------------+
| Tables_in_hive            |
+---------------------------+
| AUX_TABLE                 |
| BUCKETING_COLS            |
| CDS                       |
| COLUMNS_V2                |
| COMPACTION_QUEUE          |
| COMPLETED_COMPACTIONS     |
| COMPLETED_TXN_COMPONENTS  |
| DATABASE_PARAMS           |
| DBS                       |
| DB_PRIVS                  |
| DELEGATION_TOKENS         |
| FUNCS                     |
| FUNC_RU                   |
| GLOBAL_PRIVS              |
| HIVE_LOCKS                |
| IDXS                      |
| INDEX_PARAMS              |
| KEY_CONSTRAINTS           |
| MASTER_KEYS               |
| NEXT_COMPACTION_QUEUE_ID  |
| NEXT_LOCK_ID              |
| NEXT_TXN_ID               |
| NOTIFICATION_LOG          |
| NOTIFICATION_SEQUENCE     |
| NUCLEUS_TABLES            |
| PARTITIONS                |
| PARTITION_EVENTS          |
| PARTITION_KEYS            |
| PARTITION_KEY_VALS        |
| PARTITION_PARAMS          |
| PART_COL_PRIVS            |
| PART_COL_STATS            |
| PART_PRIVS                |
| ROLES                     |
| ROLE_MAP                  |
| SDS                       |
| SD_PARAMS                 |
| SEQUENCE_TABLE            |
| SERDES                    |
| SERDE_PARAMS              |
| SKEWED_COL_NAMES          |
| SKEWED_COL_VALUE_LOC_MAP  |
| SKEWED_STRING_LIST        |
| SKEWED_STRING_LIST_VALUES |
| SKEWED_VALUES             |
| SORT_COLS                 |
| TABLE_PARAMS              |
| TAB_COL_STATS             |
| TBLS                      |
| TBL_COL_PRIVS             |
| TBL_PRIVS                 |
| TXNS                      |
| TXN_COMPONENTS            |
| TYPES                     |
| TYPE_FIELDS               |
| VERSION                   |
| WRITE_SET                 |
+---------------------------+
57 rows in set (0.00 sec)
```

### 11.1 Database表

```
mysql> mysql> select * from DBS;
+-------+-----------------------+---------------------------------+---------+------------+------------+
| DB_ID | DESC                  | DB_LOCATION_URI                 | NAME    | OWNER_NAME | OWNER_TYPE |
+-------+-----------------------+---------------------------------+---------+------------+------------+
|     1 | Default Hive database | hdfs://ibbd/user/hive/warehouse | default | public     | ROLE       |
+-------+-----------------------+---------------------------------+---------+------------+------------+
1 row in set (0.00 sec)
```

default数据库正式我们上面所看到的，使用`describe database default`命令所查到的信息。

### 11.2 Table表

TBLS存储Hive Table的元数据信息,每个表有唯一的TBL_ID。
SD_ID外键指向所属的Database,SD_IID关联SDS表的主键。 其中SDS存储列(CD_ID)等信息。TBLS.SD_ID关联SDS.SD_ID, SDS.SD_ID关联CDS.CD_ID, CDS.CD_ID关联COLUMNS_V2.CD_ID。

```
mysql> desc TBLS;
+--------------------+--------------+------+-----+---------+-------+
| Field              | Type         | Null | Key | Default | Extra |
+--------------------+--------------+------+-----+---------+-------+
| TBL_ID             | bigint(20)   | NO   | PRI | NULL    |       |
| CREATE_TIME        | int(11)      | NO   |     | NULL    |       |
| DB_ID              | bigint(20)   | YES  | MUL | NULL    |       |
| LAST_ACCESS_TIME   | int(11)      | NO   |     | NULL    |       |
| OWNER              | varchar(767) | YES  |     | NULL    |       |
| RETENTION          | int(11)      | NO   |     | NULL    |       |
| SD_ID              | bigint(20)   | YES  | MUL | NULL    |       |
| TBL_NAME           | varchar(128) | YES  | MUL | NULL    |       |
| TBL_TYPE           | varchar(128) | YES  |     | NULL    |       |
| VIEW_EXPANDED_TEXT | mediumtext   | YES  |     | NULL    |       |
| VIEW_ORIGINAL_TEXT | mediumtext   | YES  |     | NULL    |       |
+--------------------+--------------+------+-----+---------+-------+
11 rows in set (0.00 sec)
```

使用`select * from TBLS`就能查到我们所创建的表的元数据信息，例如表ID，表名，创建时间等。根据表ID就能查到字段的相关定义：

```
mysql> select * from COLUMNS_V2 where CD_ID=4;
+-------+---------+-------------+-----------+-------------+
| CD_ID | COMMENT | COLUMN_NAME | TYPE_NAME | INTEGER_IDX |
+-------+---------+-------------+-----------+-------------+
|     4 | NULL    | a           | int       |           0 |
|     4 | NULL    | b           | string    |           1 |
+-------+---------+-------------+-----------+-------------+
2 rows in set (0.00 sec)
```

### 11.3 SDS表(数据存储表)

```
mysql> select * from SDS\G;
*************************** 1. row ***************************
                    SD_ID: 4
                    CD_ID: 4
             INPUT_FORMAT: org.apache.hadoop.mapred.TextInputFormat
            IS_COMPRESSED:  
IS_STOREDASSUBDIRECTORIES:  
                 LOCATION: hdfs://ibbd/user/hive/warehouse/t_hive
              NUM_BUCKETS: -1
            OUTPUT_FORMAT: org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat
                 SERDE_ID: 4
```

- CD_ID关联COLUMN_V2.CD_ID，指定该数据的字段信息
- SERDE_ID关联SERDES.SERDE_ID，指定该数据的序列化信息(如是否是序列化表，DELIMITED字段等)

注：更多的关于元数据表的文件，请查看下面的链接：

- http://www.2cto.com/database/201311/255627.html
- http://www.cnblogs.com/1130136248wlxk/articles/5517909.html 

## 12. Hive与HBase的区别与应用场景
### 12.1 区别

- Apache Hive是一个构建在Hadoop基础设施之上的数据仓库。通过Hive可以使用HQL语言查询存放在HDFS上的数据。HQL是一种类SQL语言，这种语言最终被转化为Map/Reduce. 虽然Hive提供了SQL查询功能，但是Hive不能够进行交互查询--因为它只能够在Haoop上批量的执行Hadoop。
- Apache HBase是一种Key/Value系统，它运行在HDFS之上。和Hive不一样，Hbase的能够在它的数据库上实时运行，而不是运行MapReduce任务。

### 12.2 限制

- Hive目前不支持更新操作。另外，由于hive在hadoop上运行批量操作，它需要花费很长的时间，通常是几分钟到几个小时才可以获取到查询的结果。Hive必须提供预先定义好的schema将文件和目录映射到列，并且Hive与ACID不兼容。
- HBase查询是通过特定的语言来编写的，这种语言需要重新学习。类SQL的功能可以通过Apache Phonenix实现，但这是以必须提供schema为代价的。另外，Hbase也并不是兼容所有的ACID特性，虽然它支持某些特性。最后但不是最重要的--为了运行Hbase，Zookeeper是必须的，zookeeper是一个用来进行分布式协调的服务，这些服务包括配置服务，维护元信息和命名空间服务。

### 12.3 应用场景

- Hive适合用来对一段时间内的数据进行分析查询，例如，用来计算趋势或者网站的日志。Hive不应该用来进行实时的查询。因为它需要很长时间才可以返回结果。
- Hbase非常适合用来进行大数据的实时查询。Facebook用Hbase进行消息和实时的分析。它也可以用来统计Facebook的连接数。

## 13. 常见问题

### 13.1 从csv文件加载数据
从csv导入数据时，很可能会碰到引号的问题，需要引入插件进行解决：

```sql
-- https://cwiki.apache.org/confluence/display/Hive/CSV+Serde
CREATE TABLE my_table(a string, b string, ...)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = "\t",
   "quoteChar"     = "'",
   "escapeChar"    = "\\"
)  
STORED AS TEXTFILE;
```

另外一个解决方案是使用`\t`进行分隔。

除了分隔符，还有另一个比较麻烦的问题是换行符的问题，这个恐怕得做预处理了，把字段内的换行符都处理掉。（社区也可能有相关的插件能解决问题）

### 13.2 将多个文件同时导入一个外部数据表
例如日志记录数据很可能是按照时间分成了不同的文件的，这时需要将多个文件导入一个表中。hive支持将一个目录导入，也支持将导入多个文件。


