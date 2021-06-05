from ast import parse
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)


@magics_class
class MetaMagics(Magics):
    
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__myenv = kws

    @line_magic
    def myline(self, line):
        print(self.__myenv)
        return eval(compile(parse(line, mode='eval'), '<line-magic>', 'eval'))

    @cell_magic
    def mycell(self, line, cell):
        if line:
            myline_ast = parse(line, mode='eval')
            myline_co = compile(myline_ast, '<cell-magic-line>', 'eval')
            myline = eval(myline_co, globals(), self.__myenv)
        else:
            myline = None
        if callable(myline):
            return myline(cell)
        else:
            mycell_ast = parse(cell, mode='exec')
            mycell_co = compile(mycell_ast, '<cell-magic-cell>', 'exec')
            self.__myenv.update(locals())
            exec(mycell_co, globals(), self.__myenv)
        return

    @cell_magic
    def mybug(self, _, cell):
        return eval(compile(parse(cell, mode='exec'), '<cell-magic>', 'exec'))


def load_ipython_extension(ipython):
    print('Loading custom magics!!!')
    ipython.register_magics(MetaMagics)
    print('Loaded custom magics!!!')
