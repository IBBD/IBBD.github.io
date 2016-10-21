# 从python2到python3的迁移

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

## 相关文章

- http://cdwanze.github.io/%E7%94%B5%E8%84%91/python/python3%E8%AF%AD%E8%A8%80/python2%E5%88%B0python3%E7%9A%84%E7%A7%BB%E6%A4%8D%E9%97%AE%E9%A2%98.html
- http://ginsmile.github.io/blog/2015-10-02-cong-python2sheng-ji-dao-python3.html
- https://www.zhihu.com/question/19698598
- https://docs.python.org/3/whatsnew/3.0.html

