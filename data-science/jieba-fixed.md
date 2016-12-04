# 结巴分词的字典中只能按空格进行分隔的问题

结巴分词的字典都是使用空格进行分隔的，格式如：

```
AT&T 3 nz
B超 3 n
c# 3 nz
C# 3 nz
c++ 3 nz
C++ 3 nz
T恤 4 n
A座 3 n
A股 3 n
A型 3 n
```

但是这样会产生一个比较大的问题，对于中英文混排的文章，例如`Hong kong`这样的词都分不到一块去。

## 只能按空格进行分隔的原因

看源码主要有：

```python
# vim ./__init__.py
# 这个正则表达式在关键词里，是支持空格的
re_userdict = re.compile('^(.+?)( [0-9]+)?( [a-z]+)?$', re.U)

# vim analyse/tfidf.py
content = open(new_idf_path, 'rb').read().decode('utf-8')
for line in content.splitlines():
    word, freq = line.strip().split(' ')  # 就是这里
```

结论：分词的自定义字典的关键词是支持空格的，但是IDF的字典不支持空格

自定义词典支持空格有问题的原因在于，如：

```
re_userdict = re.compile('^(.+?)( [0-9]+ )?( [a-z]+ )?$', re.U)

# 如果自定义关键词只是有关键词，但是没有后面的，例如：
line = "hello world"

# 匹配
re_userdict_semicolon.match(line).groups()

# 匹配的结果是
('hello ', None, 'world')
```

而且，谁知道我们的关键词不会有类似`公交线路 381`的呢

知道了问题，要解决就比较简单了

ps: 结巴源码的实现真是有点一般。。。

```python
# 使用分号进行分隔
re_userdict_semicolon = re.compile('^([^;]+?)(?:;)?([0-9]+)?(?:;)?([a-z]+)?$', re.U)
```

## 测试效果





