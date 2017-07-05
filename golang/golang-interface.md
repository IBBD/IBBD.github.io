# Golang interface的一个特性
今天在看`github.com/go-sql-driver/mysql`的源码时, 看到interface比较特别的一种用法, 以前自己没有用过的, 特此记录:

```go
package main

import (
	"errors"
	"log"
    "fmt"
	"os"
)

// Logger is used to log critical error messages.
type Logger interface {
	Print(v ...interface{})
}

var errLog = Logger(log.New(os.Stderr, "[debug] ", log.Ldate|log.Ltime|log.Lshortfile))

func main() {
	tmp := log.New(os.Stderr, "[debug] ", log.Ldate|log.Ltime|log.Lshortfile)
	tmp.Print("hello world")
	errLog.Print("hello world")
	tmp.Print(errors.New("Error hello"))
	errLog.Print(errors.New("Error hello"))
    fmt.Printf("%T ==> %T", tmp, errLog)
}
```

这段程序输出如下:

```
[debug] 2017/07/05 22:31:09 err_log.go:18: hello world
[debug] 2017/07/05 22:31:09 err_log.go:19: hello world
[debug] 2017/07/05 22:31:09 err_log.go:20: Error hello
[debug] 2017/07/05 22:31:09 err_log.go:21: Error hello
*log.Logger ==> *log.Logger
```

可见其中的tmp.Print和errLog.Print的作用完全是一样的.

比较不理解的其实是下面一句：

```go
var errLog = Logger(log.New(os.Stderr, "[debug] ", log.Ldate|log.Ltime|log.Lshortfile))
```

这里的Logger明明是一个结构体，却能像函数一样调用。查看了官方的说明：https://golang.org/doc/effective_go.html#interfaces 

从结果上理解，是将一个log.Logger对象转化成了Logger对象, 类似类型转换。但是输出类型来看，两者的类型完全是一样的，所以并非类型转换。

那这里应该是怎么理解，查看官方文档貌似没有提到过这点。


## 嵌入interface
看文件container/heap/heap.go，有源码：

```go
import "sort"

type Interface interface {
	sort.Interface
	Push(x interface{}) // add x as element Len()
	Pop() interface{}   // remove and return element Len() - 1.
}
```

嵌入interface有点类似继承的概念，把`sort.Interface`中定义的接口都继承了下来。

