# IBBD技术博客

文章目录： [按目录索引](https://github.com/IBBD/blog/blob/master/0-index.md) | [按修改日期索引](https://github.com/IBBD/blog/blob/master/0-index-date.md)  


```php
echo 'Hello, world!';
```

```python
print 'Hello, world!'
```

```javascript
console.log('Hello, world!');
```

```go
fmt.Printf("Hello, world or 你好，世界 or καλημ ́ρα κóσμ or こんにちはせかい\n")
```

## 我们的技术

### 前端

![Javascript](https://github.com/IBBD/IBBD.github.io/raw/master/_img/javascript.jpg)
![React](https://github.com/IBBD/IBBD.github.io/raw/master/_img/react.jpg)
![Redux](https://github.com/IBBD/IBBD.github.io/raw/master/_img/redux.png)
![D3](https://github.com/IBBD/IBBD.github.io/raw/master/_img/d3js.jpg)

### 后台

![PHP](https://github.com/IBBD/IBBD.github.io/raw/master/_img/php.jpg)
![Laravel](https://github.com/IBBD/IBBD.github.io/raw/master/_img/laravel.jpg)
![Nodejs](https://github.com/IBBD/IBBD.github.io/raw/master/_img/nodejs.jpg)

### 后端

![Golang](https://github.com/IBBD/IBBD.github.io/raw/master/_img/golang.jpg)
![Redis](https://github.com/IBBD/IBBD.github.io/raw/master/_img/redis.jpg)
![MariaDB](https://github.com/IBBD/IBBD.github.io/raw/master/_img/mariadb.jpg)
![MongoDB](https://github.com/IBBD/IBBD.github.io/raw/master/_img/mongodb.jpg)
![Shell](https://github.com/IBBD/IBBD.github.io/raw/master/_img/shell.jpg)
![Docker](https://github.com/IBBD/IBBD.github.io/raw/master/_img/docker.jpg)

### 大数据

![Python](https://github.com/IBBD/IBBD.github.io/raw/master/_img/python.jpg)
![Hadoop](https://github.com/IBBD/IBBD.github.io/raw/master/_img/hadoop.jpg)
![Spark](https://github.com/IBBD/IBBD.github.io/raw/master/_img/spark.jpg)
![ElasticSearch](https://github.com/IBBD/IBBD.github.io/raw/master/_img/elasticsearch.jpg)
![NLTK](https://github.com/IBBD/IBBD.github.io/raw/master/_img/nltk.jpg)
![Scrapy](https://github.com/IBBD/IBBD.github.io/raw/master/_img/scrapy.jpg)

### 其他

![Git](https://github.com/IBBD/IBBD.github.io/raw/master/_img/git.jpg)
![vim](https://github.com/IBBD/IBBD.github.io/raw/master/_img/vim.jpg)
![Ubuntu](https://github.com/IBBD/IBBD.github.io/raw/master/_img/ubuntu.jpg)


## 使用步骤

### 发布：

1. git clone本项目
2. 编辑一个文档，markdown格式
3. 生成索引文件`0-index.md`，命令：`./create_index`
4. git add相应的文件
5. git commit -am '说明'
6. git push

### 搜索：

- 使用`ag`搜索，用法如下：

```sh
# Install
apt-get install silversearcher-ag

# 使用
ag test_blah ~/code/
```

- 也可以我们实现的脚本进行搜索：`./search your-keyword`

### 注意

- 索引文件所使用的title，默认使用md文件的第一行的字符串，会自动去掉前面的#号和空格，如果为空，则直接使用文件名
- 在文章最后，可以按以下格式增加日期和作者（可选项）

```

---------

Date: 2016-09-06  Author: alex cai <cyy0523xc@gmail.com>
```
