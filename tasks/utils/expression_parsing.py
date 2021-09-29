from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import (
    standard_transformations,
    split_symbols,
    implicit_multiplication,
    function_exponentiation,
    convert_xor,
)

TRANSFORMATIONS = standard_transformations + (
    split_symbols,
    implicit_multiplication,
    function_exponentiation,
    convert_xor,
)


def custom_parse_expr(expression):
    return parse_expr(expression, transformations=TRANSFORMATIONS)
