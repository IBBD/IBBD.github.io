# 一个文件备份的shell脚本

需求：`因为服务器空间不够，需要将生成的备份文件从原来的目录转移到一个新挂载的目录下。`

先看代码：

```sh 
# 转移到新的目录
old_dir=/home/git/gitlab/tmp/backups
new_dir=/data/gitlab-backup
pattern=*_gitlab_backup.tar
echo "mv to $new_dir ...doing..."

# 将创建超过一天（24小时）的文件转移到新目录
# -mtime +n|-n : 加号表示大于，减号表示小于，大于0意思就是24小时以上的
# -exec ：将满足条件的文件执行后面的操作
find $old_dir/$pattern -mtime +0 -exec mv {} $new_dir \;

# 统计新目录下满足条件的文件个数
total=$(find $new_dir/$pattern | wc -l)
if [ $total -gt 10 ]
then
    # 注意：算数运算不能直接加或者减，因为在shell里面默认都是字符串，a+b的结果只会是字符串“a+b”
    # 和赋值一样，=号前后不能有空格
    let delete_num=$total-10

    # 保留最新的10个
    # awk是模式搜索与处理语言
    rm $(find $new_dir/$pattern | awk '{count++}{if (count <= '$delete_num') print $1}')
fi

# 程序的最后，输出执行情况
echo '==>all is ok'
```

这里需要说明的有几个地方：

- 数值计算
- 子shell 
- find命令 
- awk命令

下面逐一展开。

## 数值计算 






---------

Date: 2015-10-09  Author: alex cai <cyy0523xc@gmail.com>
