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
        myline = eval(compile(parse(line, mode='eval'), '<cell-magic-line>', 'eval'))
        return myline, parse(cell, mode='exec')
    
    @cell_magic
    def mybug(self, _, cell):
        return eval(compile(parse(cell, mode='exec'), '<cell-magic>', 'exec'))


def load_ipython_extension(ipython):
    print('Loading custom magics!!!')
    ipython.register_magics(MetaMagics)
    print('Loaded custom magics!!!')
