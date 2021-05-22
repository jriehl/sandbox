from ast import parse
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)


@magics_class
class MyMagics(Magics):
    
    @line_magic
    def myline(self, line):
        return parse(line, mode='eval')
    
    @cell_magic
    def mycell(self, line, cell):
        return parse(line, mode='eval'), parse(cell, mode='exec')


def load_ipython_extension(ipython):
    print('Loading custom magics!!!')
    ipython.register_magics(MyMagics)
    print('Loaded custom magics!!!')
