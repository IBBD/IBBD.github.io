# 使用dockerfile来构建nginx镜像

- 镜像：https://hub.docker.com/_/nginx/
- dockerfile：https://github.com/nginxinc/docker-nginx/

## 基本操作 

```sh
# 拉取镜像
sudo docker pull nginx
sudo docker images

# 运行
# docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
sudo docker run --name some-nginx -d -p 8080:80 nginx
sudo docker ps -a

# 在浏览器输入：http://localhost:8080，即可访问

# 进入容器
# docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
# Run a command in an existing container
sudo docker exec -ti some-nginx /bin/bash

# 在容器内操作 
ps aux
ls /etc/nginx 
cat /etc/nginx/nginx.conf

# 退出容器
exit

# 容易的启动，停止，删除
# 删除之前先要停止
sudo docker stop|start|restart|rm some-nginx 

```

## 自定义配置文件

dockerfile: https://github.com/IBBD/dockerfile-nginx

### 与php-fpm的交互问题

```
docker run -ti -rm --name php-fpm php:5.6-fpm
```

在启动nginx容易的时候，加上```--link``` 和 ```--volumes-from``` 两个参数。

## 问题

1. 启动不了

在dockerfile一句一句调试

```
tail -f tail -f /var/log/nginx/error.log 

```


