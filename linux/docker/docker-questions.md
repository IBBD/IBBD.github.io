# Docker平时遇到的问题

1. 在docker里怎么执行crontab任务？

试了一下，很难，不过可以有变通的方法，如下：

```sh
# 在宿主的环境可以执行如下：
sudo docker exec -ti ibbd-php-fpm php /var/www/test.php
# 所以可以直接在crontab执行
```

2. 在docker中启动mongoDB，出现以下问题：

```
root@fecd3a082d92:/# service mongod start
Starting database: mongod/etc/init.d/mongod: 138: ulimit: Illegal option -u
 failed!
```

3. 在阿里云上安装docker，无法启动

`docker info` 提示如下：

```
connect to the Docker daemon. Is 'docker -d' running on this host?
```
解决：
```
sudo route del -net 172.16.0.0 netmask 255.240.0.0  
```
4. 在阿里云ECS上通过dockerfile编译php-fpm的镜像时，出错

```
E: Unable to locate package libmcrypt-dev
E: Unable to locate package libfreetype6-dev
E: Unable to locate package libjpeg62-turbo-dev
E: Unable to locate package libpng12-dev
E: Unable to locate package libssl-dev
```
在本地编译时没问题，应该是刚安装，软件源还来不及更新，所以才会无法找到包。我猜测在更换软件源之后，也很可能会出现这个问题。

解决：暂时注释掉更换源的语句。

5. 构建时，可能会一直卡在pulling那里，重试也没有用，这时重启docker可能可以解决问题：`sudo service docker restart`

`docker pull`的过程中尽量不要强制退出，可能会导致一些比较奇怪的问题。

6. 构建scrapy时，run命令错误提示如下：

```
End of CmdRun(), Waiting for hijack to finish
```
可能是`docker run`这个命令写得有问题，重新写一个就ok了。

7. 构建时的cache问题

Dockerfile可能写成如下形式：

```
RUN apt-get update \ 
    && apt-get install -y gcc
    && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y git
```

这样会失败，前面已经rm了。最后写在一起，如果不能写在一起，就要先update，最后rm多余的内容

8. 镜像无法删除

```
sudo docker rmi --force=true 8c00acfb0175 
Error response from daemon: Conflict, 8c00acfb0175 wasn't deleted
Error: failed to remove images: [8c00acfb0175]
```

确定 `sudo docker ps -a`返回为空，没有依赖的容器了。

后来又可以了，暂时无解

9. 使用pip安装依赖时出现的问题

```
error: command 'gcc' failed with exit status 1
```

确认gcc已经安装成功，网上有人说是因为没有安装libxml2-dev和libxlst1-dev，并给出的解决方案是：

```sh
sudo apt-get install python-dev
sudo apt-get install libxml2 libxml2-dev
sudo apt-get install libxslt1.1 libxslt1-dev
```

解决。出现新的问题：

```
Download error on https://pypi.python.org/simple/cffi/: EOF occurred in violation of protocol (_ssl.c:590) -- Some packages may not be found!
Couldn't find index page for 'cffi' (maybe misspelled?)
```





---------

Date: 2015-10-09  Author: alex cai <cyy0523xc@gmail.com>
