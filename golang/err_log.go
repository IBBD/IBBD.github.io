package main

import (
	"errors"
	"fmt"
	"log"
	"os"
)

// Logger is used to log critical error messages.
type Logger interface {
	Print(v ...interface{})
}

var errLog = Logger(log.New(os.Stderr, "[debug] ", log.Ldate|log.Ltime|log.Lshortfile))

func main() {
	tmp := log.New(os.Stderr, "[debug] ", log.Ldate|log.Ltime|log.Lshortfile)
	tmp.Print("hello world")
	errLog.Print("hello world")
	tmp.Print(errors.New("Error hello"))
	errLog.Print(errors.New("Error hello"))
	fmt.Printf("%T ==> %T\n", tmp, errLog)
}
