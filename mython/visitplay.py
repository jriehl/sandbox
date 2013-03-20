#! /usr/bin/env python
# ______________________________________________________________________

__DEBUG__ = False

# ______________________________________________________________________

class TrampolineVisitor(object):
    def send(self, result):
        self.result = result

    def debugout(self, *args):
        print("%r: %s" % (self.visitor_stack[1:],
                          ''.join(str(x) for x in args)))

    def _visit(self, tree):
        if __DEBUG__:
            self.debugout("visiting ", tree)
        data, children = tree
        transformed_children = []
        for child in children:
            if __DEBUG__:
                self.debugout("visiting child ", child)
            transformed_child = yield True, child
            if __DEBUG__:
                self.debugout("transformed_child ", transformed_child)
            if transformed_child:
                transformed_children.append(transformed_child)
        yield False, (data, transformed_children)

    def trampoline_visit(self, tree):
        self.result = None
        self.visitor_stack = [self._visit(tree)]
        data = None
        while self.visitor_stack:
            if __DEBUG__:
                self.debugout("tos: ", self.visitor_stack[-1])
            push, data = self.visitor_stack[-1].send(data)
            if push:
                self.visitor_stack.append(self._visit(data))
                data = None
            else:
                del self.visitor_stack[-1]
        return data

# ______________________________________________________________________

def main(*args):
    tree = (1, [(2, []), (3, [(4, []), (5, [])])])
    result = TrampolineVisitor().trampoline_visit(tree)
    assert result == tree, '%s != %s' % (result, tree)

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of visitplay.py
