from abc import ABC

from src.parser.objects.objects import Identifier
from src.parser import types


class BuiltinFunction(ABC):
    name = None
    parameters_list = None
    return_type = None


class Print(BuiltinFunction):
    name = "print"
    parameters_list = None
    return_type = types.Void()


class String(BuiltinFunction):
    name = "String"
    parameters_list = [Identifier('x')]
    return_type = types.String()


class Integer(BuiltinFunction):
    name = "Integer"
    parameters_list = [Identifier('x')]
    return_type = types.Integer()


class Boolean(BuiltinFunction):
    name = "Boolean"
    parameters_list = [Identifier('x')]
    return_type = types.Bool()


class Float(BuiltinFunction):
    name = "Float"
    parameters_list = [Identifier('x')]
    return_type = types.Float()
