/* goplay: Reads a Go source file and print its AST.
   Example:
   $ go build ./cmd/goplay && ./goplay cmd/goplay/main.go
*/

package main

import (
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
	err = ast.Print(fset, node)
	if err != nil {
		panic(err)
	}
	os.Exit(0)
}
