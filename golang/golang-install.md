# Golang最新版本安装

完整的安装脚本请看这里：https://github.com/cyy0523xc/ubuntu-init/blob/master/step05-golang.sh

-----------------

新版本的golang需要旧版本的golang(1.5以下的版本, 现在通常选择1.4.2)来编译, 所以安装时, 需要先安装golang1.5以下的版本.

```sh
# 安装1.4.2版本
cd /home/ibbd/golang
wget https://github.com/golang/go/archive/go1.4.2.zip
unzip go1.4.2.zip
cd go1.4.2/src
./all.bash

# 安装最新版golang
cd /home/ibbd/golang
wget https://github.com/golang/go/archive/go1.7.zip
unzip go1.7.zip
cd go1.7/src
./all.bash

# 这时会报错如下:
ERROR: Cannot find /home/ibbd/golang/go1.4/bin/go.
Set $GOROOT_BOOTSTRAP to a working Go tree >= Go 1.4.

# 配置$GOROOT_BOOTSTRAP
export GOROOT_BOOTSTRAP=/home/ibbd/golang/go-go1.4.2

# 重新安装
./all.bash

# 配置GOPATH  配置PATH
# 这些配置最好启动时自动加载了
# vim /etc/bash.bashrc
export GOROOT=/home/ibbd/golang/go-go1.7/
export GOPATH=/var/www/golang
export PATH=/home/ibbd/golang/go-go1.7/bin:$PATH

# 查看配置
go env
```

## 升级新版本

1. 将新版本下载下来, 并解压
2. 配置好`$GOROOT_BOOTSTRAP`
3. 执行`./all.bash`
4. 修改相应的环境变量

## 安装过程中踩过的坑

### 在ubuntu16.04上安装1.4出现问题如下
运行`./all.bash`时出现如下问题：

```
# cmd/pprof
/home/alex/golang/go-go1.4.3/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
/home/alex/golang/go-go1.4.3/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
runtime/cgo(.text): unexpected relocation type 298
runtime/cgo(.text): unexpected relocation type 298
# cmd/go
/home/alex/golang/go-go1.4.3/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
/home/alex/golang/go-go1.4.3/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
runtime/cgo(.text): unexpected relocation type 298
runtime/cgo(.text): unexpected relocation type 298
```

解决：

```sh
# 安装旧版go
sudo apt-get install golang

# 配置环境变量
export GOROOT_BOOTSTRAP="$(go env GOROOT)"

# 编译新版本
cd /path/to/go-go1.9/src
bash all.bash

# 配置新版环境变量
export GOROOT=/home/alex/golang/go-go1.9/
export GOPATH=/var/www/golang
export PATH=/home/alex/golang/go-go1.9/bin:$PATH

# 查看新版本是否配置成功
go env

```





---------

Date: 2016-09-06  Author: alex cai <cyy0523xc@gmail.com>
