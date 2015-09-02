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

