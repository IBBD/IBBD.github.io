# Golang踩坑分享


## golang path的相关配置

我的配置如下：

```sh
export GOPATH=/var/www/go-src
export GOROOT=/home/alex/golang/go-go1.6.2
export PATH=$GOROOT/bin:$GOPATH/bin:$PATH
```

## golang.org被墙的问题

1. 在`gopm.io`上下载，解压到相应的目录
2. 在`https://github.com/golang`上找到相应的包，`git clone`到相应的目录

第一种方法有时会报错。


