#! /usr/bin/env python
'''cfg_test.py

Tests various algorithms on control flow graphs.

FIXME: This class does NOT calculate the correct dominator
relationship.  See the fixed version in numba.cfg.ControlFlowGraph in
the actual numba repository.
'''
# ______________________________________________________________________

import pprint

# ______________________________________________________________________

class CFG (object):
    def __init__ (self):
        self.blocks = {}
        self.blocks_in = {}
        self.blocks_out = {}
        self.blocks_reads = {}
        self.blocks_writes = {}
        self.blocks_dom = {}

    def add_block (self, key, value):
        self.blocks[key] = value
        self.blocks_in[key] = set()
        self.blocks_out[key] = set()
        self.blocks_reads[key] = set()
        self.blocks_writes[key] = set()

    def add_edge (self, from_block, to_block):
        self.blocks_out[from_block].add(to_block)
        self.blocks_in[to_block].add(from_block)

    def compute_dom (self):
        '''Compute the dominator relationship in the CFG.'''
        raise NotImplementedError("FIXME: Incorrectly implemented the first "
                                  "time around.")
        for block in self.blocks.iterkeys():
            self.blocks_dom[block] = set((block,))
        changed = True
        while changed:
            changed = False
            for block in self.blocks.keys():
                olddom = self.blocks_dom[block]
                newdom = olddom.union(*[self.blocks_dom[pred]
                                        for pred in self.blocks_in[block]])
                if newdom != olddom:
                    changed = True
                    self.blocks_dom[block] = newdom
        return self.blocks_dom

    def idom (self, block):
        '''Compute the immediate dominator (idom) of the given block
        key.  Returns None if the block has no in edges.

        Note that in the case where there are multiple immediate
        dominators (a join after a non-loop branch), this returns one
        of the predecessors, but is not guaranteed to reliably select
        one over the others (depends on the order used by iterators
        over sets).

        Since our data structure stores back edges, we can skip the
        naive, O(n^2), approach to finding the idom of a given block.'''
        preds = self.blocks_in[block]
        npreds = len(preds)
        if npreds == 0:
            ret_val = None
        elif npreds == 1:
            ret_val = tuple(preds)[0]
        else:
            ret_val = [pred for pred in preds
                       if block not in self.blocks_dom[pred]][0]
        return ret_val

    def block_writes_to_writer_map (self, block):
        ret_val = {}
        for local in self.blocks_writes[block]:
            ret_val[local] = block
        return ret_val

    def get_reaching_definitions (self, block):
        '''Return a nested map for the given block
        s.t. ret_val[pred][local] equals the block key for the
        definition of local that reaches the argument block via that
        predecessor.

        Useful for actually populating phi nodes, once you know you
        need them.'''
        if hasattr(self, 'reaching_defns'):
            ret_val = self.reaching_defns
        else:
            preds = self.blocks_in[block]
            ret_val = {}
            for pred in preds:
                ret_val[pred] = self.block_writes_to_writer_map(pred)
                crnt = self.idom(pred)
                while crnt != None:
                    crnt_writer_map = self.block_writes_to_writer_map(crnt)
                    # This order of update favors the first definitions
                    # encountered in the traversal since the traversal
                    # visits blocks in reverse execution order.
                    crnt_writer_map.update(ret_val[pred])
                    ret_val[pred] = crnt_writer_map
                    crnt = self.idom(crnt)
            self.reaching_defns = ret_val
        return ret_val

    def nreaches (self, block):
        '''For each local, find the number of unique reaching
        definitions the current block has.'''
        # Slice and dice the idom tree so that each predecessor claims
        # at most one definition so we don't end up over or
        # undercounting.
        preds = self.blocks_in[block]
        idoms = {}
        idom_writes = {}
        # Fib a little here to truncate traversal in loops if they are
        # being chased before the actual idom of the current block has
        # been handled.
        visited = preds.copy()
        for pred in preds:
            idoms[pred] = set((pred,))
            idom_writes[pred] = self.blocks_writes[pred].copy()
            # Traverse up the idom tree, adding sets of writes as we
            # go.
            crnt = self.idom(pred)
            while crnt != None and crnt not in visited:
                idoms[pred].add(crnt)
                idom_writes[pred].update(self.blocks_writes[crnt])
                visited.add(crnt)
                crnt = self.idom(crnt)
        all_writes = set.union(*[idom_writes[pred] for pred in preds])
        ret_val = {}
        for local in all_writes:
            ret_val[local] = sum((1 if local in idom_writes[pred] else 0
                                  for pred in preds))
        return ret_val

    def phi_needed (self, join):
        '''Return the set of locals that will require a phi node to be
        generated at the given join.'''
        nreaches = self.nreaches(join)
        return set([local for local in nreaches.iterkeys()
                    if nreaches[local] > 1])

