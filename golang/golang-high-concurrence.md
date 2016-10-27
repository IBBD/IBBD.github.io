# Golang高并发编程

go能处理高并发的根本原因在于执行go协程只需极少的栈内存(大概4~5KB), 并且能根据需要动态增长和缩减占用的资源。

## 高并发的本质goroutine

简单而言,goroutine就是一段代码，一个函数入口，以及在堆上为其分配的一个堆栈。所以它非常廉价，我们可以很轻松的创建上万个goroutine，但它们并不是被操作系统所调度执行,而是通过系统的线程来多路派遣这些函数的执行，使得每个用go关键字执行的函数可以运行成为一个单位协程。当一个协程阻塞的时候，调度器就会自动把其他协程安排到另外的线程中去执行，从而实现了程序无等待并行化运行。而且调度的开销非常小，一颗CPU调度的规模不下于每秒百万次，这使得在程序中能够创建大量的goroutine，实现高并发的同时，依旧能保持高性能。

## 依赖通讯来共享内存，而不是依赖共享内存来实现通讯

## 开启多核并行并发执行

默认情况下，go所有的goroutines是在一个线程中执行的，而不是同时利用多核进行并行执行，或者通过切换时间片让出CPU进行并发执行。下面看一段示例：

```go
func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	wg := sync.WaitGroup{}
	wg.Add(3)
	for i := 0; i < 3; i++ {
		go GoPrint(&wg)
	}

	wg.Wait()
}

func GoPrint(wg *sync.WaitGroup) {
	for i := 0; i < 3; i++ {
		time.Sleep(time.Second)
		fmt.Printf("%d ", i)

	}
	wg.Done()
}
```

## go并发执行安全问题

go的内存模型对于并发安全有两种保护措施。

- 一种是通过加锁来保护
- 一种是通过channel来保护

发现并发安全的有效命令：

```sh
go run main.go -race
```

## 一次写多次读，也要加锁保护

go语言编程中， 当有多个goroutine并发操作同一个变量时，除非是全都是只读操作， 否则就得【加锁】或者【使用channel】来保证并发安全。 不要觉得加锁麻烦，但是它能保证并发安全。

## 批量处理多个Channel操作

## 附录

- [golang 并发concurrency 使用总结](http://www.grdtechs.com/2016/02/17/go-concurrency-summarize/)
- [谈谈go语言编程的并发安全](http://yanyiwu.com/work/2015/02/07/golang-concurrency-safety.html)
- [Benign data races: what could possibly go wrong?](https://software.intel.com/en-us/blogs/2013/01/06/benign-data-races-what-could-possibly-go-wrong)

