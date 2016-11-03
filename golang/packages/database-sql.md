# database/sql包源码学习（Golang）

在平常开发时，数据库几乎是必备的，在使用`database/sql`包时却经常遇到种种问题。最重要的结论：

- Open返回的DB句柄是协程安全的，可以被众多协程共用，通常不需要调用DB.Close
- sql操作很重，如果可能，应该尽量使用缓存或者异步
- database/sql包有自动重试等功能，外部通常不需要自己实现
- 对于普通的sql，通常不要试图使用Prepare来优化查询
- rows.Scan之后，一定要Close

## 关于连接池

- 避免错误操作，例如LOCK TABLE后用 INSERT会死锁，因为两个操作不是同一个连接，insert的连接没有table lock。
- 当需要连接，且连接池中没有可用连接时，新的连接就会被创建。
- 默认没有连接上限，你可以设置一个，但这可能会导致数据库产生错误“too many connections”
- db.SetMaxIdleConns(N)设置最大空闲连接数
- db.SetMaxOpenConns(N)设置最大打开连接数
- 长时间保持空闲连接可能会导致db timeout

## 重要数据结构

### sql.DB

DB是数据库句柄，它包含着一个连接池，里面可以有0个或者多个连接。对于多协程的并发调用，它也是安全的。

sql包会自动的创建和释放连接池中的连接，也能保持一个空闲连接的连接池。在事务中，一旦`DB.Begin`被调用，其返回的Tx对象就是绑定到一个单独的连接上，直到事务提交或者回滚，这个连接才会重新被返回空闲连接池。

连接池的大小可以由方法`SetMaxIdleConns`控制。

```go
type DB struct {
	driver driver.Driver
	dsn    string
	// numClosed is an atomic counter which represents a total number of
	// closed connections. Stmt.openStmt checks it before cleaning closed
	// connections in Stmt.css.
	numClosed uint64

	mu           sync.Mutex // protects following fields
	freeConn     []*driverConn
	connRequests []chan connRequest
	numOpen      int // 已经打开的和将要打开的连接的总数

    // 用来接收创建新连接的信号
    // connectionOpener方法会读取该channel的信号，而当需要创建连接的时候，maybeOpenNewConnections就会往该channel发信号。
    // 当调用db.Close()的时候，该channel就会被关闭
	openerCh    chan struct{}
	closed      bool
	dep         map[finalCloser]depSet
	lastPut     map[*driverConn]string // stacktrace of last conn's put; debug only
	maxIdle     int                    // zero means defaultMaxIdleConns; negative means 0
	maxOpen     int                    // <= 0 means unlimited
	maxLifetime time.Duration          // maximum amount of time a connection may be reused
	cleanerCh   chan struct{}
}
```

## sql.Open方法

注意：该方法只是校验了参数，但是并没有真正创建到数据的连接，如果需要验证数据源是否ok，则需要调用`Ping`方法。

该方法返回的DB对象是线程安全的，可以放心使用，它自己会保持一个空闲的连接池。所以，Open方法在程序里应该只被调用一次，通常情况是不需要去关闭的。
```go
func Open(driverName, dataSourceName string) (*DB, error) {
	driversMu.RLock()
	driveri, ok := drivers[driverName]
	driversMu.RUnlock()
	if !ok {
		return nil, fmt.Errorf("sql: unknown driver %q (forgotten import?)", driverName)
	}
	db := &DB{
		driver:   driveri,
		dsn:      dataSourceName,
		openerCh: make(chan struct{}, connectionRequestQueueSize),
		lastPut:  make(map[*driverConn]string),
	}

    // 这是关键一步
	go db.connectionOpener()
	return db, nil
}

// Runs in a separate goroutine, opens new connections when requested.
func (db *DB) connectionOpener() {
	for range db.openerCh {
		db.openNewConnection()
	}
}

// Open one new connection
func (db *DB) openNewConnection() {
    // 在发送到db.openerCh之前，maybeOpenNewConnections之前已经将numOpen++
    // 如果新连接创建失败，或者已经被关闭，则在返回之前必须减1
	ci, err := db.driver.Open(db.dsn)

    // 创建连接的过程加了互斥锁
	db.mu.Lock()
	defer db.mu.Unlock()
	if db.closed {
		if err == nil {
			ci.Close()
		}
		db.numOpen--
		return
	}
	if err != nil {
		db.numOpen--
		db.putConnDBLocked(nil, err)
		db.maybeOpenNewConnections()
		return
	}
	dc := &driverConn{
		db:        db,
		createdAt: nowFunc(),
		ci:        ci,
	}
	if db.putConnDBLocked(dc, err) {
		db.addDepLocked(dc, dc)
	} else {
		db.numOpen--
		ci.Close()
	}
}

// 如果有连接请求，并且连接数还没达到上限，就通知connectionOpener创建新的连接
func (db *DB) maybeOpenNewConnections() {
	numRequests := len(db.connRequests)
	if db.maxOpen > 0 {
		numCanOpen := db.maxOpen - db.numOpen
		if numRequests > numCanOpen {
			numRequests = numCanOpen
		}
	}
	for numRequests > 0 {
		db.numOpen++ // optimistically
		numRequests--
		if db.closed {
			return
		}
		db.openerCh <- struct{}{}
	}
}
```

