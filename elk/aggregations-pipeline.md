# Elasticsearch的Aggregations聚合之Pipeline

- By cyy0523xc@gmail.com

## 介绍

Pipeline聚合是工作在别的Agg之上，而不是在文档集合之上，给原有的输出增加新的输出信息。Pipeline聚合的类型：

- Parent：
- Sibling：

### buckets_path属性

大多数的pipeline需要其他的agg作为输入，而这些输入的agg就被定义在`buckets_path`属性中，语法如下：

```
AGG_SEPARATOR       :=  '>'
METRIC_SEPARATOR    :=  '.'
AGG_NAME            :=  <the name of the aggregation>
METRIC              :=  <the name of the metric (in case of multi-value metrics aggregation)>
PATH                :=  <AGG_NAME>[<AGG_SEPARATOR><AGG_NAME>]*[<METRIC_SEPARATOR><METRIC>]
```

例如："my_bucket>my_stats.avg"将会关联到定义在my_bucket中的my_stats的avg这个指标。

## 均值Pipeline

```json
{
    "aggs" : {
        "sales_per_month" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "month"
            },
            "aggs": {
                "sales": {
                    "sum": {
                        "field": "price"
                    }
                }
            }
        },
        "avg_monthly_sales": {
            "avg_bucket": {
                "buckets_path": "sales_per_month>sales" 
            }
        }
    }
}
```

结果例如：

```json
{
   "aggregations": {
      "sales_per_month": {
         "buckets": [
            {
               "key_as_string": "2015/01/01 00:00:00",
               "key": 1420070400000,
               "doc_count": 3,
               "sales": {
                  "value": 550
               }
            },
            ...
         ]
      },
      "avg_monthly_sales": {
          "value": 328.33333333333333
      }
   }
}
```

类似均值的还有：

- max_bucket
- min_bucket
- sum_bucket
- stats_bucket
- extended_stats_bucket
- percentiles_bucket

## 累积求和

```json
{
    "aggs" : {
        "sales_per_month" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "month"
            },
            "aggs": {
                "sales": {
                    "sum": {
                        "field": "price"
                    }
                },
                "cumulative_sales": {
                    "cumulative_sum": {
                        "buckets_path": "sales" 
                    }
                }
            }
        }
    }
}
```

响应值：

```json
{
   "aggregations": {
      "sales_per_month": {
         "buckets": [
            {
               "key_as_string": "2015/01/01 00:00:00",
               "key": 1420070400000,
               "doc_count": 3,
               "sales": {
                  "value": 550
               },
               "cumulative_sales": {
                  "value": 550
               }
            },
            {
               "key_as_string": "2015/02/01 00:00:00",
               "key": 1422748800000,
               "doc_count": 2,
               "sales": {
                  "value": 60
               },
               "cumulative_sales": {
                  "value": 610
               }
            },
            {
               "key_as_string": "2015/03/01 00:00:00",
               "key": 1425168000000,
               "doc_count": 2,
               "sales": {
                  "value": 375
               },
               "cumulative_sales": {
                  "value": 985
               }
            }
         ]
      }
   }
}
```


## 移动平均聚合：Moving Average

对于给定的数据`[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`，假设窗口值为5，则移动平均结果如下：

```
(1 + 2 + 3 + 4 + 5) / 5 = 3
(2 + 3 + 4 + 5 + 6) / 5 = 4
(3 + 4 + 5 + 6 + 7) / 5 = 5
etc
```

语法如下：

```json
{
    "moving_avg": {
        "buckets_path": "the_sum",
        "window": 5,
        "gap_policy": "insert_zero",
        "model": "holt",
        "settings": {
            "alpha": 0.8
        }
    }
}
```

### Models

移动平均可以使用不同的计算模型, 不同的model可能会有不同的参数，可以在settings参数中设置：

#### simple模型

就是使用窗口内的值的和除于窗口值，通常窗口值越大，最后的结果越平滑: `(a1 + a2 + ... + an) / n`

#### 线性模型：Linear

对窗口内的值先做线性变换处理，再求平均：`(a1 * 1 + a2 * 2 + ... + an * n) / (1 + 2 + ... + n)`

#### 指数模型：EWMA (Exponentially Weighted)

EWMA模型通常也成为单指数模型（single-exponential）, 和线性模型的思路类似，离当前点越远的点，重要性越低，具体化为数值的指数下降，对应的参数是`alpha`。
`alpha`值越小，下降越慢。（估计是用`1 - alpha`去计算的）默认的`alpha=0.3`

计算模型：`s2 = α * x2 + (1 - α) * s1`

