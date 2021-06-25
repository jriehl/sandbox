/* goplay: Reads a Go source file and prints its AST.
   Example:
   $ go build ./cmd/goplay && ./goplay cmd/goplay/main.go
*/

package main

import (
	"go/parser"
	"go/token"
	"os"

	"github.com/jriehl/sandbox/tree/master/gobox/pkg/astplay"
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
	astplay.Display(astplay.NewASTFramePtr(node))
	os.Exit(0)
}