## DB.Close

关闭数据库，并释放所有相关资源。

再次强调：**通常不需要执行该操作**。DB句柄应该是长期生存的，可以安全的共享于众多的协程中。

```go
func (db *DB) Close() error {
	db.mu.Lock()
	if db.closed { // Make DB.Close idempotent
		db.mu.Unlock()
		return nil
	}
	close(db.openerCh)
	if db.cleanerCh != nil {
		close(db.cleanerCh)
	}
	var err error
	fns := make([]func() error, 0, len(db.freeConn))
	for _, dc := range db.freeConn {
		fns = append(fns, dc.closeDBLocked())
	}
	db.freeConn = nil
	db.closed = true
	for _, req := range db.connRequests {
		close(req)
	}
	db.mu.Unlock()
	for _, fn := range fns {
		err1 := fn()
		if err1 != nil {
			err = err1
		}
	}
	return err
}

```

## DB.Query

查询时基本都得用到这个方法。

```go
// Query executes a query that returns rows, typically a SELECT.
// The args are for any placeholder parameters in the query.
func (db *DB) Query(query string, args ...interface{}) (*Rows, error) {
	return db.QueryContext(context.Background(), query, args...)
}

// QueryContext executes a query that returns rows, typically a SELECT.
// The args are for any placeholder parameters in the query.
func (db *DB) QueryContext(ctx context.Context, query string, args ...interface{}) (*Rows, error) {
	var rows *Rows
	var err error
    // maxBadConnRetries是一个常量，值为2
	for i := 0; i < maxBadConnRetries; i++ {
		// cacheOrNewConn: 是获取连接策略常量，优先从连接池中获取一个可用的连接，如果没有可用连接，此时如果连接数已经达到上限，则等待，否则则直接创建一个新连接。
		rows, err = db.query(ctx, query, args, cachedOrNewConn)
		// 如果连接异常，则重试
		if err != driver.ErrBadConn {
			break
		}
	}
	if err == driver.ErrBadConn {
		// 再重试一遍，使用创建连接的策略
		return db.query(ctx, query, args, alwaysNewConn)
	}
	return rows, err
}

func (db *DB) query(ctx context.Context, query string, args []interface{}, strategy connReuseStrategy) (*Rows, error) {
	ci, err := db.conn(ctx, strategy)
	if err != nil {
		return nil, err
	}

    // 执行查询
	return db.queryConn(ctx, ci, ci.releaseConn, query, args)
}

// connRequest represents one request for a new connection
// When there are no idle connections available, DB.conn will create
// a new connRequest and put it on the db.connRequests list.
type connRequest struct {
	conn *driverConn
	err  error
}

var errDBClosed = errors.New("sql: database is closed")

// conn 获取一个缓存中的或者新打开的连接
func (db *DB) conn(ctx context.Context, strategy connReuseStrategy) (*driverConn, error) {
	db.mu.Lock()
	if db.closed {
		db.mu.Unlock()
		// 如果数据库已经关闭，会直接返回错误，而且外部不会对这个错误做处理
		return nil, errDBClosed
	}
	// Check if the context is expired.
	if err := ctx.Err(); err != nil {
		db.mu.Unlock()
		return nil, err
	}
	lifetime := db.maxLifetime

	// 如果可能，返回一个空闲的连接
	numFree := len(db.freeConn)
	if strategy == cachedOrNewConn && numFree > 0 {
		// 取第一个空闲连接，并生成新的空闲连接列表
		// 问题是：如果开始将连接全部放到一个数组里，然后只是标注那些已经使用，这样效率会不会更好
		conn := db.freeConn[0]
		copy(db.freeConn, db.freeConn[1:])
		db.freeConn = db.freeConn[:numFree-1]
		conn.inUse = true
		db.mu.Unlock()
		if conn.expired(lifetime) {
			// 如果超时了，则关闭该连接，返回该错误时，外部会重试
			conn.Close()
			return nil, driver.ErrBadConn
		}
		return conn, nil
	}

	// Out of free connections or we were asked not to use one. If we're not
	// allowed to open any more connections, make a request and wait.
	if db.maxOpen > 0 && db.numOpen >= db.maxOpen {
		// Make the connRequest channel. It's buffered so that the
		// connectionOpener doesn't block while waiting for the req to be read.
		req := make(chan connRequest, 1)
		db.connRequests = append(db.connRequests, req)
		db.mu.Unlock()

		// Timeout the connection request with the context.
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case ret, ok := <-req:
			if !ok {
				return nil, errDBClosed
			}
			if ret.err == nil && ret.conn.expired(lifetime) {
				ret.conn.Close()
				return nil, driver.ErrBadConn
			}
			return ret.conn, ret.err
		}
	}

	db.numOpen++ // optimistically
	db.mu.Unlock()
	ci, err := db.driver.Open(db.dsn)
	if err != nil {
		db.mu.Lock()
		db.numOpen-- // correct for earlier optimism
		db.maybeOpenNewConnections()
		db.mu.Unlock()
		return nil, err
	}
	db.mu.Lock()
	dc := &driverConn{
		db:        db,
		createdAt: nowFunc(),
		ci:        ci,
	}
	db.addDepLocked(dc, dc)
	dc.inUse = true
	db.mu.Unlock()
	return dc, nil
}


// queryConn 执行查询
// The connection gets released by the releaseConn function.
func (db *DB) queryConn(ctx context.Context, dc *driverConn, releaseConn func(error), query string, args []interface{}) (*Rows, error) {
	if queryer, ok := dc.ci.(driver.Queryer); ok {
		dargs, err := driverArgs(nil, args)
		if err != nil {
			releaseConn(err)
			return nil, err
		}
		var rowsi driver.Rows
		withLock(dc, func() {
			rowsi, err = ctxDriverQuery(ctx, queryer, query, dargs)
		})
		if err != driver.ErrSkip {
			if err != nil {
				releaseConn(err)
				return nil, err
			}
			// Note: ownership of dc passes to the *Rows, to be freed
			// with releaseConn.
			rows := &Rows{
				dc:          dc,
				releaseConn: releaseConn,
				rowsi:       rowsi,
			}
			rows.initContextClose(ctx)
			return rows, nil
		}
	}

	var si driver.Stmt
	var err error
	withLock(dc, func() {
		si, err = ctxDriverPrepare(ctx, dc.ci, query)
	})
	if err != nil {
		releaseConn(err)
		return nil, err
	}

	ds := driverStmt{dc, si}
	rowsi, err := rowsiFromStatement(ctx, ds, args...)
	if err != nil {
		withLock(dc, func() {
			si.Close()
		})
		releaseConn(err)
		return nil, err
	}

	// Note: ownership of ci passes to the *Rows, to be freed
	// with releaseConn.
	rows := &Rows{
		dc:          dc,
		releaseConn: releaseConn,
		rowsi:       rowsi,
		closeStmt:   si,     // close的时候，这个也需要关闭
	}
	rows.initContextClose(ctx)
	return rows, nil
}
```
## Rows.Next

