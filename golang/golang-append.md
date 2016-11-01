# Golang中append函数的性能分析

注意区分数组和切片的定义。

## 切片的两个重要特性

定义切片的几种方式：

```go
// 从数组里定义
var arr [10]int
slice1 := arr[2:5]
slice2 := arr[:0] // 空切片

// 直接定义
var slice3 []int

// 使用make
slice4 := make([]int, 4, 8)   // 这里4是切片长度，8是切片的容量

// 获取切片的长度和容量的方法
println(len(slice4), cap(slice4))

```
长度和容量是切片的两个重要属性。

## append函数的性能分析

先看这段程序的输出：

```go
	var b []int
	fmt.Printf("len = %d, cap=%d\n", len(b), cap(b))

	for i := 0; i < 10; i++ {
		b = append(b, i)
		fmt.Printf("len = %d, cap=%d\n", len(b), cap(b))
	}

	var c []int = make([]int, 0, 4)
	fmt.Printf("len = %d, cap=%d\n", len(c), cap(c))

	for i := 0; i < 10; i++ {
		c = append(c, i)
		fmt.Printf("len = %d, cap=%d\n", len(c), cap(c))
	}
```

输出结果如下：

```
len = 0, cap=0
len = 1, cap=1
len = 2, cap=2
len = 3, cap=4
len = 4, cap=4
len = 5, cap=8
len = 6, cap=8
len = 7, cap=8
len = 8, cap=8
len = 9, cap=16
len = 10, cap=16
len = 0, cap=4
len = 1, cap=4
len = 2, cap=4
len = 3, cap=4
len = 4, cap=4
len = 5, cap=8
len = 6, cap=8
len = 7, cap=8
len = 8, cap=8
len = 9, cap=16
len = 10, cap=16
```

总结：`使用append给一个切片增加数据的时候，如果切片的长度超过其容量，则容量会倍增。`

## 优化建议

- 在创建切片的时候，选择一个合理的初值，能减少容量的变化次数
- 容量的初值，应该设置为2的n次方

## 附录

- [数组、切片(以及字符串): append内置函数的运作机制](https://www.oschina.net/translate/go-lang-slices)

