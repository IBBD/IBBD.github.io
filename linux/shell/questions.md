# Shell使用过程中遇到的问题集合 

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



