# python异步任务队列：celery
说明：对celery使用时间不长，本文仅作为一种总结，未必都正确，或者可能存在更好的解决方式。

以下基于4.2.1版本。

## 使用celery期待达到的目的

- 将耗时任务异步化队列化提升，系统的可靠性和稳定性。
- 异常中止的任务，在重启后能继续执行。
- 可以简单的进行流量控制，避免拖垮服务器。

第一第二点都是可以实现的，第三点文档有说怎么配置，还没测试过。

## 主要代码
说明：代码只保留需要的部分。

### vim app.py

```python
from flask import Flask
from flask_celery import Celery

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# app.logger.addHandler(logger)

# celery
app.config['CELERY_BROKER_URL'] = celery_broker
app.config['CELERY_RESULT_BACKEND'] = celery_backend
celery = Celery(app)
```

开始的时候，是自己写，后来还是直接使用了`flask_celery`这个package，这里有一个比较大的问题，如果加上`app.logger.addHandler(logger)`，在celery worker启动的时候会报错。

### vim tasks.py

```python
from model_flow.app import celery
from model_flow.sys_path import get_sys_paths, \
    check_celery_set, celery_set_paths
from model_flow.settings import set_root_path, set_cache_path, \
    get_root_path, get_cache_path


def decorator_model(func):
    """模型异步接口装饰器"""
    def call(algo_name, algo_type, *args, **kwargs):
        user_root_path = get_root_path()
        cache_root_path = get_cache_path()
        sys_paths = get_sys_paths()
        func.delay(user_root_path, cache_root_path, sys_paths,
                   algo_name, algo_type, *args, **kwargs)
    return call


@decorator_model
@celery.task(name='model_flow.celery_tasks.tasks.train')
def train(
    user_root_path, cache_root_path, sys_paths,
    algo_name, algo_type,
    *args, **kwargs
):
    # 设置环境变量
    set_root_path(user_root_path)
    set_cache_path(cache_root_path)
    if check_celery_set() is False:
        celery_set_paths(sys_paths)

    # do something else...
```

需要在worker中使用到一些全局变量，还有需要设置import路径，开始时希望通过其他的方式共享变量，但是那些尝试都失败了。于是就成了上面的样子，每次调用的时候都传一次，并使用装饰器自动的获取和传递参数。实现有点丑陋，但至少功能是实现了。

本来想着，在这些参数改变的时候，自动触发调用相应的task来进行一次性设置，但是那样只会设置其中一个worker，其他的worker依然不会改变！

在task需要指定name，例如`model_flow.celery_tasks.tasks.train`，否则在外部引用的时候，会找不到task。

注意：`worker是独立的进程`，不同的worker也是独立的进程，他们之间没有共享数据，在`celery.conf`也共享不了。

### 启动
这个很简单

```sh
celery worker -A tasks.celery --loglevel=DEBUG
```

## 最后

- worker是独立的进程
- worker是独立的进程
- worker是独立的进程

重要的事情说三遍！！
