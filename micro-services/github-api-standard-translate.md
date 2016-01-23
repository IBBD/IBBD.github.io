# github api规范文档翻译

源文档：https://developer.github.com/v3/

## 目录

1. 当前版本
2. 概要（Schema）
3. 参数
4. 根节点（Root Endpoint）
5. 错误返回
6. HTTP重定向
7. HTTP动词（HTTP Verbs）
8. 权限
9. 超媒体（Hypermedia）
10. 分页
11. 请求限速（Rate Limiting）
12. 必须的User Agent（User Agent Required）
13. 不是必须的头信息（Conditional requests）
14. 跨域资源共享（Cross Origin Resource Sharing）
15. JSON-P回调
16. 时区

## 当前版本

默认情况下，所有API请求都必须包含`v3`这个版本号，推荐把这个版本信息包含在`Accept`头信息里，如下：

```
Accept: application/vnd.github.v3+json
```

## 概要

- 所有API请求使用`HTTPS`
- 所有的数据交互都使用`JSON`格式

```
curl -i https://api.github.com/users/octocat/orgs

HTTP/1.1 200 OK
Server: nginx
Date: Fri, 12 Oct 2012 23:33:14 GMT
Content-Type: application/json; charset=utf-8
Connection: keep-alive
Status: 200 OK
ETag: "a00049ba79152d03380c34652f2cb612"
X-GitHub-Media-Type: github.v3
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1350085394
Content-Length: 5
Cache-Control: max-age=0, private, must-revalidate
X-Content-Type-Options: nosniff
```

- 空白的字段使用`null`，而不是省略。
- 所有的时间戳在返回时使用`ISO 8601`的格式，`YYYY-MM-DDTHH:MM:SSZ`

### 概要信息接口（Summary Representations）

当你请求一个资源的列表时，返回值会包含对应的属性集合。这些是资源的概要信息，而有一些属性是比较复杂的，所以这些信息并不会在列表接口返回。要获取这些属性，需要使用`详细`信息接口。

例如：当需要获取一个代码库的列表时，你得到每个代码库的概要信息。如下：

```
GET /orgs/octokit/repos
```

### 详细信息接口（Detailed Representations）

当获取某个具体的单个资源时，接口会返回该资源的所有属性，这就是详细信息接口。（注意，授权信息有时会影响详细接口的返回值。）

例如：

```
GET /repos/octokit/octokit.rb
```

## 参数

很多API的方法都可以带有可选的参数，例如GET方法，任何不作为路径一部分的参数，都可以用作HTTP的查询字符串参数：

```
curl -i "https://api.github.com/repos/vmg/redcarpet/issues?state=closed"
```

在这个例子中，vmg和redcarpet这两个是参数`:owner`和`:repo`的值，同时`:state`的值也在查询字符串里。

对于 POST，PATCH，PUT 和 DELETE 这些请求，参数不止能包含在URL里，还能包含在JSON字符串里面（`Content-Type`的值为`application/json`）

```
curl -i -u username -d '{"scopes":["public_repo"]}' \
    https://api.github.com/authorizations
```

## 根节点（Root Endpoint）

通过GET方法请求根节点，你能获取所有支持的接口类型：

```
curl https://api.github.com
```

## 客户端的错误信息

在接口的返回值里，有三种类型的错误信息：

- 第一种：发送不合法的JSON文档，将会得到一个`400 Bad Request`响应。

```
HTTP/1.1 400 Bad Request
Content-Length: 35

{"message":"Problems parsing JSON"}
```

- 第二种：发送错误的JSON值的类型，也会得到`400 Bad Request`的响应。

```
HTTP/1.1 400 Bad Request
Content-Length: 40

{"message":"Body should be a JSON object"}
```

- 第三种：发送错误的字段，将会得到`422 Unprocessable Entity`的响应。

