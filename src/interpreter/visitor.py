from typing import Callable


class Visitor:

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor: Callable = getattr(self, method, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))
