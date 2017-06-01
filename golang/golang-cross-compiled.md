# Golang下的交叉编译
最近项目需要编译到多个平台上执行，需要多个目标平台上执行，例如linux，mac，windowns等。本来想直接在不同平台上直接编译，不过这样太麻烦了，而且很难管理，所以只能交叉编译了。

golang对交叉编译支持也比较好，不过如果需要自己去配置还是挺麻烦的，所以找了一个工具：https://github.com/karalabe/xgo/

## 一个坑
因为我们用的是内部的git仓库，通过配置host的形式访问，而且直接按照文档所说去执行，会有问题：

- 运行的容器内并没有相应的host
- 不清楚他内部是怎么挂载目录的

查看xgo的源码，在相应地方把容器的启动参数打印出来，如下：

```
[run --rm -v /var/www/golang/src/git.ibbd.net/ai/nlp-tools/eyenlp-classify:/build -v /home/alex/.xgo-cache:/deps-cache:ro -e REPO_REMOTE= -e REPO_BRANCH= -e PACK= -e DEPS= -e ARGS= -e OUT= -e FLAG_V=false -e FLAG_X=false -e FLAG_RACE=false -e FLAG_TAGS= -e FLAG_LDFLAGS= -e FLAG_BUILDMODE=default -e TARGETS=./. -e EXT_GOPATH= karalabe/xgo-latest git.ibbd.net/ai/nlp-tools/eyenlp-classify]
```

注意：这里并没有设置或者挂载`GOPATH`目录，但是我们在使用的时候又希望将外部的代码目录挂载到容器里，这样里外的目录结构可以保持一致，可以省掉很多麻烦。

开始时并不太确定`/var/www/golang/src/git.ibbd.net/ai/nlp-tools/eyenlp-classify:/build`这个目录挂载的作用，后来才知道，这是用来保存编译后生成的文件的。

xgo在启动docker容器的时候，使用了`--rm`参数，即每次使用完就删掉相应的容器。

## 使用步骤
因为不能直接像文档那样使用xgo，所以我们想先启动容器，然后进入容器之后，做相应的配置，再编译。

#### SETP1: 启动容器
挂载代码目录，挂载编译目录，同时命名容器，方便后续使用：

```sh
docker run -ti --name=ibbd-xgo \
    -v /var/www/:/var/www \
    -v /var/www/build:/build \
    karalabe/xgo-latest /bin/sh
```

这样启动的时候，会报错，不过并不影响使用，关闭窗口之后，使用`docker ps`可以看到容器已经正常运行了。

#### SETP2: 进入容器配置环境

```sh
# 进入容器
docker exec -ti ibbd-xgo /bin/bash

# 查看golang的配置
go env

# 设置GOPATH
export GOPATH="/var/www/golang"
```

#### STEP3: 编译
因为我们使用了内外一致的目录结构，并配置了GOPATH，所以就不存在内部git仓库提到的问题了。编译：

```sh
xgo git.ibbd.net/ai/nlp-tools/eyenlp-classify
```

编译完之后，到`/var/www/build`目录就可以看到相应的文件。

## 问题

#### 所有平台都编译，这个太慢，而且我们并不需要所有平台的。

