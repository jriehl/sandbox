package astplay

import (
	"fmt"
	"go/ast"
	"reflect"
	"strings"
)

/*
	Example of using the HandleNode() function.

	err = astplay.HandleNode(node, 0)
	if err != nil {
		panic(err)
	}
	fmt.Println("----------")
*/

func HandleDecls(decls []ast.Decl, depth int) error {
	for _, n := range decls {
		err := HandleNode(n, depth+1)
		if err != nil {
			return err
		}
	}
	return nil
}

func HandleStmts(stmts []ast.Stmt, depth int) error {
	for _, n := range stmts {
		err := HandleNode(n, depth+1)
		if err != nil {
			return err
		}
	}
	return nil
}

func HandleExprs(exprs []ast.Expr, depth int) error {
	for _, n := range exprs {
		err := HandleNode(n, depth+1)
		if err != nil {
			return err
		}
	}
	return nil
}

func HandleSpecs(specs []ast.Spec, depth int) error {
	for i, n := range specs {
		fmt.Println(strings.Repeat(" ", depth), i)
		err := HandleNode(n, depth+1)
		if err != nil {
			return err
		}
	}
	return nil
}

func HandleNode(node ast.Node, depth int) error {
	padding := strings.Repeat(" ", depth)
	switch n := node.(type) {
	// ______________________________________________________________________
	case *ast.File:
		fmt.Printf("%sAt a file node named: %v\n", padding, n.Name)
		err := HandleDecls(n.Decls, depth)
		if err != nil {
			return err
		}

	// ______________________________________________________________________
	case *ast.GenDecl:
		fmt.Println(padding, "GenDecl")
		err := HandleSpecs(n.Specs, depth)
		if err != nil {
			return err
		}

	case *ast.ImportSpec:
		fmt.Println(padding, "ImportSpec")

	case *ast.TypeSpec:
		fmt.Println(padding, "TypeSpec")

	case *ast.ValueSpec:
		fmt.Println(padding, "ValueSpec")

	// ______________________________________________________________________
	case *ast.FuncDecl:
		fmt.Println(padding, "FuncDecl")

	// ______________________________________________________________________
	default:
		return fmt.Errorf("unhandled node type %v", reflect.TypeOf(n))
	}
	return nil
}

// ____________________________________________________________________________
//
type ASTFrame struct {
	node     ast.Node
	depth    int
	children []*ASTFrame
}

type frameBuilder struct {
	root  *ASTFrame
	top   *ASTFrame
	stack []*ASTFrame
}

func NewASTFramePtr(node ast.Node) *ASTFrame {
	builder := frameBuilder{nil, nil, make([]*ASTFrame, 0)}
	ast.Walk(&builder, node)
	return builder.root
}

func (a *frameBuilder) Pop() {
	stackLen := len(a.stack)
	if stackLen == 0 {
		a.root = a.top
		a.top = nil
	} else {
		a.top = a.stack[stackLen-1]
		a.stack = a.stack[:stackLen-1]
	}
}

func (a *frameBuilder) Push(newTop *ASTFrame) {
	if a.top != nil {
		a.top.children = append(a.top.children, newTop)
		a.stack = append(a.stack, a.top)
	}
	a.top = newTop
}

func (a *frameBuilder) PushNode(node ast.Node) {
	newTop := &ASTFrame{node, len(a.stack), make([]*ASTFrame, 0)}
	if a.top != nil {
		newTop.depth += 1
		a.top.children = append(a.top.children, newTop)
		a.stack = append(a.stack, a.top)
	}
	a.top = newTop
}

func (a *frameBuilder) Visit(node ast.Node) ast.Visitor {
	if node == nil {
		a.Pop()
		return nil
	}
	a.PushNode(node)
	return a
}

func Display(a *ASTFrame) {
	padding := strings.Repeat("  ", a.depth)
	ty_str := reflect.TypeOf(a.node).String()[5:]
	fmtStr := `%s{"type": "%s", "start": "%v", "end": "%v", "children": [`
	fmt.Printf(fmtStr, padding, ty_str, a.node.Pos(), a.node.End())
	childCount := len(a.children)
	if childCount > 0 {
		fmt.Printf("\n")
		for i, child := range a.children {
			Display(child)
			if i < childCount-1 {
				fmt.Printf(",\n")
			}
		}
		fmt.Printf("\n%s", padding)
	}
	fmt.Printf("]}")
	if a.depth == 0 {
		fmt.Printf("\n")
	}
}
