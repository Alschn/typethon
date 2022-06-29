from typing import Any

from src.parser.objects.objects import FunctionDefinition, Variable


class Scope:
    symbol_table: dict[str, Variable]

    def __init__(self, parent_scope=None):
        self.parent_scope = parent_scope
        self.symbol_table = {}

    def try_to_find_and_set_variable(self, var: str, evaluated_value: Any):
        """Check if variable is in the current scope. If it is not, then check current scope's parent.
        Traverse through scope until variable is found and set or not found."""

        if var in self.symbol_table:
            self.symbol_table[var] = evaluated_value
            return True

        return self.parent_scope.try_to_find_and_set_variable(var, evaluated_value)

    def set_variable(self, var: str, evaluated_value: Any):
        """If variable exists in current scope or above, then reassign value.
        Otherwise add a new variable to symbol table in current scope."""

        if not self.try_to_find_and_set_variable(var, evaluated_value):
            self.symbol_table[var] = evaluated_value

    def get_variable(self, var: str):
        """Loops through all parent scopes (including current scope).
        Returns first matched variable or None if there was no match."""

        scope = self
        while (value := scope.symbol_table.get(var)) is None and scope.parent_scope is not None:
            scope = scope.parent_scope

        return value


class GlobalScope(Scope):
    """Global scope is a top level scope, which apart from inheriting default behaviour
    has its own function table for function definitions."""

    fun_table: dict[str, FunctionDefinition]

    def __init__(self, parent_scope: Scope = None):
        super().__init__(parent_scope)

        self.fun_table = {}

    def try_to_find_and_set_variable(self, var: str, evaluated_value: Any) -> bool:
        """If variable name is in symbol table, sets its value and returns True.
        Otherwise returns False."""

        if var in self.symbol_table:
            self.symbol_table[var] = evaluated_value
            return True

        return False

    def add_fun_def(self, fun_def: FunctionDefinition) -> None:
        """Adds function definition object to dictionary"""

        self.fun_table[fun_def.name] = fun_def

    def get_fun_def(self, fun: str) -> FunctionDefinition | None:
        """Gets function definition object from dictionary or returns None"""

        return self.fun_table.get(fun)
