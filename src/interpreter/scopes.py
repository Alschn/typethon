class Scope:
    pass


class GlobalScope(Scope):

    def __init__(self):
        self.func_defs = []
        self.var_defs = []
