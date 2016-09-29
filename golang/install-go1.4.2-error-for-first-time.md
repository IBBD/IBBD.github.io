# 首次安装Go1.4.2碰到的一个错误

刚想在笔记本配置go1.7.1的环境，却在安装1.4.2版本时报错了，如下：

```
# cmd/go
/home/alex/programs/go-go1.4.2/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
/home/alex/programs/go-go1.4.2/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
runtime/cgo(.text): unexpected relocation type 298
runtime/cgo(.text): unexpected relocation type 298
# cmd/pprof
/home/alex/programs/go-go1.4.2/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
/home/alex/programs/go-go1.4.2/pkg/linux_amd64/runtime/cgo.a(_all.o): unknown relocation type 42; compiled without -fpic?
runtime/cgo(.text): unexpected relocation type 298
runtime/cgo(.text): unexpected relocation type 298
```

解决方法很简单：

```sh
# 注意：下面这个命令是一行的，不要拆分成两行执行
CGO_ENABLED=0 ./make.bash
```

来源：http://stackoverflow.com/questions/37192696/error-building-go-compiler-from-source



---------

Date: 2016-09-29  Author: alex <alex@ibbd.net>
