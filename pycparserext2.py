from pycparser import c_ast
from pycparserext.ext_c_parser import GnuCParser

class GnuCParser2(GnuCParser):
    initial_type_symbols = GnuCParser.initial_type_symbols.union(set([
        '__auto_type'
    ]))

    def p_declaration(self, p):
        ''' declaration : decl_body asm_opt SEMI
        '''
        p[0] = p[1]

    def p_unary_expression_4(self, p):
        ''' unary_expression : LAND identifier
        '''
        p[0] = c_ast.UnaryOp(
            p[1],
            p[2],
            self._token_coord(p, 1)
        )

    def p_jump_statement_5(self, p):
        ''' jump_statement : GOTO TIMES expression SEMI
        '''
        p[0] = c_ast.Goto(p[3], self._token_coord(p, 1))
