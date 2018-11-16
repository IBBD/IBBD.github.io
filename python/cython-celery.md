# cython编译celery相关项目时的大坑

## 函数的参数问题

在使用Cython编译后，有的函数被调用时，会爆出一个无参数的TypeError：

```
func() takes no keyword arguments
```

在Bottle框架(一个Web框架)的issue中有人也遇到这种问题。

通过这里给出的方法我们对报出Error的方法进行修改。

例如：

```python
# 原来
def sum(a,b): pass
# 修改后
def sum(a=None, b=None): pass
```

这样可以将问题解决。


## 不使用cython来编译celery部分的代码

```
'method-wrapper' object has no attribute '__module__'
Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/celery/local.py", line 317, in _get_current_object
    return object.__getattribute__(self, '__thing')
AttributeError: 'PromiseProxy' object has no attribute '__thing'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/flask/app.py", line 1813, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.6/site-packages/flask/app.py", line 1799, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "model_flow/server/model_api.py", line 93, in model_flow.server.model_api.model_train_api
  File "model_flow/celery_tasks/tasks.py", line 17, in model_flow.celery_tasks.tasks.decorator_model.call
  File "/usr/local/lib/python3.6/site-packages/celery/local.py", line 146, in __getattr__
    return getattr(self._get_current_object(), name)
  File "/usr/local/lib/python3.6/site-packages/celery/local.py", line 319, in _get_current_object
    return self.__evaluate__()
  File "/usr/local/lib/python3.6/site-packages/celery/local.py", line 349, in __evaluate__
    thing = Proxy._get_current_object(self)
  File "/usr/local/lib/python3.6/site-packages/celery/local.py", line 109, in _get_current_object
    return loc(*self.__args, **self.__kwargs)
  File "/usr/local/lib/python3.6/site-packages/celery/app/base.py", line 445, in _task_from_fun
    '__header__': staticmethod(head_from_fun(fun, bound=bind)),
  File "/usr/local/lib/python3.6/site-packages/celery/utils/functional.py", line 278, in head_from_fun
    namespace = {'__name__': fun.__module__}
AttributeError: 'method-wrapper' object has no attribute '__module__'
```

## 下面这个问题会导致worker容器挂掉

```
[2018-11-16 10:53:10,146: CRITICAL/MainProcess] Unrecoverable error: AttributeError("'float' object has no attribute 'items'",)
Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/celery/worker/worker.py", line 205, in start
    self.blueprint.start(self)
  File "/usr/local/lib/python3.6/site-packages/celery/bootsteps.py", line 119, in start
    step.start(parent)
  File "/usr/local/lib/python3.6/site-packages/celery/bootsteps.py", line 369, in start
    return self.obj.start()
  File "/usr/local/lib/python3.6/site-packages/celery/worker/consumer/consumer.py", line 317, in start
    blueprint.start(self)
  File "/usr/local/lib/python3.6/site-packages/celery/bootsteps.py", line 119, in start
    step.start(parent)
  File "/usr/local/lib/python3.6/site-packages/celery/worker/consumer/consumer.py", line 593, in start
    c.loop(*c.loop_args())
  File "/usr/local/lib/python3.6/site-packages/celery/worker/loops.py", line 91, in asynloop
    next(loop)
  File "/usr/local/lib/python3.6/site-packages/kombu/asynchronous/hub.py", line 354, in create_loop
    cb(*cbargs)
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/redis.py", line 1040, in on_readable
    self.cycle.on_readable(fileno)
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/redis.py", line 337, in on_readable
    chan.handlers[type]()
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/redis.py", line 724, in _brpop_read
    self.connection._deliver(loads(bytes_to_str(item)), dest)
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/virtual/base.py", line 983, in _deliver
    callback(message)
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/virtual/base.py", line 632, in _callback
    self.qos.append(message, message.delivery_tag)
  File "/usr/local/lib/python3.6/site-packages/kombu/transport/redis.py", line 149, in append
    pipe.zadd(self.unacked_index_key, time(), delivery_tag) \
  File "/usr/local/lib/python3.6/site-packages/redis/client.py", line 2263, in zadd
    for pair in iteritems(mapping):
  File "/usr/local/lib/python3.6/site-packages/redis/_compat.py", line 123, in iteritems
    return iter(x.items())
AttributeError: 'float' object has no attribute 'items'
```

因为镜像重新编译之前是没有问题的，错误信息也提到了redis，故怀疑是celery或者redis包的版本问题（redis镜像本身并没有更新），使用pip list命令对比：

```
# 旧版本镜像
celery              4.2.1
redis               2.10.6 

# 新版本镜像
celery              4.2.1
redis               3.0.1
```

前后使用的redis镜像版本一致：

```
redis-server -v
Redis server v=5.0.0 sha=00000000:0 malloc=jemalloc-5.1.0 bits=64 build=9a5fa86bdce33ad2
```

试着将redis镜像更新到最新版本看是否能解决:

```
Redis server v=5.0.1 sha=00000000:0 malloc=jemalloc-5.1.0 bits=64 build=29efca43cc88267
```

事实问题依旧。

在github上查到问题：https://github.com/celery/celery/issues/5175

需要将redis package包版本暂时回退到`pip install redis==2.10.6`