为Scan方法准备下一行结果，如果成功则返回true，而没有更多下一行或者错误发生时，则返回false

注意：每次调用Scan之前，必须先调用Next

```go
func (rs *Rows) Next() bool {
	if rs.isClosed() {
		return false
	}
	if rs.lastcols == nil {
		rs.lastcols = make([]driver.Value, len(rs.rowsi.Columns()))
	}
	rs.lasterr = rs.rowsi.Next(rs.lastcols)
	if rs.lasterr != nil {
		// Close the connection if there is a driver error.
		if rs.lasterr != io.EOF {
			rs.Close()
			return false
		}
		nextResultSet, ok := rs.rowsi.(driver.RowsNextResultSet)
		if !ok {
			rs.Close()
			return false
		}
		// The driver is at the end of the current result set.
		// Test to see if there is another result set after the current one.
		// Only close Rows if there is no futher result sets to read.
		if !nextResultSet.HasNextResultSet() {
			rs.Close()
		}
		return false
	}
	return true
}
```

## Rows.Scan

```go
// Scan copies the columns in the current row into the values pointed
// at by dest. The number of values in dest must be the same as the
// number of columns in Rows.
//
// Scan 会将数据库的字段转化为Go能识别的字段：
//
//    *string
//    *[]byte
//    *int, *int8, *int16, *int32, *int64
//    *uint, *uint8, *uint16, *uint32, *uint64
//    *bool
//    *float32, *float64
//    *interface{}
//    *RawBytes
//    any type implementing Scanner (see Scanner docs)
//
// In the most simple case, if the type of the value from the source
// column is an integer, bool or string type T and dest is of type *T,
// Scan simply assigns the value through the pointer.
//
// Scan 也能在字符串类型和数值类型之间转换，只要转换的过程中没有信息丢失。
// 例如一个float64类型的300或者string类型的300,都能自动转换为uint16，但是不能转为uint8，因为已经超过其最大值
// One exception is that scans of some float64 numbers to
// strings may lose information when stringifying. In general, scan
// floating point columns into *float64.
//
// If a dest argument has type *[]byte, Scan saves in that argument a
// copy of the corresponding data. The copy is owned by the caller and
// can be modified and held indefinitely. The copy can be avoided by
// using an argument of type *RawBytes instead; see the documentation
// for RawBytes for restrictions on its use.
//
// If an argument has type *interface{}, Scan copies the value
// provided by the underlying driver without conversion. When scanning
// from a source value of type []byte to *interface{}, a copy of the
// slice is made and the caller owns the result.
//
// Source values of type time.Time may be scanned into values of type
// *time.Time, *interface{}, *string, or *[]byte. When converting to
// the latter two, time.Format3339Nano is used.
//
// Source values of type bool may be scanned into types *bool,
// *interface{}, *string, *[]byte, or *RawBytes.
//
// For scanning into *bool, the source may be true, false, 1, 0, or
// string inputs parseable by strconv.ParseBool.
func (rs *Rows) Scan(dest ...interface{}) error {
	if rs.isClosed() {
		return errors.New("sql: Rows are closed")
	}
	if rs.lastcols == nil {
		return errors.New("sql: Scan called without calling Next")
	}
	if len(dest) != len(rs.lastcols) {
		return fmt.Errorf("sql: expected %d destination arguments in Scan, not %d", len(rs.lastcols), len(dest))
	}
	for i, sv := range rs.lastcols {
		err := convertAssign(dest[i], sv)
		if err != nil {
			return fmt.Errorf("sql: Scan error on column index %d: %v", i, err)
		}
	}
	return nil
}
```