```
HTTP/1.1 422 Unprocessable Entity
Content-Length: 149

{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "Issue",
      "field": "title",
      "code": "missing_field"
    }
  ]
}
```

除了上面的错误信息，还会有一些错误代码，以方便客户端定位问题：


Error Name     | Description
---------      | --------------
missing        | 资源不存在
missing_field  | 请求的字段不存在
invalid        | 字段的格式不对。可以查看资源的文档，以定位问题。
already_exists | 字段值已经存在，这个通常发生在唯一键上面。

此外，也会有一些自定义的验证错误（对应的`code=custom`），这种错误通常会有一个`message`字段的描述信息，还有`documentation_url`字段帮助你解决问题。

## HTTP重定向

在需要的时候，v3版API会使用HTTP重定向，这时客户端不要把它当作错误来处理。

HTTP状态值 | 描述
------     | ------
301        | 永久重定向。你请求的URI已经被新的URI所取代，你应该直接请求的新的URI。
302,307    | 临时重定向。

其他的重定向状态值的使用和`HTTP 1.1 spec`一致。

## HTTP动词（HTTP Verbs）

v3版API的每个action会尽量保持和HTTP动作（verbs）一致。

Verb   | 描述
----   | -----
head   |
get    | 查询
post   | 创建
patch  | 更新，请求的时候可以在`body`带上部分的JSON数据。
put    | 替换。这个方式的请求不能待`body`属性，所以请求头的`Content-Length`必须为0
delete | 删除

## 权限

在一些接口，请求需要授权的接口会得到`404 Not Found`的信息（正常情况是`403 Forbidden`）。在第三版API中，有三种方式的授权方式，将有效防止未授权用户对私有资料的访问。

### 基本授权方式（Basic Authentication）

```
curl -u "username" https://api.github.com
```

### OAuth2 Token (sent in a header)

```
curl -H "Authorization: token OAUTH-TOKEN" https://api.github.com
```

### OAuth2 Token (sent as a parameter)

```
curl https://api.github.com/?access_token=OAUTH-TOKEN
```

### OAuth2 Key/Secret

```
curl 'https://api.github.com/users/whatever?client_id=xxxx&client_secret=yyyy'
```

