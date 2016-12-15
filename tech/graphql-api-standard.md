# IBBD GraphQL API 规范文档

- 官网：http://graphql.org/
- API IDE：https://github.com/graphql/graphiql
- PHP版实现：https://github.com/Folkloreatelier/laravel-graphql

## GraphQL基本规范

GraphQL是API的UI。

- 类型系统（服务器端）描述有什么数据，客户端决定获取什么数据。
- 不需要版本号的概念，接口可以方便的实现前后的版本兼容。对不需要的参数，可以标注为`deprecated`，并且可以注明原因。
- GraphQL可以自解释，API文档大大的减少，并且有一个强大的开发工具`Graphiql`。因此字段定义中的描述字段也是比较重要的，对应名字通常是`description`。
- 可以通过组合的形式，将大量的数据集合到一次请求里。这样的确是减少了请求数，但是不建议这样，一次请求应该包含一个单一的目的。
- GraphQL查询可以不断的嵌套和组合，提供了极大的灵活性，但是这样也会导致请求过于复杂，难以维护。适当的时候，可以使用数据库层面的视图功能，简化查询，简化逻辑。例如不同的用户角色如果需要访问不同的数据，那就可以通过不同的视图来提供。

## 类型系统
类型系统是GraphQL最基础也最重要的部分。

- 内置类型
  - 基础标量类型（scalar）：`ID`, `String`, `Int`, `Float`, `Boolean`
  - 两个内置修饰类型：`ListOf` and `NonNull`
- 枚举类型：可以用于状态等类型字段的定义
- 接口类型：接口用于描述多个类型的通用字段，例如一个表示实体数据结构的 GraphQL 接口为：

```javascript
const EntityType = new GraphQLInterfaceType({
  name: 'Entity',
  fields: {
    name: { type: GraphQLString }
  }
});
```

- Object类型：

用于描述层级或者树形数据结构。对于树形数据结构来说，叶子字段的类型都是标量数据类型。几乎所有 GraphQL 类型都是对象类型。Object 类型有一个 name 字段，以及一个很重要的 fields 字段。fields 字段可以描述出一个完整的数据结构。例如一个表示地址数据结构的 GraphQL 对象为：

```javascript
const AddressType = new GraphQLObjectType({
  name: 'Address',
  fields: {
    street: { type: GraphQLString },
    number: { type: GraphQLInt },
    formatted: {
      type: GraphQLString,
      resolve(obj) {
        return obj.number + ' ' + obj.street
      }
    }
  }
});
```

- 联合类型：（在我们选择的php库中尚未实现，暂时不管）
- 字段（Field）类型：

## 模式Schema
当定义好所有类型之后，就要开始定义模式。模式有两个特别的根类型组成：`query`和`mutation`，例子见：https://github.com/webonyx/graphql-php/blob/master/tests/StarWarsSchema.php 

设计的思路是：`先设计好类型系统，再设计模式`。

## 查询语言
查询语言的开发原则是：

- 一次查询只实现一个单一目标。
- 尽量避免使用片段，指令之类的高级特性。
- 使用POST提交数据
- 参数与查询语句分离

下面还会有例子说明这几点。

## 权限

http头信息：

```
Authorization: token_value_of_successful_login
```

权限验证应该在中间件处理完成，尽量避免在业务逻辑中掺杂着权限校验的逻辑。

权限通常分为几个层面：

- 接口层面的权限: 有些接只有管理员才有权限访问。
- 记录层面的权限: 例如用户只能访问自己账户相关的记录，而管理员可以访问所有记录。

经过权限的中间件检验时，能否注入参数？例如统一注入`loginId`参数。

注入参数的方式如下（php实现）：

- 通过配置文件，指定controller为自己实现
- 在自己实现的controller里，就可以注入了
- 权限判断也要实现在自己实现的controller里
- 注入的参数需要先在每个类型的args参数里注入`loginId`等参数（注意在控制器需要避免该参数从接口传入）。 具体做法类似下面的`offset`, `limit`等参数。

