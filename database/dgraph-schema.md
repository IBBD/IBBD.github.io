# Dgraph schema and index
Schema是用来指定predicates的类型的，用于做类型检查和强制转换。

## 1. Schema Types

Dgraph Type | Go type
----------- | ---------
int	        | int64
float	    | float
string	    | string
bool	    | bool
id	        | string
date	    | time.Time (RFC3339 format [Optional timezone] eg: 2006-01-02T15:04:05.999999999+10:00 or 2006-01-02T15:04:05.999999999)
geo	        | go-geom
uid	        | uint64

说明：

- uid类型就是对象的唯一标识。
- Mutations只会检查标量类型（scalar types）。
- 如果schema中没有指定类型，则会根据第一行mutation来断定类型。如果没有指定存储类型，就会作为default类型处理，而存储上就是作为string类型。

## 2. 索引
要想在字段上实现过滤功能，必须先在上面建立索引。

索引的定义类似如下：

```
name: string @index .
age: int @index .
address: string @index .
dateofbirth: date @index .
health: float @index .
location: geo @index .
timeafterbirth:  datetime @index .
```

在Dgraph中，除了uid类型，其他所有的标量类型都可以被索引。在上面的例子中，dgraph使用默认的tokenizer来索引，此外我们也可以制定tokenizer，例如这样：

```
name: string @index(exact, term) .
age: int @index(int) .
address: string @index(term) .
dateofbirth: date @index(date) .
health: float @index(float) .
location: geo @index(geo) .
timeafterbirth:  datetime @index(datetime) .
```

现在支持的tokenizer包括：term, fulltext, exact, int, float, geo, date, datetime。在一个索引中可以支持多种tokenizer，特别是在字符串的字段中。

### 2.1 字符串索引
有三种支持的字符串类型：exact, term and fulltext。

Index type	| Usage
----------- | -----------
exact	         | matching of entire value
term	         | matching of terms/words
fulltext	     | matching with language specific stemming and stopwords
trigram	regular  | expressions matching

## 3. 反向边（Reverse Edges）
在Dgraph中，边（关系）都是有方式的，从一个节点到另一个节点。不过也提供了定义反向边的功能：

```
directed_by: uid @reverse .
```

使用方式如下：

```
curl localhost:8080/query -XPOST -d '
{
  me(id: m.06pj8) {
    name@en
    ~directed_by(first: 5) {
      name@en
    }
  }
}'
```

## 4. 增加和修改Schema

```
curl localhost:8080/query -XPOST -d $'
mutation {
  schema {
    genre: uid @reverse .
  }
}'
```

## 5. 获取Schema

```
curl localhost:8080/query -XPOST -d '
schema {
  type
  index
  reverse
  tokenizer
}'
```

上面命令的返回值如下：

```
{
  "schema": [
    {
      "predicate": "crew_gig.crew_role",
      "type": "uid"
    },
    {
      "predicate": "regional_release_date.release_date",
      "type": "date"
    },
    {
      "predicate": "metacritic_id",
      "type": "default"
    },
    {
      "predicate": "cut.note",
      "type": "string"
    },
    {
      "predicate": "name",
      "type": "string",
      "index": true,
      "tokenizer": [
        "term",
        "exact",
        "fulltext",
        "trigram"
      ]
    },
    {
      "predicate": "loc",
      "type": "geo",
      "index": true,
      "tokenizer": [
        "geo"
      ]
    },
    {
      "predicate": "rating",
      "type": "uid",
      "reverse": true
    }
  ]
}
```


