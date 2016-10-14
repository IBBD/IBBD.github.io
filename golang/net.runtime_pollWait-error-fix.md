# net.runtime_pollWait问题解决过程（Golang）

## 错误信息

```
goroutine 20905 [runnable]:
net.runtime_pollWait(0x7fbdd84464f0, 0x77, 0xc43eb6d250)
	/home/ibbd/golang/go-go1.7.1/src/runtime/netpoll.go:160 +0x59
net.(*pollDesc).wait(0xc422969090, 0x77, 0xc43eb6d288, 0x4f99c5)
	/home/ibbd/golang/go-go1.7.1/src/net/fd_poll_runtime.go:73 +0x38
net.(*pollDesc).waitWrite(0xc422969090, 0x594198, 0x628280)
	/home/ibbd/golang/go-go1.7.1/src/net/fd_poll_runtime.go:82 +0x34
net.(*netFD).connect(0xc422969030, 0x628280, 0xc422616720, 0x0, 0x0, 0x626b00, 0xc427215000, 0x0, 0x0)
	/home/ibbd/golang/go-go1.7.1/src/net/fd_unix.go:152 +0x26a
net.(*netFD).dial(0xc422969030, 0x628280, 0xc422616720, 0x628560, 0x0, 0x628560, 0xc43c48f710, 0x10, 0x10)
	/home/ibbd/golang/go-go1.7.1/src/net/sock_posix.go:137 +0x137
net.socket(0x628280, 0xc422616720, 0x580d0d, 0x3, 0x2, 0x1, 0x0, 0x0, 0x628560, 0x0, ...)
	/home/ibbd/golang/go-go1.7.1/src/net/sock_posix.go:89 +0x209
net.internetSocket(0x628280, 0xc422616720, 0x580d0d, 0x3, 0x628560, 0x0, 0x628560, 0xc43c48f710, 0x1, 0x0, ...)
	/home/ibbd/golang/go-go1.7.1/src/net/ipsock_posix.go:158 +0x129
net.doDialTCP(0x628280, 0xc422616720, 0x580d0d, 0x3, 0x0, 0xc43c48f710, 0x658630, 0x0, 0x0)
	/home/ibbd/golang/go-go1.7.1/src/net/tcpsock_posix.go:58 +0xb9
net.dialTCP(0x628280, 0xc422616720, 0x580d0d, 0x3, 0x0, 0xc43c48f710, 0x0, 0xf1, 0x10)
	/home/ibbd/golang/go-go1.7.1/src/net/tcpsock_posix.go:54 +0xe4
net.dialSingle(0x628280, 0xc422616720, 0xc422968fc0, 0x627400, 0xc43c48f710, 0x0, 0x0, 0x0, 0x0)
	/home/ibbd/golang/go-go1.7.1/src/net/dial.go:501 +0x479
net.dialSerial(0x628280, 0xc422616720, 0xc422968fc0, 0xc424030e50, 0x1, 0x1, 0x0, 0x0, 0x0, 0x0)
	/home/ibbd/golang/go-go1.7.1/src/net/dial.go:469 +0x223
net.(*Dialer).DialContext(0xc420692d70, 0x628240, 0xc42000c528, 0x580d0d, 0x3, 0x582b5b, 0xe, 0x0, 0x0, 0x0, ...)
	/home/ibbd/golang/go-go1.7.1/src/net/dial.go:351 +0x657
net.(*Dialer).Dial(0xc420692d70, 0x580d0d, 0x3, 0x582b5b, 0xe, 0x0, 0x0, 0x0, 0x0)
	/home/ibbd/golang/go-go1.7.1/src/net/dial.go:282 +0x75
net.(*Dialer).Dial-fm(0x580d0d, 0x3, 0x582b5b, 0xe, 0x0, 0x0, 0x0, 0x0)
	/var/www/golang/src/github.com/garyburd/redigo/redis/conn.go:98 +0x52
github.com/garyburd/redigo/redis.Dial(0x580d0d, 0x3, 0x582b5b, 0xe, 0xc43eb6dc40, 0x3, 0x3, 0x5946a8, 0xc43eaca400, 0x5820d8, ...)
	/var/www/golang/src/github.com/garyburd/redigo/redis/conn.go:136 +0x147
github.com/garyburd/redigo/redis.DialTimeout(0x580d0d, 0x3, 0x582b5b, 0xe, 0x3b9aca00, 0x1dcd6500, 0x1dcd6500, 0xc42001612c, 0x29fd, 0x29fd00000000, ...)
	/var/www/golang/src/github.com/garyburd/redigo/redis/conn.go:64 +0x103
git.ibbd.net/dsp/test.init.1.func1(0xc42001612c, 0x0, 0x0, 0x0)
	/var/www/golang/src/git.ibbd.net/dsp/test/main.go:13 +0x6a
github.com/garyburd/redigo/redis.(*Pool).get(0xc420016100, 0x0, 0x0, 0x0, 0x0)
	/var/www/golang/src/github.com/garyburd/redigo/redis/pool.go:258 +0x6d0
github.com/garyburd/redigo/redis.(*Pool).Get(0xc420016100, 0x0, 0x0)
	/var/www/golang/src/github.com/garyburd/redigo/redis/pool.go:158 +0x2f
git.ibbd.net/dsp/test.test2(0x3fd2)
	/var/www/golang/src/git.ibbd.net/dsp/test/main.go:27 +0x5a
created by git.ibbd.net/dsp/test.TestUseRedis
	/var/www/golang/src/git.ibbd.net/dsp/test/main_test.go:12 +0x4d
```

## 相应代码

main.go：

```go
package main

import (
	"fmt"
	"github.com/garyburd/redigo/redis"
	"time"
)

var redisPool *redis.Pool

func init() {
	dialFunc := func() (c redis.Conn, err error) {
		c, err := redis.DialTimeout("tcp", "127.0.0.1:6379", time.Second, time.Millisecond*500, time.Millisecond*500)
		return
	}
	redisPool = &redis.Pool{
		MaxIdle:     10000,
		MaxActive:   5000,
		IdleTimeout: time.Second,
		Dial:        dialFunc,
		Wait:        true,
	}

}

func test2(i int) {
	c := redisPool.Get()
	defer c.Close()

	for i := 0; i < 10; i++ {
		_, err := c.Do("SET", "x", i)
		if err != nil {
			fmt.Println("GET: " + err.Error())
		}

		_, err = c.Do("GET", "x")
		if err != nil {
			fmt.Println("GET: " + err.Error())
		}
	}
	//fmt.Println(redisPool.ActiveCount())
}
```

main_test.go

```go
package main

import (
	"testing"
	"time"
)

func TestUseRedis(t *testing.T) {
	var n int = 5000

	for i := 0; i < n; i++ {
		go test2(i)
	}

	time.Sleep(time.Second * 2)

	for i := 0; i < n; i++ {
		go test2(i)
	}

	time.Sleep(time.Second * 2)

	begin := time.Now()
	for i := 0; i < n; i++ {
		go test2(i)
	}
	println(time.Now().Sub(begin).Nanoseconds())
}
```

执行`go test`时，有时就会报开头所出现的错误。

## 过程

暂时没有更好的解决方法，将连接池大小设置为cpu核数的2倍，就测试数据看，这个性能是比较高的。

---------

Date: 2016-10-14  Author: alex cai <cyy0523xc@gmail.com>
