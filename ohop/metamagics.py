from ast import parse
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)


@magics_class
class MetaMagics(Magics):
    
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__myenv = {'self': self}
        self.__myenv.update(kws)

    @line_magic
    def myline(self, line):
        return eval(compile(parse(line, mode='eval'), '<line-magic>', 'eval'))

    @cell_magic
    def mycell(self, line, cell):
        # Interesting note: the empty string is NOT checked or supported by ast.parse()...
        line_val = None
        if line:
            line_ast = parse(line, mode='eval')
            line_co = compile(line_ast, '<cell-magic-line>', 'eval')
            line_val = eval(line_co, globals(), self.__myenv)
        self.__myenv.update(locals())
        if callable(line_val):
            cell_val = line_val(cell, **self.__myenv)
        else:
            cell_ast = parse(cell)
            cell_co = compile(cell_ast, '<cell-magic>', 'exec')
            cell_val = exec(cell_co, globals(), self.__myenv)
        return line_val, cell_val

    @cell_magic
    def mybug(self, _, cell):
        return eval(compile(parse(cell, mode='exec'), '<cell-magic>', 'exec'))


def load_ipython_extension(ipython):
    print('Loading custom magics!!!')
    ipython.register_magics(MetaMagics)
    print('Loaded custom magics!!!')
