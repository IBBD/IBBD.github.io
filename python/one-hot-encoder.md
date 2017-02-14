# 使用Python进行One-Hot编码及特征工程的相关问题解决
什么是One-Hot编码，这里不做介绍，只介绍怎么使用。

## 简单使用

```python
mport numpy as np
from sklearn.preprocessing import OneHotEncoder

# 原始数据
data = [[0,1],[0,2],[3,1]]

# 转化编码
enc = OneHotEncoder()
enc.fit(data)
hoted_data = enc.transform(data).toarray()
print(hoted_data)
```

上面的代码会输出：

```
array([[ 1.,  0.,  1.,  0.],
       [ 1.,  0.,  0.,  1.],
       [ 0.,  1.,  1.,  0.]])
```

上面将每个特征都作为类别数据进行了转换，例如第一列有0和3两个值，编码成01和10，同理第二列也一样。

## 类别数据与数值数据混合编码
在实际使用中，可能同时包含类别数据与数值数据。使用`OneHotEncoder??`查看文档，可以看到其有`categorical_features`的参数，其默认值为`all`，即所有字段都作为类别特征。

```python
# 只将第一列的数据作为类别特征
enc = OneHotEncoder(categorical_features=np.array([0]))
enc.fit(data)
hoted_data = enc.transform(data).toarray()
print(hoted_data)
```

其输出结果如下：

```
[[ 1.  0.  1.]
 [ 1.  0.  2.]
 [ 0.  1.  1.]]
```

和前面的输出结果做对比，就能发现其中的差别。

注：`fit`和`transform`还可以合并为`fit_transform`。

## 归一化
对于上面的输出结果，第三列数值型字段并没有进行归一化，不过在python中进行归一化也很简单：

```python
from sklearn.preprocessing import MinMaxScaler

data2 = [[0, 1], [0, 2], [3, 3]]
mms = MinMaxScaler()
mms_data = mms.fit_transform(data2)
'''
array([[ 0. ,  0. ],
       [ 0. ,  0.5],
       [ 1. ,  1. ]])
'''
```
## 字符串特征转换为整型
上面的example都是基于整型数据进行特征工程的，但是实际上，很多类别数据都是字符串的类型，需要先处理。`LabelEncoder`的用法如下：

```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
le_data = le.fit_transform(["hello", "world", "test"])
'''
array([0, 2, 1])
'''
```

实际处理时，数据格式可能是这样的`[['hello', 1], ['hello', 2], ['world', 3]]`，这时使用`pandas`比较好处理，例如：

```python
import pandas as pd

# 原始数据
data3 = [['hello', 1], ['hello', 2], ['world', 3]]
df3 = pd.DataFrame(data3)
df3.columns = ["f1", "f2"]
'''
      f1  f2
0  hello   1
1  hello   2
2  world   3
'''

# 这时需要提取第一列就非常简单了
le = LabelEncoder()
le_f1 = le.fit_transform(df3["f1"])  # array([0, 0, 1])

df3["f1"] = le_f1
```

## 处理有序分类特征
例如年龄段这类数据，它是有序的。这里处理比较简单，不详述。

## 相关文章

- http://www.jianshu.com/p/516f009c0875
- https://ljalphabeta.gitbooks.io/python-/content/categorical_data.html

