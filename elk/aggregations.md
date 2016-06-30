# 使用ElasticSearch的Aggregations功能

## Aggregations的类型

### Bucketing: 桶

通过Bucketing聚合，可以将一个大的数据集，切分成若干小的数据集。在每一个切分好的小的数据集上可以继续聚合。
Bucketing聚合可以有子聚合，并且没有限制聚合的嵌套深度。

### Metric: 指标

在一个数据集上聚合运算，计算指标，例如计算均值等。
指标聚合通常可以分成两类：

1. 单一值指标聚合，例如avg等
2. 多值指标聚合，例如stats等

### Pipeline: 管道


## Aggregations的语法结构

```json
"aggregations" : {
    "<aggregation_name>" : {
        "<aggregation_type>" : {
            <aggregation_body>
        }
        [,"meta" : {  [<meta_data_body>] } ]?
        [,"aggregations" : { [<sub_aggregation>]+ } ]?
    }
    [,"<aggregation_name_2>" : { ... } ]*
}
```

`aggregations`通常简写成`aggs`，表示一个聚合组，下面可以有多个聚合，这里是管道的概念，先执行第一个聚合，再执行下一个聚合（如果有的话）。

## 指标聚合

### 基本指标计算：avg，max，min, value_count, sum: stats

如均值计算：

```json
{
    "aggs" : {
        "grade_avg" : {
            "avg" : {
                "field" : "grade",
                "missing": 10,
                "script" : {
                    "inline": "_value * correction",
                    "params" : {
                        "correction" : 1.2
                    }
                }
            }
        }
    }
}
```

说明：

1. missing属性是定义缺少字段的默认值.（count聚合不需要该属性）
2. scrpit脚本可以计算新值

这两个属性通常比较少用。

### 唯一值计算：Cardinality

例如从一堆用户的操作记录里面，计算独立用户数。注意：这里使用的是基数估计算法。

```json
{
    "aggs" : {
        "author_count" : {
            "cardinality" : {
                "field" : "author",
                "precision_threshold": 100 
            }
        }
    }
}
```

`precision_threshold`参数通常取值100，允许的最大值是40000。当唯一值小于该值时，统计是准确的，大于该值时就会出现一定的误差。当该值的设置为100或以上，误差是相当小的。

*注*: 在Kibana中，要提升唯一值的计算精度，可以设置该参数：

```json
{
    "precision_threshold": 40000
}
```

### 扩展统计聚合：Extended Stats

`extended_stats`聚合是`stats`聚合的扩展版，除了包含基础的统计值之外，还包括`sum_of_squares`, `variance`, `std_deviation` and `std_deviation_bounds`（包括`upper`, `lower`）.

```json
{
    ...

    "aggregations": {
        "grade_stats": {
           "count": 9,
           "min": 72,
           "max": 99,
           "avg": 86,
           "sum": 774,
           "sum_of_squares": 67028,
           "variance": 51.55555555555556,
           "std_deviation": 7.180219742846005,
           "std_deviation_bounds": {
              "upper": 100.36043948569201,
              "lower": 71.63956051430799
           }
        }
    }
}
```

#### 标准偏差范围：Standard Deviation Bounds

可以使用`sigma`参数，例如：

```json
"extended_stats" : {
    "field" : "grade",
    "sigma" : 3 
}
```

### 其他聚合

- `geo_bounds`：能计算出包含所有geo_point值的一个矩阵范围。
- `geo_centroid`：计算geo_point值的中心位置坐标。
- `percentiles`：计算百分位值
- `percentile_ranks`：等级的百分位值
- `top_hits`：

Scripted指标: 可以使用script来增加相应的指标。


## Bucket聚合

### 直方图聚合：Histogram

例如对价格区间进行汇总统计：

```json
{
    "aggs" : {
        "prices" : {
            "histogram" : {
                "field" : "price",
                "interval" : 50
            }
        }
    }
}
```

注：
- `min_doc_count`属性来限制结果集，过滤掉文档数小于该值的bucket。
- `order`: 可以对bucket进行排序

### 范围聚合：Range

```json
{
    "aggs" : {
        "price_ranges" : {
            "range" : {
                "field" : "price",
                "ranges" : [
                    { "to" : 50 },
                    { "from" : 50, "to" : 100 },
                    { "from" : 100 }
                ]
            }
        }
    }
}
```

注：

- 每一个bucket可以指定`key`，例如对价格来说，可以定义：cheat，average, expensive
- 可以使用`script`属性，对值进行相应的处理

### 日期直方图聚合：Date Histogram
 
例如按照月份聚合数据：

```json
{
    "aggs" : {
        "articles_over_time" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "month"
            }
        }
    }
}
```

可选的步长单位有：year, quarter, month, week, day, hour, minute, second

### 日期区间聚合：Date Range 

```json
{
    "aggs": {
        "range": {
            "date_range": {
                "field": "date",
                "format": "MM-yyy",
                "ranges": [
                    { "to": "now-10M/M" }, 
                    { "from": "now-10M/M" } 
                ]
            }
        }
    }
}
```

### 过滤器及过滤器组：Filter and Filters 

