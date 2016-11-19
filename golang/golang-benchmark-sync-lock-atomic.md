# 读多写少的场景下的并发优化(golang)

大部分场景下，数据都是读远远大于写的，在并发的时候，怎么避免读写冲突，是一个值得深思的问题。下面是对直接读，加互斥锁读，加读锁读，使用原子操作读的性能数据如下：

```
// 具体源码在文章附录
BenchmarkHelloNoLock-4   	2000000000	         1.15 ns/op
BenchmarkHelloLock-4     	20000000	        84.2 ns/op
BenchmarkHelloRLock-4    	30000000	        59.1 ns/op
BenchmarkHelloAtomic-4   	2000000000	         1.92 ns/op
```

效率上：`直接读 > 原子读 >> 读锁读 > 互斥锁读`

锁是很重的操作！

## 优化建议

- 使用原子操作替代锁，如果可以的话

## 一种优化的方案

适用场景：读操作远远多于写操作，写操作是通过后台任务的形式定时执行。

达到的目的：

- 大多数读操作都不需要加锁

```go
package main

import (
	"sync"
	"sync/atomic"
	"time"
)

type tHello struct {
	rw    sync.RWMutex
	tag   int32
	hello string
}

var helloT = &tHello{
	hello: "hello world",
}

func getHello() {
	// 大多数情况使用原子操作
	if atomic.LoadInt32(&tHello.tag) == 0 {
		return tHello.hello
	}

	// 正在更新的时候，才需要读锁
	tHello.rw.RLock()
	return tHello.hello
	tHello.rw.RUnlock()
}

// 定期执行的任务
func setHello() {
	// 增加读操作标识
	atomic.AddInt32(&tHello.tag, 1)

	// 延迟一小点时间，作为过度
	// 等待没有加的读操作完成
	time.Sleep(time.Microsecond)

	tHello.rw.Lock()
	// 这个时间是模拟加载数据的时间
	time.Sleep(time.Millisecond)
	tHello.rw.RUnlock()

	// 移除读操作标识
	atomic.AddInt32(&tHello.tag, -1)
}
```


## 性能测试源码

```go
package main

import (
	"sync"
	"sync/atomic"
	"testing"
)

type tHello struct {
	mu    sync.Mutex
	rw    sync.RWMutex
	tag   int32
	hello string
}

var helloT = &tHello{
	hello: "hello world",
}

func BenchmarkHelloNoLock(b *testing.B) {
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			_ = helloT.hello
		}
	})
}

func BenchmarkHelloLock(b *testing.B) {
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			helloT.mu.Lock()
			_ = helloT.hello
			helloT.mu.Unlock()
		}
	})
}

func BenchmarkHelloRLock(b *testing.B) {
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			helloT.rw.RLock()
			_ = helloT.hello
			helloT.rw.RUnlock()
		}
	})
}

func BenchmarkHelloAtomic(b *testing.B) {
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			if atomic.LoadInt32(&helloT.tag) == 0 {
				_ = helloT.hello
			}
		}
	})
}
```

