# IBBD Golang编码风格

- 满足`go fmt`之外，还需要遵守一定的内部风格，原则上以golang的源码风格为准，见[文档](https://github.com/golang/go)
- [编码风格基础文件](https://github.com/Ronmi/effectivego-tw/blob/master/effectivego.md)【重要】
- [golang配置文件风格](/golang/golang-env-config.md)
- 所谓的代码风格，通常是以保证可维护性和可测试性为目的的。

## 变量

- 变量命名总体要遵守语义明确的原则，避免无意义的单词。
- 尽量避免使用拼音命名，除非确实难以翻译。
- `常量`和`普通变量`：和变量的命名一样，统一为驼峰命名法，通常不使用下划线。如果首字母大写，则该变量在引用时，能别外部使用；否则，只能在package内部使用。
- 常量名字如果是几个单词的首字母缩写，则可能会全部大写，例如`const KB = 1024`
- `结构体内的字段`：采用和普通变量一样的驼峰命名方式，首字母大小写区分是否全局。
- `循环变量`：对于短循环的循环变量，可能使用像`i`，`j`，`k`，`v`等之类的单字母变量（这是习惯用法，通常不应该命名为其他的字母，例如abc等）。
- `type新类型`：采用和普通变量一样的方式。例如`type helloWorld int`，或者`type HelloWorld int`（全局类型）


## 函数

- `命名`：采用驼峰命名法，首字母是否大小写来区分是否全局有效。
- `长度`：一个函数通常不宜太长，超过50行的应该是少数，超过100行的更是少数的少数。
- 函数是在整个package内部有效的，如果模块聚合不合理，很容易出现找不到在哪里定义的问题。函数名应该是跟文件名有某种联系的（功能的内聚），这个比较难判断。
- 函数内部的变量都是局部变量，不应该使用大写字母开头
- 传入变量和返回变量以小写字母开头
- 在godoc生成的文档中，带有返回值的函数声明更利于理解

### 参数传递

- 对于少量数据，不要传递指针
- 对于大量数据的struct可以考虑使用指针
- 传入参数是map，slice，chan不要传递指针

因为map，slice，chan是引用类型，不需要传递指针的指针

## 文件与目录

- 文件名的命名采用小写字母和下划线的形式。例如`hello_world.go`
- 目录名的命名采用小写字母和连接符`-`，例如`hello-world`

## 包名命名

- 类似变量的命名方式，驼峰命名方式，首字母小写。
- 如果对应的目录名为`hello-world`，则对应的包名应该是`helloWorld`

## 异常处理

golang没有其他语言的try-catch结构，错误变量的命名通常为`err`，异常的处理通常只发生在主模块里，子模块通常只需要返回错误对象即可。

## 注释

关于注释，更多的看[这里](http://www.philo.top/2015/07/10/golang-doc/)

在编码阶段同步写好变量、函数、包注释，注释可以通过godoc导出生成文档。

注释必须是完整的句子，以需要注释的内容作为开头，句点作为结尾。

程序中每一个被导出的（大写的）名字，都应该有一个文档注释。

### 包注释: doc.go

每个程序包都应该有一个包注释，一个位于package子句之前的块注释或行注释。使用`doc.go`这样一个空文件，内容例如：

```
//Package regexp implements a simple library 
//for regular expressions.
package regexp 
```

### 函数，变量，结构等注释

第一条语句应该为一条概括语句，并且使用被声明的名字作为开头。

```
// Compile parses a regular expression and returns, if successful, a Regexp
// object that can be used to match against text.
func Compile(str string) (regexp *Regexp, err error) {}
```

注意：注释的第一行的第一个单词应该是函数名（例如Compile）

## 控制结构

### if

如果需要局部变量，使用如下方式：

```go
if err := file.Chmod(0664); err != nil {
    return err
}
```




---------

Date: 2016-09-18  Author: alex cai <cyy0523xc@gmail.com>
