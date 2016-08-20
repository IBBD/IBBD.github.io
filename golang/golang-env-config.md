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


