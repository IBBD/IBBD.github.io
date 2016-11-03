# Golang Tips

## 201611

```go
// 时间的妙用
// 这样在单元测试时，就可以对它进行覆盖，方便对时间的测试。
var nowFunc = time.Now

// 空结构体
// 对于空结构体，其实际存储空间为0
// 非常适合用来做通知chan
var c chan struct{}
```




