# Dgraph重要概念及基础入门
dgraph 是可扩展的，分布式的，低延迟图形数据库。

DGraph 的目标是提供 Google 生产水平的规模和吞吐量，在超过TB的结构数据里，未用户提供足够低延迟的实时查询。DGraph 支持 GraphQL 作为查询语言，响应 JSON。

- 官方文档：https://docs.dgraph.io/
- Github：https://github.com/dgraph-io/dgraph
- 图数据库的对比：https://docs.dgraph.io/dgraph-compared-to-other-databases/

## 1. 重要概念
在Dgraph中，使用点来表示实体，边来表示关系，边还可以定义属性（facets），例如权重。

### 1.1 点（实体）：node
因为是有向图，所以实体又可以分成两类：

1. from实体
2. to实体

例如A借钱给B，那么在这个借钱的关系中，A是from实体，B是to实体。（当然，也可以定义一个被借钱的关系，这里B就成了from实体，而A就成了to实体）

#### 1.1.1 属性类型的to实体
有一类特殊的to实体，其实可以理解为from实体的属性，例如A的年龄是20岁，那么在年龄这个关系中，A是from实体，20岁是to实体，不过我们理解上就是A的年龄属性的值是20岁。

这类实体不能作为关系的起点。

#### 1.1.2 UID实体
每个实体（非属性）都由唯一的UID来表示。例如对于一个叫张三的人这个实体，UID是这个人的标识，张三只是这个的名字（一个关系）。在使用的时候，当然需要定义这个人的唯一标识，例如身份证号等，如果实在没有其他辅助的唯一标识，那么也可以直接使用张三作为唯一标识，那可能就会出现类似这样的关系：

```
<张三> <name> "张三" .
```

第一个张三是uid实体，第二个张三是属性实体，也就是<张三>这个实体的name关系的值。

说明：在使用的时候，我们可能会对张三做hash后才作为uid。（尽量应该保持原有的名称，以方便查询，尽量在关系名这个层面进行区分）

#### 1.1.3 RDF类型
文件见：https://docs.dgraph.io/query-language/#rdf-types

### 1.2 边（关系）：edge
关系有两个特性：

1. 方向性
2. 属性（或者可以理解为权重，在某些场景下）

还是以A借钱给B这个关系为例，我们就可以定义一个时间属性，表示这个关系是什么日期发生的（注意理解这里，不能和属性类的to实体搞混了，这个发生日期既不是A的属性，也不是B的属性，而是跟关系密切相关的）。

在Dgraph中用`facets`表示。

#### 1.2.1 索引
见文档：https://docs.dgraph.io/query-language/#indexing

建立在属性类型的to实体上。

增加索引的操作样例如下：

```sh
curl localhost:8080/query -XPOST -d '
mutation {
  schema {
    name: string @index .
    initial_release_date: date @index .
  }
}'
```

#### 1.2.2 反向边：Reverse Edges
很多时候，我们在使用的时候，可能还需要查询反向的关系，例如对于A借钱给B，我们除了根据A找到B，有时也需要根据B找到A，这时就需要一个反向的关系。

反向边需要做一个配置，例如：

```
directed_by: uid @reverse .
```

使用curl操作如下：

```sh
curl localhost:8080/query -XPOST -d $'
mutation {
  schema {
    directed_by: uid @reverse .
  }
}'
```

这时查询的时候，就可以这样用：

```
{
  me(id: m.06pj8) {
    name@en
    ~directed_by(first: 5) {
      name@en
    }
  }
}
```

当然，我们也可以直接插入一条反向的关系。

#### 1.2.3 边的属性：facets
设置：

```sh
curl localhost:8080/query -XPOST -d $'
mutation {
 set {
  <alice> <name> "alice" .
  <alice> <mobile> "040123456" (since=2006-01-02T15:04:05) .
  <alice> <car> "MA0123" (since=2006-02-02T13:01:09, first=true) .
 }
}'
```

查询：

```sh
curl localhost:8080/query -XPOST -d $'{
  data(id:alice) {
    name
    mobile @facets
    car @facets
  }
}'
```

如果是uid边，例如：

```sh
curl localhost:8080/query -XPOST -d $'
mutation {
 set {
  <alice> <name> "alice" .
  <bob> <name> "bob" .
  <bob> <car> "MA0134" (since=2006-02-02T13:01:09) .
  <alice> <friend> <bob> (close=true) .
 }
}'
```

这时查询语句应该是这样的：

```sh
curl localhost:8080/query -XPOST -d $'{
  data(id:alice) {
    name
    friend @facets(close) {
      name
    }
  }
}'
```

根据facets进行过滤数据：

```sh
curl localhost:8080/query -XPOST -d $'{
  data(id:<alice>) {
    friend @facets(eq(close, true) AND eq(relative, true)) @facets(relative) {
      name
    }
  }
}'
```


## 2. 与关系型数据库的区别
Dgraph存储的是图关系，本身没有库，表，行列等概念，不过从理解上，我们可以将一个关系理解为一行记录，点和边（及边的属性）可以理解为列，不同的关系，我们可以理解为不同的表。

因此在设计阶段，关系的名字是需要重点关注的，它的作用就类似表名，应该尽量避免重复，特别是不同业务之间的冲突。因此不同的业务之间，可以使用不同的前缀进行区分，而这个前缀也就担当这库的概念。

## 3. 设计
设计时应该重点考虑：

1. 实体关系图设计
2. 实体关系文档：应该包含关系名，from，to，facets，反向边，索引等
3. 实体UID的前缀规则要重点定义好：因为UID是全局的，为了避免冲突，前缀得提前定义好。UID不能有特殊字符，如空格，大于号，小于号等，如果值本身比较复杂，可以取hash值做为uid。
4. 所有实体（非属性实体）都应该保持一个统一的name关系（统一的命名比较容易测试，特别是前端可视化）

需要先定义好关系名前缀。

