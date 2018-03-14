# API设计规范

## 一、规范说明
### 1、HTTP协议基础
#### 1）、HTTP Status Code (服务器响应回的状态码)

| 状态                                | 说明                                 |
| ------------                        | ------------                         |
| 100 Continue                        |                                      |
| 101 Switching Protocols             |                                      |
| 200 OK                              | 查询数据                             |
| 201 Created                         | 添加或修改数据成功                   |
| 202 Accepted                        |                                      |
| 203 Non-Authoritative Information   |                                      |
| 204 No Content                      | 删除数据成功                         |
| 205 Reset Content                   |                                      |
| 206 Partial Content                 |                                      |
| 300 Multiple Choices                |                                      |
| 301 Moved Permanently               |                                      |
| 302 Found                           |                                      |
| 303 See Other                       |                                      |
| 304 Not Modified                    |                                      |
| 305 Use Proxy                       |                                      |
| 307 Temporary Redirect              |                                      |
| 400 Bad Request                     | 添加或修改数据时参数错误             |
| 401 Unauthorized                    | 认证失败即登陆失败                   |
| 402 Payment Required                |                                      |
| 403 Forbidden                       | 拒绝服务，权限不足、资源正在使用等等 |
| 404 Not Found                       | 请求的资源不存在                     |
| 405 Method Not Allowed              | 请求方法不存在                       |
| 406 Not Acceptable                  | 请求的格式无法提供                   |
| 407 Proxy Authentication Required   |                                      |
| 408 Request Timeout                 | 请求超时                             |
| 409 Conflict                        | 添加或修改数据时参数值冲突           |
| 410 Gone                            |                                      |
| 411 Length Required                 |                                      |
| 412 Precondition Failed             |                                      |
| 413 Request Entity Too Large        | 一般文件上传时数据较大               |
| 414 Request-URI Too Long            | URL过长                              |
| 415 Unsupported Media Type          | 一般文件上传时数据类型不支持         |
| 416 Requested Range Not Satisfiable |                                      |
| 417 Expectation Failed              |                                      |
| 500 Internal Server Error           | 服务出现异常                         |
| 501 Not Implemented                 |                                      |
| 502 Bad Gateway                     |                                      |
| 503 Service Unavailable             |                                      |
| 504 Gateway Timeout                 |                                      |
| 505 HTTP Version Not Supported      | 版本不支持                           |

#### 2）、 HTTP Method （HTTP1.1）（向服务器发出请求的方法）

| 名称             | 说明                                             |
| ------------     | ------------                                     |
| GET（SELECT）    | 从服务器取出资源（一项或多项）。
| POST（CREATE）   | 在服务器新建一个资源。
| PUT（UPDATE）    | 在服务器更新资源（客户端提供改变后的完整资源）。
| PATCH（UPDATE）  | 在服务器更新资源（客户端提供改变的属性）。
| DELETE（DELETE） | 从服务器删除资源。
| HEAD             | 获取资源的元数据。
| OPTIONS          | 获取信息，关于资源的哪些属性是客户端可以改变的。

#### 3）、 Content-Type （要发送内容的类型以及编码）
```
Content-Type: text/html; charset=utf-8
Content-Type: application/json; charset=utf-8
Content-Type: multipart/form-data; boundary=something
```
| 名称                              | 说明                    |
| ------------                      | ------------            |
| application/x-www-form-urlencoded | get方式或传统的form表单
| application/json                  | 较为流行的json
| multipart/form-data               | 上传文件文件
| text/plain                        | 文本
| text/css                          | 文本
| text/html                         | 文本
| application/xml                   | xml文本
| text/xml                          | 文本
| application/javascript            | js文本
| text/javascript                   | 文本

### 2、API的一些约定
#### 1）、 版本号的问题