## Rows.Close

```go
var rowsCloseHook func(*Rows, *error)

// Close closes the Rows, preventing further enumeration. If Next is called
// and returns false and there are no further result sets,
// the Rows are closed automatically and it will suffice to check the
// result of Err. Close is idempotent and does not affect the result of Err.
func (rs *Rows) Close() error {
	if !atomic.CompareAndSwapInt32(&rs.closed, 0, 1) {
		return nil
	}
	if rs.ctxClose != nil {
		close(rs.ctxClose)
	}
	err := rs.rowsi.Close()
	if fn := rowsCloseHook; fn != nil {
		fn(rs, &err)
	}
	if rs.closeStmt != nil {
		rs.closeStmt.Close()
	}
	rs.releaseConn(err)
	return err
}
```

## DB.Prepare

在数据库层面，Prepared Statements是和单个数据库连接绑定的。客户端发送一个有占位符的statement到服务端，服务器返回一个statement ID，然后客户端发送ID和参数来执行statement。

当你生成一个Prepared Statement

- 自动在连接池中绑定到一个空闲连接
- Stmt对象记住绑定了哪个连接
- 执行Stmt时，尝试使用该连接。如果不可用，例如连接被关闭或繁忙中，会自动re-prepare，绑定到另一个连接。

这就导致在高并发的场景，过度使用statement可能导致statement泄漏，statement持续重复prepare和re-prepare的过程，甚至会达到服务器端statement数量上限。