其中α是平滑系数，si是之前i个数据的平滑值，取值为[0,1]，α越接近1，平滑后的值越接近当前时间的数据值，数据越不平滑，α越接近0，平滑后的值越接近前i个数据的平滑值，数据越平滑，α的值通常可以多尝试几次以达到最佳效果。
一次指数平滑算法进行预测的公式为：xi+h=si，其中i为当前最后的一个数据记录的坐标，亦即预测的时间序列为一条直线，不能反映时间序列的趋势和季节性。

#### 二次指数平滑模型: Holt-Linear

计算模型：

```
s2 = α * x2 + (1 - α) * (s1 + t1)
t2 = ß * (s2 - s1) + (1 - ß) * t1
```

默认`alpha = 0.3 and beta = 0.1`

二次指数平滑保留了趋势的信息，使得预测的时间序列可以包含之前数据的趋势。二次指数平滑的预测公式为  xi+h=si+hti  二次指数平滑的预测结果是一条斜的直线。

#### 三次指数平滑模型：Holt-Winters无季节模型

三次指数平滑在二次指数平滑的基础上保留了季节性的信息，使得其可以预测带有季节性的时间序列。三次指数平滑添加了一个新的参数p来表示平滑后的趋势。


#### Additive Holt-Winters：Holt-Winters加法模型

下面是累加的三次指数平滑

```
si=α(xi-pi-k)+(1-α)(si-1+ti-1)
ti=ß(si-si-1)+(1-ß)ti-1
pi=γ(xi-si)+(1-γ)pi-k  其中k为周期
```

累加三次指数平滑的预测公式为： `xi+h=si+hti+pi-k+(h mod k)`

#### Multiplicative Holt-Winters：Holt-Winters乘法模型

下式为累乘的三次指数平滑：

```
si=αxi/pi-k+(1-α)(si-1+ti-1)
ti=ß(si-si-1)+(1-ß)ti-1
pi=γxi/si+(1-γ)pi-k  其中k为周期
```

累乘三次指数平滑的预测公式为： `xi+h=(si+hti)pi-k+(h mod k)`

α，ß，γ的值都位于[0,1]之间，可以多试验几次以达到最佳效果。

s,t,p初始值的选取对于算法整体的影响不是特别大，通常的取值为s0=x0,t0=x1-x0,累加时p=0,累乘时p=1.


### 预测模型：Prediction

上面提到的所有平滑模型都可以支持一个预测模型，可以设置`prediction`参数。

## 导数：Derivative

使用当前值减去前一个值，其实就是环比增长。

### 一阶导数

```json
{
    "aggs" : {
        "sales_per_month" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "month"
            },
            "aggs": {
                "sales": {
                    "sum": {
                        "field": "price"
                    }
                },
                "sales_deriv": {
                    "derivative": {
                        "buckets_path": "sales" 
                    }
                }
            }
        }
    }
}
```

```json
{
   "aggregations": {
      "sales_per_month": {
         "buckets": [
            {
               "key_as_string": "2015/01/01 00:00:00",
               "key": 1420070400000,
               "doc_count": 3,
               "sales": {
                  "value": 550
               } 
            },
            {
               "key_as_string": "2015/02/01 00:00:00",
               "key": 1422748800000,
               "doc_count": 2,
               "sales": {
                  "value": 60
               },
               "sales_deriv": {
                  "value": -490 
               }
            },
            {
               "key_as_string": "2015/03/01 00:00:00",
               "key": 1425168000000,
               "doc_count": 2, 
               "sales": {
                  "value": 375
               },
               "sales_deriv": {
                  "value": 315
               }
            }
         ]
      }
   }
}
```

### 二阶导数

对一阶导数再计算一次导数。

```json
{
    "aggs" : {
        "sales_per_month" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "month"
            },
            "aggs": {
                "sales": {
                    "sum": {
                        "field": "price"
                    }
                },
                "sales_deriv": {
                    "derivative": {
                        "buckets_path": "sales"
                    }
                },
                "sales_2nd_deriv": {
                    "derivative": {
                        "buckets_path": "sales_deriv" 
                    }
                }
            }
        }
    }
}
```


## 序列差分：Serial Differencing

计算模型`f(x) = f(xt) - f(xt-n)`，当周期n为1时，则是环比增长，大于1时为环比增长。

## Bucket Script

语法

```json
{
    "bucket_script": {
        "buckets_path": {
            "my_var1": "the_sum", 
            "my_var2": "the_value_count"
        },
        "script": "my_var1 / my_var2"
    }
}
```
### Bucket Selector

```json
{
    "bucket_selector": {
        "buckets_path": {
            "my_var1": "the_sum", 
            "my_var2": "the_value_count"
        },
        "script": "my_var1 > my_var2"
    }
}
```

只选择满足条件的Bucket