# ______________________________________________________________________

def build_test_cfg_1 ():
    cfg = CFG()
    for block_num in xrange(6):
        cfg.add_block(block_num, None)
    cfg.add_edge(0,1)
    cfg.add_edge(1,2)
    cfg.add_edge(2,3)
    cfg.add_edge(2,4)
    cfg.add_edge(4,1)
    cfg.add_edge(1,5)
    cfg.blocks_reads[1] = set((2,3))
    cfg.blocks_reads[2] = set((0,1,4,5,6))
    cfg.blocks_reads[3] = set((3,))
    cfg.blocks_reads[4] = set((3,))
    cfg.blocks_writes[0] = set((0,1,2,3,4,5))
    cfg.blocks_writes[2] = set((4,5,6))
    cfg.blocks_writes[4] = set((3,))
    return cfg

# ______________________________________________________________________

def build_test_cfg_2 ():
    cfg = CFG()
    for block_num in xrange(7):
        cfg.add_block(block_num, None)
    cfg.add_edge(0,6)
    cfg.add_edge(6,1)
    cfg.add_edge(1,2)
    cfg.add_edge(2,3)
    cfg.add_edge(2,4)
    cfg.add_edge(4,1)
    cfg.add_edge(1,5)
    cfg.blocks_reads[1] = set((2,3))
    cfg.blocks_reads[2] = set((0,1,4,5,6))
    cfg.blocks_reads[3] = set((3,))
    cfg.blocks_reads[4] = set((3,))
    cfg.blocks_writes[0] = set((0,1,2,3,4,5))
    cfg.blocks_writes[2] = set((4,5,6))
    cfg.blocks_writes[4] = set((3,))
    return cfg

# ______________________________________________________________________

def build_test_cfg_3 ():
    cfg = CFG()
    for block_num in xrange(4):
        cfg.add_block(block_num, None)
    cfg.add_edge(0,1)
    cfg.add_edge(0,2)
    cfg.add_edge(1,3)
    cfg.add_edge(2,3)
    cfg.blocks_reads[0] = set((0,))
    cfg.blocks_reads[3] = set((1,))
    cfg.blocks_writes[1] = set((1,))
    cfg.blocks_writes[2] = set((1,))
    return cfg

# ______________________________________________________________________

def main (*args, **kws):
    cfg = build_test_cfg_1()
    pprint.pprint(cfg.compute_dom())
    pprint.pprint(tuple(cfg.idom(block) for block in xrange(6)))
    pprint.pprint(cfg.nreaches(1))
    print "phi needed for", cfg.phi_needed(1)
    pprint.pprint(cfg.get_reaching_definitions(1))
    print "_" * 60
    cfg = build_test_cfg_2()
    pprint.pprint(cfg.compute_dom())
    pprint.pprint(cfg.nreaches(1))
    print "phi needed for", cfg.phi_needed(1)
    pprint.pprint(cfg.get_reaching_definitions(1))
    print "_" * 60
    cfg = build_test_cfg_3()
    pprint.pprint(cfg.compute_dom())
    pprint.pprint(cfg.nreaches(3))
    pprint.pprint(tuple(cfg.idom(block) for block in xrange(4)))
    print "phi needed for", cfg.phi_needed(3)
    pprint.pprint(cfg.get_reaching_definitions(3))

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of cfg_tests.py
