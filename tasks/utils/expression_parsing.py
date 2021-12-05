from sympy import lambdify, integrate
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


if __name__ == '__main__':
    a = lambdify('x', custom_parse_expr("E^x"))
    print(a(1))