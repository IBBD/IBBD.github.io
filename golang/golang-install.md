# Golang最新版本安装

新版本的golang需要旧版本的golang(1.5以下的版本, 现在通常选择1.4.2)来编译, 所以安装时, 需要先安装golang1.5以下的版本.

```sh
cd /home/ibbd/golang

# 安装1.4.2版本
wget https://github.com/golang/go/archive/go1.4.2.zip
unzip go1.4.2.zip
cd go1.4.2/src
./all.bash

# 安装最新版golang
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



