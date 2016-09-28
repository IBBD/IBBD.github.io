# Linux 命令帮助利器

当你记不清一个命令的用法时，你会怎么做？

例如想解压一个文件，tar命令的解压用法记不清了

## 通常的做法

（1）查看命令手册

```
# man tar
```

（2）查看命令帮助

```
# tar --help
```

（3）百度搜索

（4）自己的命令备忘笔记

man和help的好处是直接在Linux命令窗口完成，但缺点也很明显，他们更像是一个说明文档，内容很全，学习时用他们很有用，但马上就想知道怎么用时就不方便了

搜索和备忘的好处是可以比较快的找到实际用法，但需要离开Linux命令窗口，完成查找操作

## 有没有更高效方法呢？

今天发现了一个利器 - cheat

先看下使用效果

```
# cheat tar
# cheat top
```

可以看到，结果非常简洁，直接列出了命令的使用案例，在网上看到有人把cheat叫做“命令小抄大全”，感觉非常贴切

在命令行中直接查看命令的使用示例，非常高效，建议试试看

github中的cheat项目地址

https://github.com/chrisallenlane/cheat

下面是安装方法（我的系统是centos）

```
# yum install python
# yum install python-pip
# yum install git
# pip install docopt pygments
# git clone https://github.com/chrisallenlane/cheat.git
# cd cheat
# python setup.py install
# cheat -v
```


---------

Date: 2016-01-26  Author: alex cai <cyy0523xc@gmail.com>
