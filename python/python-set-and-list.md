# 在Python中，set和list的性能区别
在python3中测试。

先看测试代码：

```python
import time

def cal_time(func):
    t1 = time.mktime(time.localtime())
    func()
    t2 = time.mktime(time.localtime())
    print(t2 - t1)

def func1(a=set()):
    for i in range(100000):
        if i not in a:
            a.add(i)

def func1(a=list()):
    for i in range(100000):
        if i not in a:
            a.append(i)

cal_time(func1)
cal_time(func2)
```

在本机测试结果如下：

```
In [25]: calTime(func1)
0.0

In [26]: calTime(func2)
62.0
```

差距巨大！判断key是否在某个列表里，不要使用list类型，也不需要使用蹩脚的dict类型了，直接使用set即可！