具体实现参照：https://github.com/Folkloreatelier/laravel-graphql/blob/master/src/Folklore/GraphQL/GraphQLController.php

## 异常数据返回

错误类型可以自己定义，具体实现可以指定配置文件的`error_formatter`配置项。

## 数据交换样式

样例如下

```sh
curl -g 'http://host/graphql' -d 'params={"id":1}&query=
query getUserList($id:Int){
    users(id:$id){
        id,
        name,
        email,
        friends{
            id,
            name
        }
    }
}
'
```

参数与查询语句的好处是，能将参数转化为我们熟悉的json进行操作，而且对应的query语句也能统一配置。

参数统一通过post的方式传递，分为两部分：

### json参数

参数名`params`，json结构，其中公共的参数名如下：

参数    | 类型   | 是否允许不传 | 默认值   | 说明
---     | -----  | -------      | ------   | -------
offset  | uint   | 是           | 0        | 获取列表时
limit   | uint   | 是           | 0        | 获取列表时，0表示不限
sort    | string | 是           | 空字符串 | 获取列表时，可以同时按多个字段排序，格式如`field1,-field2`，`-`表示倒序，对应sql：`field1 ASC, field2 DESC`
groupby | string | 是           | 空字符串 | 获取列表时，可以同时按多个字段groupby，如`field1,field2`，对应sql：`GROUP BY field1, field2`

这些参数采取统一注入到args的定义里，避免每次都需要重新定义：

```php
// 原来的参数定义
public function args()
{
    return [
        'id' => ['name' => 'id', 'type' => Type::string()],
        'email' => ['name' => 'email', 'type' => Type::string()]
    ];
}

// 可以定义一个参数类
class ControllerArgs 
{
    public static function get(array $args, $default_offset=0, $default_limit=0, $use_sort=false, $use_groupby=false) 
    {
        $args["offset"] = ['name' => 'offset', 'type' => Type::int()];
        $args["limit"] = ['name' => 'offset', 'type' => Type::int()];

        // sort, groupby参数类似
        return $args;
    }
}

// 这里需要修改为
public function args()
{
    $resArgs = [
        'id' => ['name' => 'id', 'type' => Type::string()],
        'email' => ['name' => 'email', 'type' => Type::string()]
    ];
    return ControllerArgs::get($resArgs)
}
```

另外：`可以统一注入loginId`等参数，并且避免外部传入该值。

### 查询语句

以文本的方式post，参数以变量的形式通过`params`传递，应该避免在语句中写入了参数。这样语句就可以统一写在配置文件里。

## 避免N+1查询问题

javascript版本官方有`dataloader`的实现，但是没有其他语言，所以在使用的时候，还得注意。例如sql语句：

```sql
SELECT b.name, u.name AS userName FROM book b
LEFT JOIN user u ON(b.userId = u.id)
WHERE 1
LIMIT 10
```

这是非常常见的查询，但是在graphql中可能就会产生N+1次查询，如果我们定义类型系统如下：

```go
type User {
    id: uint
    name: string
}

type Book {
    id: uint
    name: string
    user: User
}
```

这是查询语句为：

```
books(limit:10){
    name
    user{ name }
}
```

这时，如果实现没有做特殊的处理，就会产生N+1次查询，因为对于每个Book都会对应的查询User一次！

在php中的解决方式见：https://github.com/Folkloreatelier/laravel-graphql/blob/master/docs/advanced.md#eager-loading-relationships （关于with的用法，具体看这里：http://laravelacademy.org/post/140.html#ipt_kb_toc_140_9 ）

## 善用枚举类型
设计数据库或者接口的时候，经常会碰到状态类型的字段（枚举不止可以用于状态字段），程序如果设计比较合理的话，会用常量替换相应的数值（避免硬编码），增加可读性。但是这样还是不够，因为我们通常是前后端分离的，前后端都必须有一个常量定义，而且往往很难做统一。

在GraphQL中使用枚举类型就很适合了。看例子：

