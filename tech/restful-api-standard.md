# IBBD Restful API 规范

## 基础规范

- 基于Laravel的RESTful规范 http://laravelacademy.org/post/60.html#ipt_kb_toc_60_6 ，我们只使用get, post, put, delete

### 1，每个响应头部都包含如下版本号信息

```
 X-DSP-Version: v3
```

### 2，每个需要验证的请求头部都包含如下验证信息

```
 Authorization: token_value_of_successful_login
```

### 3，每个请求头部都包含如下版本号信息

```
 X-DSP-Version: v3
```

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

## 返回值格式

```
{
    error: {
        type: "",
        msg: ""
    }

    data: <data object or data array>
}
```

## Query

```
http://host/{prefix}/{databaseName}/{tableName}?fields={fieldNameList}query={jsonData}&sort={jsonData}&skip={skip}&limit={limit}&groupby={fieldNameList}
```

参数    | 类型        | 是否允许不传 | 默认值 | 备注
----    | ----        | ----         | ----   | ----
query   | json string | 是           |        | 查询参数，见详细说明
fields  | string      | 是           |        | 查询字段，默认返回所有字段
sort    | json string | 是           |        | 排序参数，见详细说明
offset  | uint        | 是           | 0      | 跳过前面若干条
limit   | uint        | 是           | 20     | 返回多少条记录
groupby | string      | 是           |        | 对应sql中的group by

注：

url前面部分遵循restful规范，例如：

```
http://host/{prefix}/{databaseName}/{tableName}
http://host/{prefix}/{databaseName}/{tableName}/{id}
http://host/{prefix}/{databaseName}/{tableName}/{id}/{tableName2}
```

### 参数详细说明

#### query

参考mongodb的find方法中的query参数，见相关文档：

- https://docs.mongodb.com/manual/crud/#read-operations
- https://docs.mongodb.com/manual/reference/method/db.collection.find/#db.collection.find
- https://docs.mongodb.com/manual/reference/operator/query/
- https://docs.mongodb.com/manual/tutorial/query-documents/

mongo的查询操作符比较多，我们最多只考虑实现比较操作符即可。

Example：

```
// 最简单的查询
{fildName1: val1, fieldName2: val2}

// 使用模糊匹配关键词
// $like是模糊匹配的操作符，如: hello% （匹配hello开头的字符串）
{fildName1: val1, fieldName2: {$like: "hello%"}}

// 使用操作符
// 注：这部分功能用得不多，可以后期需要时再实现
{fieldName1: val1, fieldName2: {$gt: 10, $lte: 100}}
```

比较操作符如下：

Name | Description
---- | -----
$eq  | Matches values that are equal to a specified value.
$gt  | Matches values that are greater than a specified value.
$gte | Matches values that are greater than or equal to a specified value.
$lt  | Matches values that are less than a specified value.
$lte | Matches values that are less than or equal to a specified value.
$ne  | Matches all values that are not equal to a specified value.
$in  | Matches any of the values specified in an array.
$nin | Matches none of the values specified in an array.

模糊匹配操作符：`$like`

#### fields

对应sql语句中的select部分，如：`SELECT {fieldNameList} FROM ...`。example：

```
// 返回两个字段
field1,field2

// 返回的字段使用了函数
// sum和count是sql中最基本的函数，通常和group by一起出现
field1,sum(field2) as sum_field2
field1,count(field2) as count_field2
```

#### sort

对应sql中的order by部分，参数格式使用mongodb的表示形式：

```
{fieldName1: 1, fieldName2: -1}

// 等价于sql：

ORDER BY fieldName1 ASC, fieldName2 DESC
```

#### offset and limit

分页参数，对应sql中的limit

#### groupby

对应sql的group by，如果多个字段，则用逗号分隔

### 查询返回值


## Create

## Update

## Delete





