# Golang中的interface详解

参考：
- http://blog.csdn.net/justaipanda/article/details/43155949
- http://www.cnblogs.com/hustcat/p/4007126.html

Go语言的主要设计者之一罗布·派克（ Rob Pike）曾经说过，如果只能选择一个Go语言的特 性移植到其他语言中，他会选择接口。可见接口在golang中的地位，及其对gloang这门语言所带来的活力。

------

## 传统理解的接口

```java
interface IFoo {
    void Bar();
}
class Foo implements IFoo {
    void Bar(){}
}
```

这就是java的接口，侵入式接口。

## Golang中的接口

在Go语言中，一个类只需要实现了接口要求的所有函数，我们就说这个类实现了该接口， 例如：

```go
type IWriter interface {
    Write(buf []byte) (n int, err error)
}
type File struct {
    // ...
}
func (f *File) Write(buf []byte) (n int, err error) {
    // ...
}
```

非侵入式接口一个很重要的好处就是去掉了繁杂的继承体系，我们看许大神在《go语言编程》一书中作的总结：

1. 其一， Go语言的标准库，再也不需要绘制类库的继承树图。你一定见过不少C++、 Java、 C# 类库的继承树图。这里给个Java继承树图：  http://docs.oracle.com/javase/1.4.2/docs/api/overview-tree.html  在Go中，类的继承树并无意义，你只需要知道这个类实现了哪些方法，每个方法是啥含义就足够了。
2. 其二，实现类的时候，只需要关心自己应该提供哪些方法，不用再纠结接口需要拆得多细才 合理。接口由使用方按需定义，而不用事前规划。
3. 其三，不用为了实现一个接口而导入一个包，因为多引用一个外部的包，就意味着更多的耦 合。接口由使用方按自身需求来定义，使用方无需关心是否有其他模块定义过类似的接口。

## 面向对象

golang不支持完整的面向对象思想，它没有继承，多态则完全依赖接口实现。golang只能模拟继承，其本质是组合，只不过golang语言为我们提供了一些语法糖使其看起来达到了继承的效果。

## interface的内存布局

了解interface的内存结构是非常有必要的，只有了解了这一点，我们才能进一步分析诸如类型断言等情况的效率问题。先看一个例子：

```go
type Stringer interface {
    String() string
}

type Binary uint64

func (i Binary) String() string {
    return strconv.Uitob64(i.Get(), 2)
}

func (i Binary) Get() uint64 {
    return uint64(i)
}

func main() {
    b := Binary{}
    s := Stringer(b)
    fmt.Print(s.String())
}
```

## 基本使用

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

type Seeker interface {
    Seek(offset int64, whence int) (int64, error)
}

type File struct {
    // ...
}
func (f *File) Read(buf []byte) (n int, err error)
func (f *File) Write(buf []byte) (n int, err error)
func (f *File) Seek(off int64, whence int) (pos int64, err error)
func (f *File) Close() error
```

上面定义了四个接口。

## 空接口

```go
// interface{}是一个通用类型，可以储存任意类型的值。
var general interface{}
general = 6.6
type_cast(general)
general = 2
type_cast(general)
```

在Go语言中，所有其它数据类型都实现了空接口。

```go
var v1 interface{} = 1
var v2 interface{} = "abc"
var v3 interface{} = struct{ X int }{1}
```

如果函数打算接收任何数据类型，则可以将参考声明为interface{}。最典型的例子就是标准库fmt包中的Print和Fprint系列的函数：

```go
func Fprint(w io.Writer, a ...interface{}) (n int, err error) 
func Fprintf(w io.Writer, format string, a ...interface{})
func Fprintln(w io.Writer, a ...interface{})
func Print(a ...interface{}) (n int, err error)
func Printf(format string, a ...interface{})
func Println(a ...interface{}) (n int, err error)
```

## Type switch与Type assertions

在Go语言中，我们可以使用type switch语句查询接口变量的真实数据类型，语法如下：

```go
type Stringer interface {
    String() string
}

var value interface{} // Value provided by caller.
switch str := value.(type) {
case string:
    return str //type of str is string
case Stringer: //type of str is Stringer
    return str.String()
}
```

类型转换：

```go
str, ok := value.(string)
if ok {
    fmt.Printf("string value is: %q\n", str)
} else {
    fmt.Printf("value is not a string\n")
}
```




---------

Date: 2016-05-30  Author: alex cai <cyy0523xc@gmail.com>
