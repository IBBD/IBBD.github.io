# Dgraph最短路径查询
以下基于Dgraph v0.7.7

查找任意两个节点之间的最短路径，这是一种常见的需求，Dgraph也能实现这种查询。准备数据如下：

```sh
curl localhost:8080/query -XPOST -d $'
mutation{
set {
 <a> <friend> <b> (weight=0.1) .
 <b> <friend> <c> (weight=0.2) .
 <c> <friend> <d> (weight=0.3) .
 <a> <friend> <d> (weight=1) .
 <a> <name> "alice" .
 <b> <name> "bob" .
 <c> <name> "Tom" .
 <d> <name> "Mallory" .
 }
}' | python -m json.tool
```

## 查询两个节点之间的最短路径

```sh
curl localhost:8080/query -XPOST -d $'{
 path as shortest(from:a, to:d) {
  friend
 }
 path(id: var(path)) {
   name
 }
}' | python -m json.tool
```

显然这两点之间的最短距离是a是d的朋友。返回格式如下：

```
{
    "_path_": [
        {
            "_uid_": "0xb3454265b6df75e3",
            "friend": [
                {
                    "_uid_": "0x3e0ae463957d9a21"
                }
            ]
        }
    ],
    "path": [
        {
            "name": "alice"
        },
        {
            "name": "Mallory"
        }
    ]
}
```

## 查询两个节点之间的带权重的最短路径
上面的查询没有考虑到权重，所以直接出来a->d这个朋友关系，但是如果考虑权重因素呢？查询如下：

```sh
curl localhost:8080/query -XPOST -d $'{
 path as shortest(from:a, to:d) {
  friend @facets(weight)
 }

 path(id: var(path)) {
  name
 }
}' | python -m json.tool
```

显然，从a到d有两条路径：

- a->d: 这条路径权重为1
- a->b->c->d: 这条路径看起来比较长，但是权重之和：0.1+0.2+0.3 = 0.6

所以这时的返回结果应该是第二条路径。格式如下：

```
{
    "_path_": [
        {
            "_uid_": "0xb3454265b6df75e3",
            "friend": [
                {
                    "_uid_": "0xa3b260215ec8f116",
                    "friend": [
                        {
                            "_uid_": "0x9ea118a9e0cb7b28",
                            "friend": [
                                {
                                    "_uid_": "0x3e0ae463957d9a21"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "path": [
        {
            "name": "alice"
        },
        {
            "name": "bob"
        },
        {
            "name": "Tom"
        },
        {
            "name": "Mallory"
        }
    ]
}
```

## 查询多种关系下的最短路径
修改一下数据：

```sh
curl localhost:8080/query -XPOST -d $'
mutation{
set {
 <a> <friend> <b> (weight=0.1) .
 <a> <friend> <c> (weight=0.1) .
 <b> <friend> <d> (weight=0.2) .
 <c> <colleague> <d> (weight=0.3) .
 <a> <name> "alice" .
 <b> <name> "bob" .
 <c> <name> "Tom" .
 <d> <name> "Mallory" .
 }
}' | python -m json.tool
```

如果我们要查询a到d之间的最短路径，而不管其中经过了什么关系，我们最直接想到的查询如下：


```sh
curl localhost:8080/query -XPOST -d $'{
 path as shortest(from:a, to:d) {
  friend
  colleague
 }
 path(id: var(path)) {
   name
 }
}' | python -m json.tool
```

这时的返回值是：

```
{
    "_path_": [
        {
            "_uid_": "0xb3454265b6df75e3",
            "friend": [
                {
                    "_uid_": "0x9ea118a9e0cb7b28",
                    "colleague": [
                        {
                            "_uid_": "0x3e0ae463957d9a21"
                        }
                    ]
                }
            ]
        }
    ],
    "path": [
        {
            "name": "alice"
        },
        {
            "name": "Tom"
        },
        {
            "name": "Mallory"
        }
    ]
}
```

显然给出的路径是：a->c->d。或许我们还想，如果关系很多，能不能使用通配符，将所有关系都查找出来，不过这貌似是不支持的。

## 查找满足某种特殊条件的最短路径
上面我们已经可以查询到不同关系下的最短路径，但是这个结果可能并不是我们所需要的，例如我们不想看到包含`Tom`的路径，其查询语句如下：

```sh
curl localhost:8080/query -XPOST -d $'{
  path as shortest(from: a, to: d) {
    friend @filter(not anyofterms(name, "Tom"))
    colleague
  }
  path(id: var(path)) {
    name
  }
}' | python -m json.tool
```

如果得到的信息是`Attribute name is not indexed.`，这说明name关系上还没有索引。先建里索引：

```sh
curl localhost:8080/query -XPOST -d $'
mutation {
  schema {
    name: string @index .
  }
}' | python -m json.tool
```

重复前一个查询语句，出来结果如下：

```
{
    "_path_": [
        {
            "_uid_": "0xb3454265b6df75e3",
            "friend": [
                {
                    "_uid_": "0xa3b260215ec8f116",
                    "friend": [
                        {
                            "_uid_": "0x3e0ae463957d9a21"
                        }
                    ]
                }
            ]
        }
    ],
    "path": [
        {
            "name": "alice"
        },
        {
            "name": "bob"
        },
        {
            "name": "Mallory"
        }
    ]
}
```

如果我们希望直接查询关系中包含`bob`的，貌似不行。

