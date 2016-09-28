# 在php7-fpm的docker镜像内编译GD扩展

成功编译后的镜像地址: https://hub.docker.com/r/ibbd/php7-fpm

## 安装过程

### 直接安装失败

在Dockerfile中增加:

```sh
RUN  \
    docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-png-dir=/usr/include/ \
    && docker-php-ext-install gd \
    ...
```

编译失败, 提示: 

```
If configure fails try --with-webp-dir=<DIR>
configure: error: jpeglib.h not found.
```

webp这种格式, 我们暂时不需要, 可以忽略第一行提示. `jpeglib.h not found`表示找不到相应的头文件, 这应该是系统没有安装相应的库所致.

### 正确的安装过程

先安装gd库依赖的包, 关键部分的Dockerfile如下:

```sh
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        libmcrypt-dev \
        libssl-dev \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng12-dev \
    && apt-get autoremove \
    && apt-get clean \
    && rm -r /var/lib/apt/lists/*

# install php modules 
RUN  \
    docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-png-dir=/usr/include/ \
    && docker-php-ext-install gd 
```

完整版见: https://github.com/IBBD/dockerfile-php7-fpm/blob/master/Dockerfile

其中libfreetype6-dev, libjpeg62-turbo-dev, libpng12-dev这三者是新安装的.

## 相关文档

- http://php.net/manual/en/image.installation.php
- https://github.com/docker-library/php/blob/2f96a00aaa90ee1c503140724936ca7005273df5/7.0/fpm/Dockerfile


---------

Date: 2016-09-06  Author: alex cai <cyy0523xc@gmail.com>
