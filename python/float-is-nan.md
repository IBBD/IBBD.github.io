# Python中float值可能是NaN的问题

刚刚测试一个网站是，报错：

```
Inf and NaN cannot be JSON encoded
```

查看MongoDB数据库，发现数据库的值就是`NaN`，python写入了这个值。查看字段格式化时，发现数据已经使用`float`函数进行了格式化。使用`type`函数判断类型时，又确实是`float`。

上网查一下资料，才知道`NaN 属性是代表非数字值的特殊值。该属性用于指示某个值不是数字。`，这个拗口的定义。。。

## 解决

```python
from math import isnan, isinf

val = float(val)
if isnan(val) or isinf(val):
    val = 0
```

注意：默认为0值，未必所有场景的适合
