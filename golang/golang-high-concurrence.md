# Golang高并发编程

go能处理高并发的根本原因在于执行go协程只需极少的栈内存(大概4~5KB), 并且能根据需要动态增长和缩减占用的资源。

## 高并发的本质goroutine

简单而言,goroutine就是一段代码，一个函数入口，以及在堆上为其分配的一个堆栈。所以它非常廉价，我们可以很轻松的创建上万个goroutine，但它们并不是被操作系统所调度执行,而是通过系统的线程来多路派遣这些函数的执行，使得每个用go关键字执行的函数可以运行成为一个单位协程。当一个协程阻塞的时候，调度器就会自动把其他协程安排到另外的线程中去执行，从而实现了程序无等待并行化运行。而且调度的开销非常小，一颗CPU调度的规模不下于每秒百万次，这使得在程序中能够创建大量的goroutine，实现高并发的同时，依旧能保持高性能。

## Golang用于并发的特性或者包

- channel: 默认是双向的，可以定义为单向（发送或者接收）
- sync.Mutex：互斥锁
- sync.RWMutex: 读写锁. 读写锁分为读锁和写锁，读数据的时候上读锁，写数据的时候上写锁。有写锁的时候，数据不可读不可写。有读锁的时候，数据可读，不可写。 
- sync.WaitGroup: 任务组
- sync.Once: 保证Once只执行一次
- sync.Cond: 条件变量. 用来控制某个条件下，goroutine进入等待时期，等待信号到来，然后重新启动。
- sync.Pool: 临时对象池
- sync/atomic: 原子操作

## 依赖通讯来共享内存，而不是依赖共享内存来实现通讯

## 开启多核并行并发执行

默认情况下，go所有的goroutines是在一个线程中执行的，而不是同时利用多核进行并行执行，或者通过切换时间片让出CPU进行并发执行。下面看一段示例：

```go
func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	wg := sync.WaitGroup{}
	wg.Add(3)  // 增加了三个任务
	for i := 0; i < 3; i++ {
		go GoPrint(&wg)
	}

	wg.Wait() // 等待所有任务都执行完成
}

func GoPrint(wg *sync.WaitGroup) {
	for i := 0; i < 3; i++ {
		time.Sleep(time.Second)
		fmt.Printf("%d ", i)

	}
	wg.Done()  // 执行完一个任务
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

go通过Select可以同时处理多个Channel,Select默认是阻塞的，只有当监听的Channel中有发送或接收可以进行时才会运行,当同时有多个可用的Channel,Select按随机顺序进行处理,Select可以方便处理多Channel同时响应，在goroutine阻塞的情况也可以方便借助Select超时机制来解除阻塞僵局，下面来看一个示例:

```go
func getHttpRes(url string) (string, error) {
	res := make(chan *http.Response, 1)
	httpError := make(chan *error)
	go func() {
		resp, err := http.Get(url)
		if err != nil {
			httpError <- &err
		}
		res <- resp
	}()

	for {
		select {
		case r := <-res:
			result, err := ioutil.ReadAll(r.Body)
			defer r.Body.Close()
			return string(result), err
		case err := <-httpError:
			return "err", *err
		case <-time.After(2000 * time.Millisecond):
			return "Timed out", errors.New("Timed out")
		}
	}

}
```

## 原子操作

对于并发操作而言，原子操作是个非常现实的问题。典型的就是i++的问题。 当两个CPU同时对内存中的i进行读取，然后把加一之后的值放入内存中，可能两次i++的结果，这个i只增加了一次。 如何保证多CPU对同一块内存的操作是原子的。 golang中sync/atomic就是做这个使用的。

具体的原子操作在不同的操作系统中实现是不同的。比如在Intel的CPU架构机器上，主要是使用总线锁的方式实现的。 大致的意思就是当一个CPU需要操作一个内存块的时候，向总线发送一个LOCK信号，所有CPU收到这个信号后就不对这个内存块进行操作了。 等待操作的CPU执行完操作后，发送UNLOCK信号，才结束。 在AMD的CPU架构机器上就是使用MESI一致性协议的方式来保证原子操作。 所以我们在看atomic源码的时候，我们看到它针对不同的操作系统有不同汇编语言文件。

**如果我们善用原子操作，它会比锁更为高效。**

### CAS

原子操作中最经典的CAS(compare-and-swap)在atomic包中是Compare开头的函数。

CAS的意思是判断内存中的某个值是否等于old值，如果是的话，则赋new值给这块内存。CAS是一个方法，并不局限在CPU原子操作中。 CAS比互斥锁乐观，但是也就代表CAS是有赋值不成功的时候，调用CAS的那一方就需要处理赋值不成功的后续行为了。

这一系列的函数需要比较后再进行交换，也有不需要进行比较就进行交换的原子操作。

### 增加或减少

对一个数值进行增加或者减少的行为也需要保证是原子的，它对应于atomic包的函数就是Add开头的函数

### 读取或写入

当我们要读取一个变量的时候，很有可能这个变量正在被写入，这个时候，我们就很有可能读取到写到一半的数据。 所以读取操作是需要一个原子行为的。在atomic包中就是Load开头的函数群。

写入也是同样的，如果有多个CPU往内存中一个数据块写入数据的时候，可能导致这个写入的数据不完整。 在atomic包对应的是Store开头的函数群。

## 临时对象池

当多个goroutine都需要创建同一个对象的时候，如果goroutine过多，可能导致对象的创建数目剧增。 而对象又是占用内存的，进而导致的就是内存回收的GC压力徒增。造成“并发大－占用内存大－GC缓慢－处理并发能力降低－并发更大”这样的恶性循环。 在这个时候，我们非常迫切需要有一个对象池，每个goroutine不再自己单独创建对象，而是从对象池中获取出一个对象（如果池中已经有的话）。 这就是sync.Pool出现的目的了。

sync.Pool的使用非常简单，提供两个方法:Get和Put 和一个初始化回调函数New。

sync.Pool中的对象会在系统GC时，自动回收。回收之后再次Get，就会重新new一个对象，当并发大的时候，这也会造成相当的压力。所以，sync.Pool通常只适合用来做临时对象池，而不适合于持久场景（例如连接池）


## 附录

- [golang 并发concurrency 使用总结](http://www.grdtechs.com/2016/02/17/go-concurrency-summarize/)
- [谈谈go语言编程的并发安全](http://yanyiwu.com/work/2015/02/07/golang-concurrency-safety.html)
- [Benign data races: what could possibly go wrong?](https://software.intel.com/en-us/blogs/2013/01/06/benign-data-races-what-could-possibly-go-wrong)
- [sync](https://github.com/polaris1119/The-Golang-Standard-Library-by-Example/blob/master/chapter16/16.01.md)


