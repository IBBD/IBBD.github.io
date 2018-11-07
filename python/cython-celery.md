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


## 

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