```json
{
    "aggs" : {
        "red_products" : {
            "filter" : { "term": { "color": "red" } },
            "aggs" : {
                "avg_price" : { "avg" : { "field" : "price" } }
            }
        }
    }
}
```

```json
{
  "aggs" : {
    "messages" : {
      "filters" : {
        "filters" : {
          "errors" :   { "term" : { "body" : "error"   }},
          "warnings" : { "term" : { "body" : "warning" }}
        }
      },
      "aggs" : {
        "monthly" : {
          "histogram" : {
            "field" : "timestamp",
            "interval" : "1M"
          }
        }
      }
    }
  }
}
```

### 嵌套聚合

例如，计算嵌套文档中的最小价格：

```json
{
    "aggs" : {
        "resellers" : {
            "nested" : {
                "path" : "resellers"
            },
            "aggs" : {
                "min_price" : { "min" : { "field" : "resellers.price" } }
            }
        }
    }
}
```

#### 反转嵌套聚合：Reverce Nested

例如一个issue中包含一个tag和多个评论，每个评论有包含用户名和评论内容。这时需要计算TOP5的评论用户（评论最多），并且得出用户经常使用的tag。

```json
{
  "aggs": {
    "comments": {
      "nested": {
        "path": "comments"
      },
      "aggs": {
        "top_usernames": {
          "terms": {
            "field": "comments.username"
          },
          "aggs": {
            "comment_to_issue": {
              "reverse_nested": {}, 
              "aggs": {
                "top_tags_per_comment": {
                  "terms": {
                    "field": "tags"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

说明：

- `reverse_nested`必须包含在`nested`之中。
- `reverse_nested`能返回文档的不同嵌套深度（通过path指定），当没有指定path属性时，就是回到root层。

### Terms聚合

对字段的不同值进行聚合。

```json
{
    "aggs" : {
        "products" : {
            "terms" : {
                "field" : "product",
                "size" : 5
            }
        }
    }
}
```

假设整个index保存在3个shards（分片）里，计算的时候实际计算的时候会分别在每个shard计算TOP5，然后做合并。所以，最后计算得到的文档数并不一定就是全局最优值。
为了得到更加精确的值，可以使用`shard_size`属性，给它设置一个比较大的值，在每个shard计算得到比较多的值，这样最后合并的时候，就可能得到更好的值，但是这样也意味着更大的计算量。

注：
如果在kibana中，可以在json input输入如下内容：

```json
{
    "shard_size": 10000
}
```

### 显著关键词聚合：Significant Terms

你可以在比如欺诈检测、异常检测、推荐等各方面使用关键词。[介绍文章](https://www.elastic.co/blog/significant-terms-aggregation)

Terms聚合能对数据做汇总，例如对文章做Terms聚合，就能将分词后的词的汇总展示出来。例如对于一堆文章的分词统计得到“中国”这个词出现了5次，Terms聚合也就做到这里而已。但是这个5次是多还是少，这个无法给出判断，因为没有参照和对比，也就是无法判断这个词是否显著。而`significant_terms`就能做这事。

#### 单数据集分析：Single-set analysis

```json
{
    "query" : {
        "terms" : {"force" : [ "British Transport Police" ]}
    },
    "aggregations" : {
        "significantCrimeTypes" : {
            "significant_terms" : { "field" : "crime_type" }
        }
    }
}
```

响应信息：

```json
{
    ...

    "aggregations" : {
        "significantCrimeTypes" : {
            "doc_count": 47347,
            "buckets" : [
                {
                    "key": "Bicycle theft",
                    "doc_count": 3640,
                    "score": 0.371235374214817,
                    "bg_count": 66799
                }
                ...
            ]
        }
    }
}
```

说明：
总体的自行车盗窃占比只有1% (66799/5064554)，但是在British Transport Police这个警局，占比却达到了7%（3640/47347）！这是非常显著的！

### 多数据集分析

```json
{
    "aggregations": {
        "forces": {
            "terms": {"field": "force"},
            "aggregations": {
                "significantCrimeTypes": {
                    "significant_terms": {"field": "crime_type"}
                }
            }
        }
    }
}
```

响应信息：

```json
{
 ...

 "aggregations": {
    "forces": {
        "buckets": [
            {
                "key": "Metropolitan Police Service",
                "doc_count": 894038,
                "significantCrimeTypes": {
                    "doc_count": 894038,
                    "buckets": [
                        {
                            "key": "Robbery",
                            "doc_count": 27617,
                            "score": 0.0599,
                            "bg_count": 53182
                        },
                        ...
                    ]
                }
            },
            {
                "key": "British Transport Police",
                "doc_count": 47347,
                "significantCrimeTypes": {
                    "doc_count": 47347,
                    "buckets": [
                        {
                            "key": "Bicycle theft",
                            "doc_count": 3640,
                            "score": 0.371,
                            "bg_count": 66799
                        },
                        ...
                    ]
                }
            }
        ]
    }
}
```

这样就能得到各个警局的显著的案件类型。


### 其他聚合

- 缺失值聚合：Missing, 不存在某个字段的文档
- Geo距离聚合：Geo Distance 
- Geo网格聚合：Geo Grid
- IPv4聚合
- Sampler





