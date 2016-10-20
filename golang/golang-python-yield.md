# 使用Golang来模拟Python的yield

使用python都知道，有一个经常会用到的yield。使用channel，在golang中也能构造类似的用法：

```go
package main

import (
	"fmt"
)

func main() {
	c := yield()
	for val := range c {
		fmt.Println("out: %s", val)
		//c <- ""
	}
}

func yield() chan string {
	c := make(chan string)
	go func() {
		defer close(c)
		test := []string{"hello", "world", "1", "2", "3", "4"}
		for _, s := range test {
			c <- s
			//<-c
			fmt.Println("in: %s", s)
		}
	}()

	return c
}

```
在读数据库数据时，可以用类似的思路进行封装，不过协程的切换也是有性能损失的，需要做好衡量。
