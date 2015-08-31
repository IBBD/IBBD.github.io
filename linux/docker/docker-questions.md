# Docker平时遇到的问题

1. 在docker里怎么执行crontab任务？

试了一下，很难，不过可以有变通的方法，如下：

```sh
# 在宿主的环境可以执行如下：
sudo docker exec -ti ibbd-php-fpm php /var/www/test.php
# 所以可以直接在crontab执行
```


