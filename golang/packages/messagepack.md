# [Golang]MessagePack包的使用：序列化与反序列化

在序列化算法中，MessagePack是最常用的之一，大多数语言都能支持。序列化的效率及存储空间都有相当的优势。

我们选用的包这个，文件见：
https://github.com/tinylib/msgp/wiki/Getting-Started

## 使用

1.建立数据结构, `vim data.go`：

```go
package main

type Foo struct {
	Bar string  `msg:"a"` // 注意：使用a来做标签能减少序列化后的长度
	Baz float64 `msg:"b"`
}

//go:generate msgp
```

注意代码最后的`//go:generate msgp`，这就是用来生成相应代码的。

2.执行命令`go generate`，生成`data_gen.go`和`data_gen_test.go`文件

可以查看生成的文件，看看里面有什么。

3.运行测试`go test -v -bench .`

可以看到性能报告。

4.使用：`vim main.go`

```go
package main

import (
	"fmt"
)

func main() {
	foo1 := Foo{Bar: "hello", Baz: 10.3}

	fmt.Printf("foo1: %v\n", foo1)

	// Here, we append two messages
	// to the same slice.
	data, _ := foo1.MarshalMsg(nil)

	// at this point, len(data) should be 0
	fmt.Println("len(data) =", len(data))

	// Now we'll just decode them
	// in reverse:
	data, _ = foo1.UnmarshalMsg(data)

	fmt.Printf("foo1: %v", foo1)
}
```

5.测试：`go build`，然后执行生成的可执行文件。

注意：不能直接运行`go run main.go`


