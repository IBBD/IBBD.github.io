# 一个nodejs的问题解决

今天用nodejs时的时候, 遇到一个问题: `node: error while loading shared libraries: libv8.so.3.14.5`

开始以为是路径之类错了, 按照网上所说的修改了`/etc/ld.so.conf`但是没有解决.

## 解决

后来想, 会不会是因为`node`和`nodejs`这两个不同版本导致的.

```
node -v    # 报错
nodejs -v  # 正常
```

于是, 重装了nodejs, 发现问题还是依旧. 于是:

```
which node
which nodejs

cp $(which nodejs) $(which node)
```

OK!

## END

版本不同经常会导致各种各样的问题, which命令还挺实用的.



---------

Date: 2016-08-18  Author: alex cai <cyy0523xc@gmail.com>
