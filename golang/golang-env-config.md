# IBBD Golang开发环境配置

线上线下环境尽量保持一致

## 目录配置

- 代码目录: `/var/www/golang/src/git.ibbd.net/{group name}/{project name}`
- 日志目录: `/var/log/golang/`

## 环境变量

```
export GOPATH=/var/www/golang
```

## Docker容器配置

目录映射:

- `/var/www/golang/src/git.ibbd.net:/var/www`
- `/var/www/golang:/go`
- `/var/log/golang:/var/log/golang`

## 项目文件规范

- `init.go`: Golang一个package内只允许一个init函数, 如果文件比较多的话, 必然容易引起混乱, 因此应该独立到一个文件中.
- `common.go`: 在一个package内, 变量是公用的, 经常找不到在哪个文件中定义的, 如果文件比较多就显得很麻烦了, 因此一些公用的常量, 变量, 甚至函数(如果不能独立成文件), 都可以统一定义在common.go文件中.
- `env.go`: 环境等配置类常量及变量



