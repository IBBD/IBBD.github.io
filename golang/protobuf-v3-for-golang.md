# 安装及使用Protobuf-v3（golang）

在golang中安装并使用protobuf来做数据序列化（ubuntu环境），其官方项目：https://github.com/golang/protobuf/ ，但是这里并没有比较详细的安装说明，而且其文档的例子也是对旧版协议的，故踩了不少坑。

## Install Protocol buffers

- 先按照protocol buffers

网上有不少关于这个的安装说明，但是经过事件大都是有问题，或者只是针对旧版本的。在64位ubuntu下，下面的方式经实验是ok的：

```sh
# 在 https://github.com/google/protobuf/releases/ 下载最新的cpp版本
wget https://github.com/google/protobuf/releases/download/v3.1.0/protobuf-cpp-3.1.0.tar.gz

tar zxvf protobuf-cpp-3.1.0.tar.gz

cd protobuf-3.1.0
./configure
make
sudo make install

# 检查安装是否成功
protoc -h
```

但是报错：`protoc: error while loading shared libraries: libprotoc.so.8: cannot open shared`

错误原因：

protobuf的默认安装路径是/usr/local/lib，而/usr/local/lib 不在Ubuntu体系默认的 LD_LIBRARY_PATH 里，所以就找不到该lib

解决方法：

1. 创建文件 /etc/ld.so.conf.d/libprotobuf.conf 包含内容：`/usr/local/lib`
2. 加载新配置`sudo ldconfig`

## 安装Golang支持

这个比较简单：

```sh
go get -u github.com/golang/protobuf/{proto,protoc-gen-go}
```

注意官方的说明：The compiler plugin, protoc-gen-go, will be installed in $GOBIN, defaulting to $GOPATH/bin. It must be in your $PATH for the protocol compiler, protoc, to find it.

## 入门使用

项目首页上的例子是基于版本2的，比较坑。经过测试之后，一个例子如下

`vim test.proto`

```go
// 注意：若想使用新版协议，必须加上这个
syntax = "proto3";

package example;

// 枚举量
enum Corpus {
  UNIVERSAL = 0;
  WEB = 1;
  IMAGES = 2;
  LOCAL = 3;
  NEWS = 4;
  PRODUCTS = 5;
  VIDEO = 6;
}

message Test {
  string label = 1; // 注释
  int32 type = 2;
  int64 reps = 3;
  Corpus hello = 4;
}
```

执行命令`protoc --go_out=. *.proto`，就会生成文件`test.pb.go`

其生成的关键数据结构如下：

```go

type Corpus int32

const (
	Corpus_UNIVERSAL Corpus = 0
	Corpus_WEB       Corpus = 1
	Corpus_IMAGES    Corpus = 2
	Corpus_LOCAL     Corpus = 3
	Corpus_NEWS      Corpus = 4
	Corpus_PRODUCTS  Corpus = 5
	Corpus_VIDEO     Corpus = 6
)

var Corpus_name = map[int32]string{
	0: "UNIVERSAL",
	1: "WEB",
	2: "IMAGES",
	3: "LOCAL",
	4: "NEWS",
	5: "PRODUCTS",
	6: "VIDEO",
}
var Corpus_value = map[string]int32{
	"UNIVERSAL": 0,
	"WEB":       1,
	"IMAGES":    2,
	"LOCAL":     3,
	"NEWS":      4,
	"PRODUCTS":  5,
	"VIDEO":     6,
}

func (x Corpus) String() string {
	return proto.EnumName(Corpus_name, int32(x))
}
func (Corpus) EnumDescriptor() ([]byte, []int) { return fileDescriptor0, []int{0} }

type Test struct {
	Label string                     `protobuf:"bytes,1,opt,name=label" json:"label,omitempty"`
	Type  int32                      `protobuf:"varint,2,opt,name=type" json:"type,omitempty"`
	Reps  int64                      `protobuf:"varint,3,opt,name=reps" json:"reps,omitempty"`
	Hello Corpus                     `protobuf:"varint,4,opt,name=hello,enum=example.Corpus" json:"hello,omitempty"`
}

```
## 测试生成的结构

```go
package example

import (
	"fmt"
	"testing"

	"github.com/golang/protobuf/proto"
)

func TestHello(t *testing.T) {
	test := &Test{
		Label: "0123456789",
		Reps:  1,
		Hello: 7,
	}
	data, err := proto.Marshal(test)
	fmt.Println(len(data))
	if err != nil {
		t.Fatal(err)
	}
	newTest := &Test{}
	err = proto.Unmarshal(data, newTest)
	if err != nil {
		t.Fatal(err)
	}

	fmt.Println(newTest)
	fmt.Println(newTest.Type)  // 默认值是0
	fmt.Println(newTest.Hello)
}
```

生成的结果字符串的确很短，比MessagePack还要短了不少，毕竟protobuf不需要保存key，而且如果没有值的话，也可以使用默认值。至于性能方面，有机会再去测试。

**关于Timestamp**： 官方有提供这样的类型，但是使用比较复杂，最终转化为两个整数进行保存，还不如自己直接转成整数即可。

## 扩展

- [官方文档](https://developers.google.com/protocol-buffers/docs/proto3)
- [Protobuf 的 proto3 与 proto2 的区别](https://solicomo.com/network-dev/protobuf-proto3-vs-proto2.html)
- [在 Golang 中使用 Protobuf](http://studygolang.com/articles/2540)


