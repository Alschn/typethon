from typing import Any

from src.interpreter.scopes import Scope, GlobalScope
from src.parser.objects.builtins import Print, String, Integer, Float, Boolean
from src.parser.objects.objects import FunctionDefinition


class Environment:
    """
    Environment consists of GlobalScope and a call stack. Global scope is visible everywhere and consists
    of variables and function definitions. Function Definitions are treated like variables with func type but
    are stored separated from them.

    Environment class is capable of:
    - creating new function and local scopes and removing them,
    - setting and getting variables from a current scope or above,
    - adding and retrieving function definition from a global scope
    """

    def __init__(self):
        self.global_scope = GlobalScope()
        self._add_builtin_fun_defs()

        self.current_scope = self.global_scope
        self.call_stack = []
        self.fun_call_nesting = 0

    def set_variable(self, var: str, evaluated_value: Any):
        """Sets a variable on the current scope."""

        self.current_scope.set_variable(var, evaluated_value)

    def get_variable(self, var: str):
        """Tries to get a variable while traversing through scopes,
        starting on current scope. Functions are also treated like variables!"""
        return self.current_scope.get_variable(var)

    def get_variable_or_func_def(self, var):
        return self.current_scope.get_variable(var) or self.global_scope.get_fun_def(var)

    def create_new_local_scope(self) -> None:
        """Creates a new scope, whose parent is a previous scope."""

        new_scope = Scope(self.current_scope)
        self.current_scope = new_scope

    def destroy_local_scope(self) -> None:
        """Destroys local scope by setting current scope to current scope's parent."""

        self.current_scope = self.current_scope.parent_scope

    def create_new_fun_scope(self, parameters: list, arguments: list) -> None:
        """Creates a function scope to store its parameters inside."""

        parameters_scope = self._put_parameters_inside_new_scope(parameters, arguments)
        self.call_stack.append(self.current_scope)
        self.current_scope = parameters_scope
        self.fun_call_nesting += 1

    def destroy_fun_scope(self) -> None:
        """Removes current scope, decreases func call nesting and restores scope before function call from call stack.
        If there is nothing on a call stack, then the previous scope was the global scope."""

        self.current_scope = None
        self.fun_call_nesting -= 1

        # restore previous scope
        self.current_scope = self.call_stack.pop() if self.call_stack else self.global_scope

    def _put_parameters_inside_new_scope(self, parameters: list, arguments: list) -> Scope:
        """Creates a new scope for function to store its parameters and arguments."""

        fun_scope = Scope(self.global_scope)

        for param, arg in zip(parameters, arguments):
            fun_scope.symbol_table[param.name] = arg

        return fun_scope

    def add_fun_def(self, fun_def: FunctionDefinition) -> None:
        """Adds function definition to the global scope."""

        self.global_scope.add_fun_def(fun_def)

    def get_fun_def(self, fun: str) -> None:
        """Tries to get function definition from the global scope."""

        return self.global_scope.get_fun_def(fun)

    def _add_builtin_fun_defs(self):
        for builtin in FunctionsBuilder.build():
            self.global_scope.fun_table[builtin.name] = FunctionDefinition(
                builtin.name,
                builtin.return_type,
                builtin.parameters_list,
                builtin,
                builtin=True
            )


class FunctionsBuilder:

    @staticmethod
    def build():
        for func in [
            Print(),
            String(),
            Integer(),
            Boolean(),
            Float()
        ]:
            yield func