某些操作使用了PS，例如db.Query(sql, param1, param2), 并在最后自动关闭statement。

```go
// Prepare creates a prepared statement for later queries or executions.
// Multiple queries or executions may be run concurrently from the
// returned statement.
// The caller must call the statement's Close method
// when the statement is no longer needed.
func (db *DB) Prepare(query string) (*Stmt, error) {
	return db.PrepareContext(context.Background(), query)
}

// PrepareContext creates a prepared statement for later queries or executions.
// Multiple queries or executions may be run concurrently from the
// returned statement.
// The caller must call the statement's Close method
// when the statement is no longer needed.
//
// The provided context is used for the preparation of the statement, not for the
// execution of the statement.
func (db *DB) PrepareContext(ctx context.Context, query string) (*Stmt, error) {
	var stmt *Stmt
	var err error
	for i := 0; i < maxBadConnRetries; i++ {
		stmt, err = db.prepare(ctx, query, cachedOrNewConn)
		if err != driver.ErrBadConn {
			break
		}
	}
	if err == driver.ErrBadConn {
		return db.prepare(ctx, query, alwaysNewConn)
	}
	return stmt, err
}

func (db *DB) prepare(ctx context.Context, query string, strategy connReuseStrategy) (*Stmt, error) {
	// TODO: check if db.driver supports an optional
	// driver.Preparer interface and call that instead, if so,
	// otherwise we make a prepared statement that's bound
	// to a connection, and to execute this prepared statement
	// we either need to use this connection (if it's free), else
	// get a new connection + re-prepare + execute on that one.
	dc, err := db.conn(ctx, strategy)
	if err != nil {
		return nil, err
	}
	var si driver.Stmt
	withLock(dc, func() {
		si, err = dc.prepareLocked(ctx, query)
	})
	if err != nil {
		db.putConn(dc, err)
		return nil, err
	}
	stmt := &Stmt{
		db:            db,
		query:         query,
		css:           []connStmt{{dc, si}},
		lastNumClosed: atomic.LoadUint64(&db.numClosed),
	}
	db.addDep(stmt, stmt)
	db.putConn(dc, nil)
	return stmt, nil
}

```
## Row.Scan

该方法在获取数据之前，会先调用Rows.Next来判断是否有记录，如果没有会返回`ErrNowRows`错误。其内部调用`Rows.Scan`方法获取数据。

如果结果集记录多于一条，则只返回第一条。并会调用Rows.Close来关闭。

```go
func (r *Row) Scan(dest ...interface{}) error {
	if r.err != nil {
		return r.err
	}

	// TODO(bradfitz): for now we need to defensively clone all
	// []byte that the driver returned (not permitting
	// *RawBytes in Rows.Scan), since we're about to close
	// the Rows in our defer, when we return from this function.
	// the contract with the driver.Next(...) interface is that it
	// can return slices into read-only temporary memory that's
	// only valid until the next Scan/Close. But the TODO is that
	// for a lot of drivers, this copy will be unnecessary. We
	// should provide an optional interface for drivers to
	// implement to say, "don't worry, the []bytes that I return
	// from Next will not be modified again." (for instance, if
	// they were obtained from the network anyway) But for now we
	// don't care.
	defer r.rows.Close()
	for _, dp := range dest {
		if _, ok := dp.(*RawBytes); ok {
			return errors.New("sql: RawBytes isn't allowed on Row.Scan")
		}
	}

	if !r.rows.Next() {
		if err := r.rows.Err(); err != nil {
			return err
		}
		return ErrNoRows
	}
	err := r.rows.Scan(dest...)
	if err != nil {
		return err
	}
	// Make sure the query can be processed to completion with no errors.
	if err := r.rows.Close(); err != nil {
		return err
	}

	return nil
}
```

## DB.Exec

这个的实现逻辑类似DB.Query，不再累赘。

## 参考

- [关于Golang中database/sql包的学习笔记](https://segmentfault.com/a/1190000003036452)
