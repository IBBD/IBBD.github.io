# HBase基础命令
基于版本1.2.4

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
创建一个具有两个列族“grad”和“course”的表“scores”。其中表名、行和列都要用单引号括起来,并以逗号隔开。
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
```
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
```
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

### 13).  status命令
```
hbase(main):072:0> status
```

### 14).  version命令
```
hbase(main):073:0> version
```

另外,在 shell 中,常量不需要用引号引起来,但二进制的值需要双引号引起来,而其他值则用单引号引起来。HBase Shell 的常量可以通过在 shell 中输入“Object.constants”。



