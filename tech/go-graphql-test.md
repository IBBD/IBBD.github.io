# Go GraphQL Demo

测试项目地址：https://github.com/cyy0523xc/go-graphql-test

## 基本概念

### 根查询 RootQuery

```go
var rootQuery = graphql.NewObject(graphql.ObjectConfig{
	Name:        "RootQuery",
	Fields: graphql.Fields{
		"user":  userQuery,
		"users": usersQuery,

		"book":  bookQuery,
		"books": booksQuery,

		"comment":  commentQuery,
		"comments": commentsQuery,

		"hello": &graphql.Field{
			Type:        graphql.String,
			Description: "hello world",
			Resolve: func(params graphql.ResolveParams) (interface{}, error) {
				return "hello 中国人! ", nil
			},
		},
	},
})
```

其中Fields定义的是可以返回的字段，字段内容可以是简单内容，例如上面的hello，也可以是一个嵌套的查询，例如上面的user。

最简单的查询及返回：

```sh
curl -g 'http://localhost:8080/graphql?query={hello}'
{"data":{"hello":"hello 中国人! "}}
```

### 用户查询

对一个资源的查询，通常分为两种：

- 一种是查询单个item
- 另一种是查询多个item

命名可以注意，当个用户的查询为userQuery，多个用户的查询为usersQuery。

```
var userQuery = &graphql.Field{
	Type: userType,  // 单个用户
	Args: graphql.FieldConfigArgument{
		"id": &graphql.ArgumentConfig{
			Type: graphql.NewNonNull(graphql.Int), // id参数不允许为空
		},
	},
	Resolve: func(params graphql.ResolveParams) (interface{}, error) {
		idQuery := params.Args["id"].(int)
		id := uint32(idQuery)
		for _, user := range users {
			if user.Id == id {
				return user, nil
			}
		}

		return nil, errors.New("no user")
	},
}

var usersQuery = &graphql.Field{
	Type: graphql.NewList(userType), // 多个用户
	Args: graphql.FieldConfigArgument{
		"status": &graphql.ArgumentConfig{
			Type: graphql.Int,
		},
	},
	Resolve: func(params graphql.ResolveParams) (interface{}, error) {
		var resUsers = make([]User, 0)
		statusQuery, ok := params.Args["status"].(int)
		if ok {
			status := uint8(statusQuery)
			for _, user := range users {
				if user.Status == status {
					resUsers = append(resUsers, user)
				}
			}
			return resUsers, nil
		} else {
			return users, nil
		}

		return nil, errors.New("No user")
	},
}
```

每个查询有三个基本的参数：

- 输入参数：Args：可以定义每个输出参数的类型，是否为空等
- 输出格式：Type：可以定义为单个item或者列表
- 处理函数：Resolve：接收输入参数，实现业务逻辑，并生成满足输出格式的数据。


### 用户类型

上面已经定义了一个用户的查询，现在来定义用户类型：

```
var userType = graphql.NewObject(graphql.ObjectConfig{
	Name: "User",
	Fields: graphql.Fields{
		"id": &graphql.Field{
			Type: graphql.Int,
		},
		"name": &graphql.Field{
			Type: graphql.String,
		},
		"status": &graphql.Field{
			Type: graphql.Int,
		},

		// 直接关联书籍的查询
		// 怎么将这里的参数传递过去？
		"books": booksQuery,
	},
})
```

type定义的是输出格式，这里id,name,status,books都是输出的字段

其中books字段直接关联了书籍列表的查询，就这样，查询可以相互嵌套。

## Examples

### 查询单个用户

```sh
curl -g 'http://localhost:8080/graphql?query={user(id:1){id,name}}'
{"data":{"user":{"id":1,"name":"userA"}}}
```

### 查询用户列表

```sh
curl -g 'http://localhost:8080/graphql?query={users(status:1){id,name,status}}'
{"data":{"users":[{"id":1,"name":"userA","status":1},{"id":2,"name":"userB","status":1}]}}
```

### 嵌套查询

查询某个用户，并且将该用户关联的书名全部查询出来

```sh
curl -g 'http://localhost:8080/graphql?query={user(id:1){id,name,books(userId:1){name}}}'
{"data":{"user":{"books":[{"name":"bookA"},{"name":"bookB"},{"name":"bookC"}],"id":1,"name":"userA"}}}
```

问题：
- 如果在列表里，再嵌套查询，就会产生N+1次查询
- 查询参数里有`userId:1`，但是这个参数是重复传了，是否可以省略该参数？

#### 嵌套查询

例如上面的查询能否改成下面这样：

```sh
# books不需要指定userId，因为这是在嵌套里面
curl -g 'http://localhost:8080/graphql?query={user(id:1){id,name,books{name}}}'
```

事实上是可以的，`booksQuery`定义如下：

```go
var booksQuery = &graphql.Field{
	Type: graphql.NewList(bookType),
	Args: graphql.FieldConfigArgument{
		"userId": &graphql.ArgumentConfig{
			Type: graphql.Int,
		},
	},
	Resolve: func(params graphql.ResolveParams) (interface{}, error) {
		var res = make([]Book, 0)
		var userId uint32

		//fmt.Printf("%+v\n", params)
		fmt.Printf("--------------\n")
		if id, ok := params.Args["userId"].(int); ok {
			userId = uint32(id)
		} else if user, ok := params.Source.(User); ok {
			// 如果父级对象是user，则获取其user.Id
			userId = user.Id
		} else {
			return books, nil
		}

		for _, book := range books {
			if book.UserId == userId {
				res = append(res, book)
			}
		}

		return res, nil
	},
}
```

可以通过判断父级对象，获取对应的userId值。（这样是可以解决，但是这样并不完美）

#### N+1查询问题

下面这个查询就会产生N+1次查询，怎么优化？

```sh
curl -g 'http://localhost:8080/graphql?query={users{id,name,books{name}}}'
```



