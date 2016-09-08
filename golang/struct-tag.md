# （Golang）struct中tag的获取与操作

tag是其他语言比较少见的特性，只在反射的时候有用。

```go
package main

import (
	"fmt"
	"reflect"
)

type TagType struct {
	field1 bool   "An important answer"
	field2 string `hello:"The name of the thing" world:""`
	field3 int    `how much there are`
	field4 int    `hello:"hello value" world:"world value"`
}

func main() {
	tt := TagType{true, "Barak Obama", 1, 100}
	var reflectType reflect.Type = reflect.TypeOf(tt)
	var field reflect.StructField
	for i := 0; i < reflectType.NumField(); i++ {
		field = reflectType.Field(i)
		fmt.Printf("%+v\n", field)
		fmt.Printf("%s\n", field.Tag)
		fmt.Printf("%s\n", field.Type)

		if i == 3 {
			fmt.Printf("hello: %s\n", field.Tag.Get("hello"))
			fmt.Printf("world: %s\n", field.Tag.Get("world"))
		}

		if world, ok := field.Tag.Lookup("world"); ok {
			if world == "" {
				fmt.Println("(blank)")
			} else {
				fmt.Println(world)
			}
		} else {
			fmt.Println("(not specified)")
		}
	}
}
```


