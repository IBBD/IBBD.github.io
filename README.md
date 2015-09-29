# IBBD技术博客

[文章目录请点击这里](https://github.com/IBBD/blog/blob/master/0-index.md)


```php
echo 'Hello, world!';
```

```python
print 'Hello, world!'
```

```javascript
console.log('Hello, world!');
```

## 使用步骤

发布：

1. git clone本项目
2. 编辑一个文档，markdown格式
3. 生成索引文件`0-index.md`，命令：`./create_index`
4. git add相应的文件
5. git commit -am '说明'
6. git push

搜索：

1. 按关键词搜索：`./search your-keyword`

*注意* 

- 索引文件所使用的title，默认使用md文件的第一行的字符串，会自动去掉前面的#号和空格，如果为空，则直接使用文件名

