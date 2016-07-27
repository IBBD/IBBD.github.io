# [Golang]将IP地址转化为整型

为了减少存储空间，特别是缓存时，通常需要将ip地址转化为整型进行处理，实现如下：

```go
package IP

import (
	"errors"
	"net"
)

// 将IPv4地址转为uint32的结果类型
// 注意：ParseIP的结果
func Ip2uint(ip_str string) (uint32, error) {
	ip := net.ParseIP(ip_str)
	if ip == nil {
		return 0, errors.New("ParseIP error")
	}

	return uint32(ip[12])<<24 | uint32(ip[13])<<16 | uint32(ip[14])<<8 | uint32(ip[15]), nil
}
```

这里主要的坑是`net.ParseIP`函数的返回值，查了源码才确定其结构。


