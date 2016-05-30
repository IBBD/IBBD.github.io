# （Golang）struct中的tag

tag是其他语言比较少见的特性，只在反射的时候有用。

```go
package main

import (
	"fmt"
	"reflect"
)

type Ts struct {
	a string `json:"species=gopher;color=blue" ibbd:"test2"`
	b string `json:"b" ibbd:"test"`
}

func main() {
	ts := &Ts{
		a: "tes",
		b: "tes",
	}
	fmt.Printf("\n%+v  ", ts)
	s := reflect.TypeOf(ts).Elem()
	for i := 0; i < s.NumField(); i++ {
		fmt.Println("====")
		fmt.Printf("\njson: %s  ", s.Field(i).Tag.Get("json")) //将tag输出出来
		fmt.Printf("\nibbd: %s  ", s.Field(i).Tag.Get("ibbd")) //将tag输出出来
		fmt.Println(s.Field(i).Type)                           //将字段的类型打印出来
	}

}
```


