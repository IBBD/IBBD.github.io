# 使用锁数组来避免全局锁，提升map结构的并发性能（golang）

在map结构中，判断数据是否存在通常都得加锁，而且这个锁还是全局的，锁的粒度太大，非常影响并发的性能。

## 使用锁数组来提升map的并发性能

```go
package main

import (
	"sync"
)

type TData struct {
	// 锁数组，避免全局锁，影响并发
	rws [128]sync.RWMutex

	// 实际数据
	data map[uint32]string
}

func main() {
	data := &TData{}

	uid := 1010
	key := uid & 127
	data.rws[key].Lock()
	if _, ok := data.data[uid]; !ok {
		// 设置数据
		data.data[uid] = "hello world"
	}
	data.rws[key].Unlock()
}

