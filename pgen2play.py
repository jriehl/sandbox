'''Tries to figure out how to use lib2to2.pgen2 to make a parser...
'''

import io
from lib2to3 import pytree
from lib2to3.pgen2 import pgen, driver

def pgenify(src):
    generator = pgen.ParserGenerator('<string>', io.StringIO(src))
    return generator.make_grammar()

calc_grammar = pgenify('''
statements: (statement NEWLINE)* ENDMARKER
statement: expr ['=' expr]
expr: atom [op expr]
atom: NAME | NUMBER
op: '+' | '-'
''')

calc_grammar.report()
dr = driver.Driver(calc_grammar, pytree.convert)
tree = dr.parse_string('1 + 2 + 3\n')