这种方式只允许用在服务器之间的通信上, 注意不要泄露你的秘钥。更多关于未授权的访问限制看[这里](https://developer.github.com/v3/#increasing-the-unauthenticated-rate-limit-for-oauth-applications)

### 错误的登陆限制

使用错误的信息进行登陆时，会得到`401 Unauthorized`的响应：

```
curl -i https://api.github.com -u foo:bar
HTTP/1.1 401 Unauthorized

{
  "message": "Bad credentials",
  "documentation_url": "https://developer.github.com/v3"
}
```

如果短时间内，被拒绝了几次，API将会拒绝这个用户所有的授权认证。这时会得到`403 Forbidden`的响应：

```
curl -i https://api.github.com -u valid_username:valid_password
HTTP/1.1 403 Forbidden

{
  "message": "Maximum number of login attempts exceeded. Please try again later.",
  "documentation_url": "https://developer.github.com/v3"
}
```

## 超媒体（Hypermedia）


## 分页

分页的格式如下：

```
curl 'https://api.github.com/user/repos?page=2&per_page=100'
```

注意：页码是从1开始的，如果省略了page参数，则默认为1.

### Link Header


## 请求限速（Rate Limiting）

对于授权（Basic Authentication or OAuth）了的请求，每小时上限为5000. 而对于没有授权的请求，每小时只能60次。

你可以从任何API请求的返回的头信息里看到关于限速的信息：

```
curl -i https://api.github.com/users/whatever
HTTP/1.1 200 OK
Date: Mon, 01 Jul 2013 17:27:06 GMT
Status: 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 56
X-RateLimit-Reset: 1372700873
```

下面是对这三个附加字段的解释：

Header Name           | 描述
--------              | --------
X-RateLimit-Limit     | 每小时的上限值
X-RateLimit-Remaining | 当前限制窗口剩余的次数
X-RateLimit-Reset     | 时间窗口的重设时间（UTC epoch seconds）

一旦你超过的访问次数，则会得到错误的响应信息：

```
HTTP/1.1 403 Forbidden
Date: Tue, 20 Aug 2013 14:50:41 GMT
Status: 403 Forbidden
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1377013266

{
   "message": "API rate limit exceeded for xxx.xxx.xxx.xxx. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)",
   "documentation_url": "https://developer.github.com/v3/#rate-limiting"
}
```

## 必须的User Agent

所有的API请求都必须包含一个合法的`User-Agent`头信息，否则将会被拒绝。作为`User-Agent`的值，我们要求你使用Github的用户名，或者你的应用名，以方便我们能够联系到你（如果有问题）。

这是一个样例：

```
User-Agent: Awesome-Octocat-App
```

如果你提供了一个非法的`User-Agent`值，将会得到`403 Forbidden`：

```
curl -iH 'User-Agent: ' https://api.github.com/meta
HTTP/1.0 403 Forbidden
Connection: close
Content-Type: text/html

Request forbidden by administrative rules.
Please make sure your request has a User-Agent header.
Check https://developer.github.com for other possible causes.curl -iH 'User-Agent: '
```

## 可选的请求参数

大部分请求的返回头都会包含`ETag`和`Last-Modified`这两个属性。根据这些值，在发起请求时你可以使用`If-None-Match`和`If-Modified-Since`这两个属性。如果资源没有改变，服务器将直接返回`304 Not Modified`，这时将不计算Rate Limit。

```
curl -i https://api.github.com/user
HTTP/1.1 200 OK
Cache-Control: private, max-age=60
ETag: "644b5b0155e6404a9cc4bd9d8b1ae730"
Last-Modified: Thu, 05 Jul 2012 15:31:30 GMT
Status: 200 OK
Vary: Accept, Authorization, Cookie
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4996
X-RateLimit-Reset: 1372700873

curl -i https://api.github.com/user -H 'If-None-Match: "644b5b0155e6404a9cc4bd9d8b1ae730"'
HTTP/1.1 304 Not Modified
Cache-Control: private, max-age=60
ETag: "644b5b0155e6404a9cc4bd9d8b1ae730"
Last-Modified: Thu, 05 Jul 2012 15:31:30 GMT
Status: 304 Not Modified
Vary: Accept, Authorization, Cookie
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4996
X-RateLimit-Reset: 1372700873

curl -i https://api.github.com/user -H "If-Modified-Since: Thu, 05 Jul 2012 15:31:30 GMT"
HTTP/1.1 304 Not Modified
Cache-Control: private, max-age=60
Last-Modified: Thu, 05 Jul 2012 15:31:30 GMT
Status: 304 Not Modified
Vary: Accept, Authorization, Cookie
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4996
X-RateLimit-Reset: 1372700873
```

## 跨域资源共享

接口支持从任何地方发起的AJAX请求（CORS），这是两份扩展阅读文档：[CORS W3C Recommendation](http://www.w3.org/TR/cors/) 和 [this intro](http://code.google.com/p/html5security/wiki/CrossOriginRequestSecurity). 例如：

```
curl -i https://api.github.com -H "Origin: http://example.com"
HTTP/1.1 302 Found
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: ETag, Link, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval
Access-Control-Allow-Credentials: true
```

一个CORS的请求例如这样：

```
curl -i https://api.github.com -H "Origin: http://example.com" -X OPTIONS
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, X-GitHub-OTP, X-Requested-With
Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE
Access-Control-Expose-Headers: ETag, Link, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
```

## JSON-P回调函数

在任何的GET请求中，你都可以使用`?callback`参数，输出结果时，会使用回调函数名进行包装。这是一种典型的应用，当我们想通过嵌入Github进行跨域时。





