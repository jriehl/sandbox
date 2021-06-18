/* goplay: Reads a Go source file and print its AST.
   Example:
   $ go build ./cmd/goplay && ./goplay cmd/goplay/main.go
*/

package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments)
	if err != nil {
		panic(err)
	}
	var buf bytes.Buffer
	ast.Fprint(&buf, fset, node, nil)
	fmt.Println(buf.String())
	os.Exit(0)
}