```go
// 这里使用golang
// php其实也是类似的

// 用户状态常量定义
const (
	UserStatusNormal uint8 = 0
	UserStatusMoney  uint8 = 1
	UserStatusHigh   uint8 = 2
)

// 接口中的用户类型定义
var userStatusType = graphql.NewEnum(graphql.EnumConfig{
	Name: "UserStatus",
	Values: graphql.EnumValueConfigMap{
		// 普通用户
		"NORMAL": &graphql.EnumValueConfig{
			Value: UserStatusNormal,
		},
		// 付费用户
		"MONEY": &graphql.EnumValueConfig{
			Value: UserStatusMoney,
		},
		// 高级用户
		"HIGH": &graphql.EnumValueConfig{
			Value: UserStatusHigh,
		},
	},
})

var userType = graphql.NewObject(graphql.ObjectConfig{
	Name: "User",
	Fields: graphql.Fields{
		// 这里省略了其他字段
		"status": &graphql.Field{
			Type: userStatusType, // 枚举类型
		},
	},
})

var usersQuery = &graphql.Field{
	Type: graphql.NewList(userType),
	Args: graphql.FieldConfigArgument{
		"status": &graphql.ArgumentConfig{
			Type:         userStatusType,  // 用户状态枚举类型
			DefaultValue: 0,
		},
	},
	Resolve: func(params graphql.ResolveParams) (interface{}, error) { },
}
```

下面看看使用效果：

```sh
# 注意status参数的类型是UserStatus
curl -g 'http://localhost:8080/graphql' -d 'query=query+getList($status:UserStatus){users(status:$status){id,name,status}}&params={"status":"NORMAL"}'

# 返回结果：
{"data":{"users":[{"id":3,"name":"userC","status":"NORMAL"}]}}
```

这样前端使用的时候，就可以直接使用`NORMAL`，不再是没有直观意义的数值，可读性会大大提升。

## Create a mutation
通常的写法是这样：

```
mutation users {
    updateUserPassword(id: "1", password: "newpassword") {
        id
        email
    }
}
```

但是这样生成字符串不方便，使用变量的形式，并将参数统一放到post的body中，如：

```
curl -g "http://homestead.app/graphql" -d 'query=mutation+users($id:Int,$password:String){updateUserPassword(id:$id, password:$password){id,email}}&params={id:"1", password:"newpassword"}'
```

同样，对于update的请求也是一样的处理。

## 自解析
写接口的时候，通常还需要写相应的接口文档，这不仅累赘，增加了维护的负担，而且文档本身的理解也经常达不到各方的一致（例如前端，后端，测试等）。

```go
// 定义
var userType = graphql.NewObject(graphql.ObjectConfig{
	Name:        "User",
	Description: "用户类型",
	Fields: graphql.Fields{
		"id": &graphql.Field{
			Type:        graphql.Int,
			Description: "用户ID",  // 字段注释
		},
		"name": &graphql.Field{
			Type:        graphql.String,
			Description: "用户名",
		},
		"status": &graphql.Field{
			Type:        userStatusType,
			Description: "用户状态",
		},
	},
})

// 查询
// 使用：__type
curl -g 'http://localhost:8080/graphql' -d 'query={__type(name:"User"){name,description,fields{name,description,type{name}}}}'

// 返回值
{
  "data": {
    "__type": {
      "name": "User",
      "description": "用户类型",
      "fields": [
        {
          "description": "用户名",
          "name": "name",
          "type": {
            "name": "String"
          }
        },
        {
          "description": "用户状态",
          "name": "status",
          "type": {
            "name": "UserStatus"
          }
        },
        {
          "description": "用户ID",
          "name": "id",
          "type": {
            "name": "Int"
          }
        }
      ]
    }
  }
}
```

相关文档：https://facebook.github.io/graphql/?spm=5176.100239.blogcont8183.18.i5VDOY#sec-Introspection

## 相关文档阅读

- 深入理解 GraphQL https://yq.aliyun.com/articles/8183
