# ElasticSearch中的Mapping配置

Mapping是用来约束一个文档的字段，以及文档是怎么被被索引的。
以下是一个简单的mapping文件：

```json
{
    "properties": {
        "month": {
            "type": "date",
            "format": "yyyyMM"
        },
        "imsi": {
            "type": "string",
            "index": "not_analyzed"
        },
        "msg_cnt": {
            "type": "integer"
        },
        "location": {
            "type": "geo_point"
        },
        "ip_addr": {
            "type": "ip"
        },
        "name": { 
            "properties": {
                "first": { "type": "string" },
                "last":  { "type": "string" }
            }
        },
        "proposer": {
            "type": "nested",
            "properties": {
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
}
```

## Mapping Types

每一个index都有一个或者多个mapping types，这些types将一个index的文档分配到逻辑组里。例如，在一个博客系统中，用户相关的信息可以保存在`user` type中，而文章相关的信息则保存在`blogpost` type中。

每一个mapping包含以下信息：

- 元字段（Meta fields）：用来定义文档中元数据的处理方式，也就是mapping的基本信息，例如`_index`, `_type`, `_id`, `_source`等字段。
- 字段（properties）：每个type都会包含一个或者多个字段。例如一个用户type可能包含title, name, age等字段。

## 字段的数据类型

- 简单类型： string, date, long, double, boolean or ip.
    - date：可以通过format属性来定义输入的日期格式，也可以定义多个格式，例如`yyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis`
    - boolean：注意这些值都会被设置为false：`false, "false", "off", "no", "0", "" (empty string), 0, 0.0`
    - ip：实际上会转化为long类型进行存储，因此可以像整数一样进行比较等操作
- 内嵌JSON类型：`object`和`nested`
    - object：不需要定义type属性，只需要定义`properties`属性即可
    - nested：该字段是一个数组，数组的每个元素都是一个对象，可以定义`properties`属性
- 特殊类型：geo_point, geo_shape, or completion

## 特别注意事项

1. 对于一个已经存在的mapping的index，是不允许被更新的，你应该新建一个index，并重新索引。
2. 在一个index内部，相同的字段名（即使是在不同的type内）是共享的，所以必须采用相同的属性。
3. 在mongoDB上，相同的字段名允许使用不同的字段类型，但是在es中是不允许的。


