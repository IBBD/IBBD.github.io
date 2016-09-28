# python中使用click来构建接口应用

这个其实没什么好说的，直接上代码就懂了：

```python
import click

@click.command()
@click.argument('word', required=True)
@click.option('-p', "--page", default="1", required=False,
              help='Page: 当前页码')
@click.option('-n', "--num", default="15", required=False,
              help='page Number: 每页显示条数')
@click.option('-s', "--simple", default="true", required=False,
              help='Simple: 是否为简单模式，true则只显示标题和URL, 否则显示全部')
@click.option('-t', "--tag", default="false", required=False,
              help='Tag: 是否为标签模式')
def search(word, page, num, simple, tag):
    # do sometings...
    return


if __name__ == "__main__":
    search()
```




---------

Date: 2016-07-27  Author: alex cai <cyy0523xc@gmail.com>
