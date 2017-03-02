# elasticsearch5版本映射的变化

## 1、string类型被替换成了text/keyword两种类型。 

对于分词字段的字符串字段用text来替换，对于不分词的字符串字段用keyword来替换，为了兼容5.0中还保留了string类型，将在6.0版本中去掉。

字符串映射现在有如下的默认映射：

```json
{
  "type": "text",
  "fields": {
    "keyword": {
      "type": "keyword",
      "ignore_above": 256
    }
  }
}
```

字符串被映射成了两个字段，一个字段进行分词，另一个子字段不进行分析，可以用于聚合或者排序。

## 2、数字类型

数字类型现在是一种全新的数据结构，被成为BKD tree。相比以前的方式有更快的对比查询效率和占用更少的磁盘空间。注意，数字类型将不参与索引的评分，如果需要对数字字段进行参与评分，可以同时映射为数字类型和keyword类型。例如：

```json
PUT my_index
{
  "mappings": {
    "my_type": {
      "properties": {
        "my_number": {
          "type": "long",
          "fields": {
            "keyword": {
              "type":  "keyword"
            }
          }
        }
      }
    }
  }
}
```
## 3、geo_point字段

和数字类型类型，Geo point字段类型也用了BKD tree结构。.由于这种结构从根本上进行多维空间数据的支持，下列字段参数将不在支持：Geohash，geohash_prefix，geohash_precision，lat_lon。Geohashes在接口中仍然可以使用，但他们不再是用来索引地理数据点。

## 4、_timestamp 和 _ttl 字段

元字段`_timestamp` 和 `_ttl`字段将不再被支持，对于`_timestamp`可以在文档中添加日期字段来代替或者用ingest pipline，例如：

```json
PUT _ingest/pipeline/timestamp
{
  "description" : "Adds a timestamp field at the current time",
  "processors" : [ {
    "set" : {
      "field": "timestamp",
      "value": "{{_ingest.timestamp}}"
    }
  } ]
}

PUT newindex/type/1?pipeline=timestamp
{
  "example": "data"
}

GET newindex/type/1
```

对于_ttl可以用time-based索引或者在一个时间戳字段范围查询(_delete-by-query)的任务来替换。

```json
POST index/type/_delete_by_query
{
  "query": {
    "range" : {
      "timestamp" : {
        "lt" : "2016-05-01"
      }
    }
  }
}
```
## 5、索引属性

所有再用的字段类型，除了将要废弃的string，索引属性只有 true/false用来代替not_analyzed/no，string字段类型还是analyzed/not_analyzed/no.

## 6、非索引字段的文档值

在此之前，设置一个字段的属性为index:no将禁用文档的值，现在，doc-values的值对数字和boolean类型的值总是有效，除非doc_values的值设置为false。

## 7、默认浮点类型的之用float来代替double 

在动态映射浮点类型的字段时，默认映射成float类型，而不是double类型，因为大多数情况下float类型已经够用了，而float类型将显著的减少磁盘空间的占用。

norms现在用boolean来代替对象，norms.enabled被替换成了boolean，norms.loading 参数eager 将不在起作用，现在norms是基于磁盘的.

设置fielddata.format: doc_values在用于隐式启用字段的文档映射中。现在隐式方式将不在起作用，需要明确的设置doc_values的值为有效或者无效。

fielddata.filter.regex参数将不在支持，未来版本会取消。

## 8、字段映射限制

在5.0中对索引中的字段进行了限制，最大1000个字段。

字段的最大深度（嵌套字段）是20。

索引中嵌套字段的最大数量是有限的50。

`_parent`字段将不再索引，连接父母与孩子之间的文件不再依赖索引字段，因此从5.0.0起_parent字段不再索引。为了找到文档引用一个特定的父id，可以使用新的parent_id来进行查询。搜索返回中的得到响应和hits仍然包括父键下的父标识。

`_source`映射不再支持格式选项，现在只是为了兼容性保留，为了会被去掉。

核心类型不再支持对象符号(bject notation)，它被用来提供每个文档的boosts ,例如：

```json
{
  "value": "field_value",
  "boost": 42
}
```

_all查询的精度

在_all上的每个字段的长度由以前的4个字节压缩到了一个字节，虽然这将使索引的空间效率更高，这也意味着索引时间的计算将不太准确。

转自：https://my.oschina.net/secisland/blog/790889
