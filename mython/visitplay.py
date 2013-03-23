#! /usr/bin/env python
# ______________________________________________________________________

__DEBUG__ = False

# ______________________________________________________________________

def visitation_generator(tree, builder):
    data, children = tree
    child_count = len(children)
    if child_count > 0:
        for child in children:
            yield child
        transformed_children = builder[-child_count:]
        del builder[-child_count:]
    else:
        transformed_children = []
    builder.append((data, transformed_children))

def visit(tree):
    builder = []
    generators = [visitation_generator(tree, builder)]
    while generators:
        #for child in generators[-1]: # XXX Why doesn't this work?
        try:
            child = next(generators[-1])
            try:
                generators.append(visitation_generator(child, builder))
            except StopIteration:
                pass
        except StopIteration:
            del generators[-1]
    return builder[-1]

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
    t0 = (0,[])
    t1 = (1,[t0])
    t2 = (2,[t1])
    trees = [t0,t1,t2,(1, [(2, []), (3, [(4, []), (5, [])])])]
    for tree in trees:
        result0 = visit(tree)
        assert result0 == tree, '%s != %s' % (result0, tree)
        result1 = TrampolineVisitor().trampoline_visit(tree)
        assert result1 == tree, '%s != %s' % (result1, tree)

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of visitplay.py
