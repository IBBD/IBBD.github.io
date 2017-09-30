# Python最简单的异步实现
php中`fastcgi_finish_request`函数来实现请求的异步，使用非常简单，只要调用一下即可，并不需要改变原有的逻辑。

## 使用tornado.web实现
在python中也可以实现类似的效果，具体看代码：

```python
# -*- coding: utf-8 -*-
# 最简单的异步实现方式
#
# Author: alex
# Created Time: 2017年09月30日 星期六 17时12分31秒
import time
import tornado.ioloop
import tornado.web
import tornado.options

tornado.options.parse_command_line()


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("Hello world")
        self.finish()
        time.sleep(6)
        print("after sleep")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ], autoreload=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
```

使用curl模拟请求：`curl localhost:8000`，会马上输出`Hello world`，过6秒之后会在控制台打印出`after sleep`，就这样实现了异步的功能。

在实现上比php的稍微复杂了一下，不过也不复杂。

