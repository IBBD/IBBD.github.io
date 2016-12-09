# IBBD Restful API 规范

## 基础规范

- 基于Laravel的RESTful规范 http://laravelacademy.org/post/60.html#ipt_kb_toc_60_6 ，我们只使用get, post, put, delete

## HTTP状态码

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

// 使用操作符
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

#### fields

对应sql语句中的select部分，如：`SELECT {fieldNameList} FROM ...`

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





