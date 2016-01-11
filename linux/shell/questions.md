# Shell使用过程中遇到的问题集合 

## 解决命令行的locale问题

之前一直提示：

```
bash: warning: setlocale: LC_ALL: cannot change locale (en_GB.UTF-8)
```

解决

```
vim /etc/default/locale
LC_ALL=""

locale-gen en_US.UTF-8
```

重启终端即可。

## sed的问题 

命令直接修改redis配置文件的绑定ip

```sh 
sed -i 's/^bind\s[\s0-9\.]*$/bind 10.161.221.70/g' /etc/redis/redis.conf

# 报错：sed: -e expression #1, char 26: unterminated `s' command
# 改成如下：

sed -i 's/^bind\s[\s0-9\.]*$/bind\s10.161.221.70/g' /etc/redis/redis.conf

# 这个没有报错了，但是结果却不对，把对应的行修改成了：binds10.161.221.70
# 改成下面的形式能够正常，但是很别扭

sed -i 's/^bind(\s)[\s0-9\.]*$/bind$110.161.221.70/' /etc/redis/redis.conf
```



## if语句中有多个条件组合时 

例如下面的语句：

```sh 
if [ $# -lt 3 -o $1 = help ]; then 
    # do somethings...
fi
```

这个语句执行的时候，会报参数异常，需要修改为如下：

```sh 
if [ $# -lt 3 -o "$1" = help ]; then 
    # do somethings...
fi
```



