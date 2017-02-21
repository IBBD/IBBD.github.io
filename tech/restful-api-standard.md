# IBBD Restful API 规范

## 基础规范

- 基于Laravel的RESTful规范 http://laravelacademy.org/post/60.html#ipt_kb_toc_60_6 ，我们只使用get, post, put, delete

### 1，每个响应头部都包含协议的具体版本信息

```
 X-DSP-Version: v1.2.2.1
```

### 2，每个需要验证的请求头部都包含如下验证信息

```
 X-DSP-Token: token_value_of_successful_login
```

### ~~3，每个请求头部都包含协议的大版本号~~

- 基于各种情况，取消了API版本化，详情参考[这里](http://www.infoq.com/cn/news/2016/07/web-api-versioning/)
- 服务端只会维护一个版本，版本升级向后兼容，响应头中的版本信息仅用于提示客户端当前API版本，具体的变更可以参考发布日志，例如 https://hostname.com/release.md
- Restful服务的变迁后让原有的业务正常工作肯定是需要工作量，关键在于这个工作量由谁来承担。如果由服务提供者承担，那么他们需要保证接口的向后兼容性，而不是随意改变URI；如果由服务的用户承担，那么他们需要迁移代码以适应新的接口。作为服务提供者，服务就像自己的产品，当然应该是自己多做些，客户少做些来的好！


### 4，HTTP状态码表及说明

http status code | message                  | method     | usage
----             | ------                   | ------     | --------                     
200              | OK                       | get        | 查询数据
201              | CREATED                  | post,patch | 添加或修改数据成功
204              | NO CONTENT               | delete     | 删除数据成功
400              | INVALID REQUEST          | post,patch | 添加或修改数据时参数错误
401              | Unauthorized             | all        | 权限校验失败
403              | Forbidden                | all        | 请求被禁止
404              | NOT FOUND                | all        | 请求的资源不存在
405              | Method Not Allowed       | all        | 请求方法不存在
406              | Not Acceptable           | get        | 请求的格式无法提供
408              | Request Timeout          | all        | 请求超时
409              | Conflict                 | post,patch | 添加或修改数据时参数值冲突
413              | Request Entity Too Large | post,patch | 一般文件上传时数据较大
414              | Request-URI Too Long     | all        | URL过长
415              | Unsupported Media Type   | post       | 一般文件上传时数据类型不支持
500              | Internal Server Error    | all        | 服务出现异常

### 5，返回值格式

```
{
    error: {
        code: "",
        msg: ""
    }

    data: <data object or data array>
}
```

### 6，错误状态码code说明

- httpCode为200，201，400，409时body中有数据返回，其他状态码body中均无数据
- 产生错误时code值为具体的字段，msg值为错误详情，data为空，否则表示请求成功
- httpCode为200，201，400时，code值为field，则表示field参数值错误
- httpCode为409时，code值为field，则表示field参数值重复


## Query

### 请求方式：GET

### URL格式：

```
http://hostname.com/{prefix}/{resource}?query={"offset":0,"limit":20,"sort":{"field":"asc"},"fields":["field"],"search":{"fields":[],"value":""},"where":{"filed":{"operator":"value"}}}
```

参数     | 类型        | 默认值 | 备注
----     | ----        | ----   | ----
resource | string      |        | 要访问的实体
query    | json string |        | 查询参数
offset   | uint        | 0      | 记录起始位置，>=0，
limit    | uint        | 20     | 返回记录数目，>=0，值为0时表示取起始位置后的所有数据
sort     | json string |        | 返回记录排序，field排序的字段，由具体的API定义，asc与desc字段排序的方向
fields   | json string |        | 返回字段，默认返回所有字段，由具体的API定义
search   | json string |        | 模糊查询匹配的字段,fields需要匹配的字段，由具体的API定义，search_value模糊匹配的值
where    | json string |        | 搜素条件，filed搜素字段，由具体的API定义，value字段的值，operator运算符，

注：

- 1、url前面部分遵循restful规范，例如：

```
http://hostname.com/{prefix}/{resource}
http://hostname.com/{prefix}/{resource}/{id}
http://hostname.com/{prefix}/{resource}/{id}/{resource2}
```
- 2、operator运算符有

Name | Description
---- | -----
eq   | Matches values that are equal to a specified value.
gt   | Matches values that are greater than a specified value.
gte  | Matches values that are greater than or equal to a specified value.
lt   | Matches values that are less than a specified value.
lte  | Matches values that are less than or equal to a specified value.
ne   | Matches all values that are not equal to a specified value.
in   | Matches any of the values specified in an array.
nin  | Matches none of the values specified in an array.


### 一个完整的例子

```
https://hostname.com/admin/media?query=$query_value 
```

$query_value如下

```json
{
    "offset":0,
    "limit":20,
    "sort":{
        "id":"asc",
        "name":"desc"
    },
    "fields":["id","name","position","size"],
    "where":{
        "id":{"gt":10},
        "name":{"like":"zhangsan"},
        "updated_at":{
            "gt":"2016-12-16 16:42:23",   //操作符仅支持gt,lt,gte,lte
            "lt":"2016-12-16 16:42:23"
        }
    },
    "search":{
        "fields":["name","id"],
        "value":"adview"
    }
}
```

请求参数

| 参数   | 类型   | 说明               | 范围及格式
| ---    | ---    | ---                | ---
| sort   | string | 指定排序参数       | 排序参数可选：id,recommend
| fields | string | 返回参数           | 可选项参考返回例子中的参数
| where  | string | 查询条件           | 可选参数：id,channel_id,recommend,name
| search | string | 查询条件，模糊查询 | 可选参数：name

返回结果

```json
{
    "error": {
        "code":"",
        "msg": ""
    },
    "total":1,
    "data" :[
        {
            "id": 1,
            "channel_id": 1,
            "recommend" :100,
            "channel_name": "adview",
            "name": "搜狐视频",
            "position": "首页/时尚/财经/科技/汽车信息流",
            "size": "150*150,690*345",
            "price":12.9,
            "updated_at":"2016-12-16 16:42:23"
        }
    ]
}
```

## Create

### 请求方法：POST

### 请求数据：JSON

### URL格式：

```
http://hostname.com/{prefix}/{resource}
```

### 一个完整的例子

```
https://hostname.com/admin/media
```

```json
{
    "channel_id": 1,
    "name": "搜狐视频",
    "position": "首页/时尚/财经/科技/汽车信息流",
    "size": "150*150,690*345",
    "price":12.9
}
```

请求参数

| 参数       | 类型   | 说明       | 范围及格式
| ---        | ---    | ---        | ---
| channel_id | int    | 渠道ID\*   | >1
| name       | string | 名称\*     |
| position   | string | 位置\*     |
| size       | string | 尺寸\*     |
| price      | int    | 建议出价\* | >0

返回结果

```json
{
    "error": {
        "code":"",
        "msg": ""
    },
    "data" : {
        "id": 1,
        "channel_id": 1,
        "recommend" :100,
        "channel_name": "adview",
        "name": "搜狐视频",
        "position": "首页/时尚/财经/科技/汽车信息流",
        "size": "150*150,690*345",
        "price": 12.9,
        "created_at": "2016-12-16 16:42:23",
        "updated_at": "2016-12-16 16:42:23"
    }
}
```

## Update

### 请求方法：PATCH

### 请求数据：JSON

### URL格式：

```
http://hostname.com/{prefix}/{resource}/{id}
```

### 一个完整的例子

```
https://hostname.com/admin/media/1
```

```json
{
    "channel_id": 1,
    "recommend": 100,
    "name": "搜狐视频",
    "position": "首页/时尚/财经/科技/汽车信息流",
    "size": "150*150,690*345",
    "price": 12.9
}
```

请求参数

| 参数       | 类型   | 说明     | 范围及格式
| ---        | ---    | ---      | ---
| channel_id | int    | 渠道ID   | >1
| recommend  | int    | 排序     | >=1
| name       | string | 名称     |
| position   | string | 位置     |
| size       | string | 尺寸     |
| price      | int    | 建议出价 | >0

返回结果

```json
{
    "error": {
        "code":"",
        "msg": ""
    },
    "data" : {
        "id": 1,
        "channel_id": 1,
        "recommend" :100,
        "channel_name": "adview",
        "name": "搜狐视频",
        "position": "首页/时尚/财经/科技/汽车信息流",
        "size": "150*150,690*345",
        "price":12.9,
        "created_at":"2016-12-16 16:42:23",
        "updated_at":"2016-12-16 16:42:23"
    }
}
```


## Delete

### 请求方法：DELETE

### URL格式：

```
http://hostname.com/{prefix}/{resource}/{id}
```

### 一个完整的例子

```
https://hostname.com/admin/media/1
```