- 服务端只会维护一个版本，版本升级向前兼容；这里有一个很好的[理由](http://www.infoq.com/cn/news/2016/07/web-api-versioning/)
- 响应头中会带有当前API版本，具体的变更可以参考发布日志，例如https://hostname.com/release.md；
- RESTful服务的变迁后让原有的业务正常工作肯定是需要工作量，关键在于这个工作量由谁来承担。如果由服务提供者承担，那么他们需要保证接口的向后兼容性，而不是随意改变URI；如果由服务的用户承担，那么他们需要迁移代码以适应新的接口。作为服务提供者，服务就像自己的产品，当然应该是自己多做些，客户少做些来的好！

#### 2）、 自定义头部信息
- 以X-开头，各词之间用-分割
- X-API-Version表示当前API版本号，每次更新都会更改
- X-Auth-Token表示登陆后的会话凭证

```
 X-API-Version: v1.2.2.1
 X-Auth-Token: 5eb63bbbe01eeed093cb22bb8f5acdc3
```
#### 3）、 请求与返回格式

- 仅文件上传接口会用multipart/form-data
- 推荐使用application/json
- 返回结果均为json,固定的返回格式如下

```json
{
// 自定义的业务错误状态码
"code":0,
// 错误的具体提示
"msg":"",
// 错误的参数
"field":"",
// 返回的结果，例如查询接口返回的对象集合
"data":[{"name":"zhangsan","age":18}],
// 返回数据的数目
"total":1
}
```

每个应用根据具体情况具体定义，以下例子仅供参考

| 自定义状态码 | 用途场景                                     |
| ------------ | ------------                                 |
| 0            | 请求成功处理                                 |
| 4001         | 缺少参数                                     |
| 4002         | 多了参数                                     |
| 40031        | 参数值类型错误（int,float,string）           |
| 40032        | 参数值格式错误（email，url, phone, address） |
| 40033        | 参数值范围错误，不在指定范围内               |
| 4011         | 缺少X-Auth-Token                             |
| 4012         | X-Auth-Token值错误，用户不在线               |
| 4031         | 权限不足                                     |
| 4032         | 资源不满足删除条件，比如有子集               |
| 5001         | 未知错误                                     |
| 5002         | 数据库服务不可用                             |
| 5003         | 缓存服务不可用                               |
| 5004         | 邮件服务不可用                               |
| 5005         | 短信服务不可用                               |

#### 4）、RESTful规范应该遵循的一些原则
- URL中用的是名词复数，url是指向资源的，而不是描述行为的
- GET和HEAD方法必须始终是安全的，搜索引擎可能会访问了它
- URL是区分小写的，建议全部小写，多个词之间用-，因为浏览器中超链接显示的默认效果是，文字并附带下划线，这样会影响阅读
- 注意domain.com/users 与 domain.com/users/ 是不一样的

```
http://hostname.com/{prefix}/{resource}
http://hostname.com/{prefix}/{resource}/{id}
http://hostname.com/{prefix}/{resource}/{id}/{resource2}
```

## 二、一个完整的例子

#### 1.1、资源user的属性

| 名称         | 类型         | 范围/格式           | 说明         |
| ------------ | ------------ | ------------        | ------------ |
| id           | int          | >1                  | 用户系统标识 |
| name         | string       | 32>len>3            | 用户昵称     |
| created_at   | datatime     | 2018-03-03 12:34:56 | 创建时间     |

#### 1.2、查询符合条件的用户（版本1）
- Method：GET
- Auth：YES
- URL：http://hostname.com/{prefix}/users?offset=0&limit=20&order=asc&by=id
- Content-Type：application/x-www-form-urlencoded
- parameters：

| 名称         | 类型         | 范围/格式       | 说明                                    |
| ------------ | ------------ | ------------    | ------------                            |
| offset       | int          | total>offset>=0 | 从第几条开始去数据，默认从0开始         |
| limit        | int          | >=0             | 取回多少条数据，默认10条，0取回所有数据 |
| order        | enum         | asc、dsc        | 正序或倒序                              |
| by           | enum         | id              | 来自于user的属性                        |

其他查询条件自定义

- response （200）

请求成功

```json
{
	"code":0,
	"msg":"",
	"field":"",
	"data":[
		{"id":1,"name":"zhangsan","created_at":"2018-01-01 12:23:23"}
		{"id":2,"name":"李四","created_at":"2018-01-01 12:23:23"}
	],
	"total":2
}
```

请求失败

```json
{
	"code":40033,
	"msg":"order的值不在指定范围",
	"field":"order",
	"data":[],
	"total":0
}
```

#### 1.2、查询符合条件的用户（版本2）

参数query固定格式说明如下，参数query可以省略，其值为json，需要进行urlencode

```json
{
	//记录起始位置，>=0，可以省略，默认取0
	"offset":0,
	//返回记录数目，>=0，值为0时表示取起始位置后的所有数据，可以省略，默认取10
	"limit":20,
	//返回记录排序，由具体的API定义，asc与desc字段排序的方向，字段来自于fields，可以省略，默认不排序
	"sort":{"id": "asc","name": "desc"},
	//返回字段，由具体的API定义，可以省略，默认取该资源所有属性
	"fields":["id","name","created_at"],
	//模糊查询匹配的字段，fields需要匹配的字段，由具体的API定义，value模糊匹配的值
	//%表示任意匹配，例子是查询name值以hello开头的数据，可以省略，默认不进行模糊查询
	"search":{"fields": ["name"],"value": "hello%"}
	//过滤条件，可以省略，默认不进行筛选
	"where":{
		//可用查询字段由具体的API定义,多个字段之间是and关系
		"id":{"gt": 10},
		//查询字段值为对象,其中键名是运算符,键值是该字段可取的正常值
		"created_at": {"gt": "2016-12-16 16:42:23","lt": "2016-12-16 16:42:23"}
	}
}
```

查询中的operator运算符说明

| 名称         | 说明                                                                |
| ------------ | ------------                                                        |
| eq           | Matches values that are equal to a specified value.                 |
| gt           | Matches values that are greater than a specified value.             |
| gte          | Matches values that are greater than or equal to a specified value. |
| lt           | Matches values that are less than a specified value.                |
| lte          | Matches values that are less than or equal to a specified value.    |
| ne           | Matches all values that are not equal to a specified value.         |
| in           | Matches any of the values specified in an array.                    |
| nin          | Matches none of the values specified in an array.                   |

- Method：GET
- Auth：YES
- URL：http://hostname.com/{prefix}/users?query={"offset":0,"limit":20,"sort":{"id":"asc"},"fields":["id","name","created_at"]}
- Content-Type：application/x-www-form-urlencoded
- parameters：

| 名称         | 可取属性           |
| ------------ | ------------       |
| fields       | id,name,created_at |
| sort         | id                 |
| search       | name               |
| where        | id,name,created_at |

- response （200）

请求成功

```json
{
	"code":0,
	"msg":"",
	"field":"",
	"data":[
		{"id":1,"name":"zhangsan","created_at":"2018-01-01 12:23:23"}
		{"id":2,"name":"李四","created_at":"2018-01-01 12:23:23"}
	],
	"total":2
}
```

请求失败

```json
{
	"code":40032,
	"msg":"where的值错误",
	"field":"where",
	"data":[],
	"total":0
}
```

#### 1.3、添加一个用户
- Method：POST
- Auth：YES
- URL：http://hostname.com/{prefix}/users
- Content-Type：application/json
- parameters：

```json
{
	"name":"赵六"
}
```

| 名称         | 是否必须     | 默认值       |
| ------------ | ------------ | ------------ |
| name         | Y            | 无           |

- response （200）

请求成功

```json
{
	"code":0,
	"msg":"",
	"field":"",
	"data":[
		{"id":1,"name":"lisi","created_at":"2018-01-01 12:23:23"}
	],
	"total":1
}
```

#### 1.4、 修改一个用户
- Method：PATCH
- Auth：YES
- URL：http://hostname.com/{prefix}/users/1
- Content-Type：application/json
- parameters：

```json
{
	"name":"赵六"
}
```

| 名称         | 是否必须     | 默认值       |
| ------------ | ------------ | ------------ |
| name         | N            | 原值         |

- response （200）

请求成功

```json
{
	"code":0,
	"msg":"",
	"field":"",
	"data":[
		{"id":1,"name":"赵六","created_at":"2018-01-01 12:23:23"}
	],
	"total":1
}
```

#### 1.5、 删除一个用户
- Method：DELETE
- Auth：YES
- URL：http://hostname.com/{prefix}/users/1
- parameters：无
- response （200）

请求成功

```json
{
	"code":0,
	"msg":"删除成功",
	"field":"",
	"data":[],
	"total":1
}
```
