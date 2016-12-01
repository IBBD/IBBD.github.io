# 从python2到python3的迁移



## 在vim中快速修改print

```
:%s/^\(\s*print\)\s+\(.+\)$/\1(\2)/gc
```

## 碰到的几个问题

- `print "something"`改成`print("somethings")`
- `from filename import packagename`改为`from .filename import packagename`
- `except Exception, e`变成`except (Exception) as e`
- unicode的改变

```python
hello in [unicode, str]:
改成：
hello == str:
```

这个改动就无法兼容python2了，所以最好的方式，还是定义unicode，如下：

```python
try:
    unicode
except NameError:
    unicode = str
```

这样在python3的时候，就不会报错了

- `long`类型的问题

```python
try:
    long
except NameError:
    long = int
```

- `file`函数在python3中不支持，报错：`builtins.NameError: name 'file' is not defined`, 使用`open`函数替代。
- `ImportError: Bad magic number`不同版本的pyc所致，清除所有的pyc，重跑即可

```sh
find . -name "*.pyc" -type f -exec rm {} \;
```

- `do not assign a lambda expression, use a def`

```python
f = lambda x, y: x if y in x else x + [y]

# 改为：

def f(x, y):
    return x if y in x else x + [y]
```
- `builtins.AttributeError: module 'urllib' has no attribute 'quote_plus'`：将`import urllib`改为`import urllib.parse`，使用如下：

```python
# 修改为如下
val_encode = urllib.parse.quote_plus(val.encode('utf8'))
```

- `builtins.TypeError: can't pickle dict_keys objects`

打印出来结构如下：

```
 'save_fields': dict_keys(['desc', 'url', 'date', 'from', 'keyword', 'title'])
```

fix：

```python
env['save_fields'] = list(env['save_fields'])
```

这是keys方法导致的，在python2中：

```python
$ python
>>> foo = { 'bar': "hello", 'baz': "world" }
>>> type(foo.keys())
<type 'list'>
>>> foo.keys()
['baz', 'bar']
>>> foo.keys()[0]
'baz'
```

但是在python3中：

```python
$ python3
>>> foo = { 'bar': "hello", 'baz': "world" }
>>> type(foo.keys())
<class 'dict_keys'>
>>> foo.keys()
dict_keys(['baz', 'bar'])
>>> foo.keys()[0]
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
TypeError: 'dict_keys' object does not support indexing
```

- `TypeError: 'str' does not support the buffer interface`

```python
plaintext = 'Polish text: ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'
filename = 'foo.gz'
with gzip.open(filename, 'wb') as outfile:
    outfile.write(bytes(plaintext, 'UTF-8'))
with gzip.open(filename, 'r') as infile:
    outfile_content = infile.read().decode('UTF-8')
```

- `TypeError: can't use a string pattern on a bytes-like object`转成bytes
- `TypeError: unsupported operand type(s) for +: 'dict_items' and 'dict_items'`，python3不再支持这样
- `POST data should be bytes or an iterable of bytes. It cannot be of type str.`, 主要是改成这样：`urllib.parse.urlencode(d).encode("utf-8")`

## 相关文章

- http://www.ttlsa.com/docs/dive-into-python3/porting-code-to-python-3-with-2to3.html
- http://cdwanze.github.io/%E7%94%B5%E8%84%91/python/python3%E8%AF%AD%E8%A8%80/python2%E5%88%B0python3%E7%9A%84%E7%A7%BB%E6%A4%8D%E9%97%AE%E9%A2%98.html
- http://ginsmile.github.io/blog/2015-10-02-cong-python2sheng-ji-dao-python3.html
- https://www.zhihu.com/question/19698598
- https://docs.python.org/3/whatsnew/3.0.html

