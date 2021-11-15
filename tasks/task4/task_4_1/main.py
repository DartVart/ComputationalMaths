import sys

from sympy import lambdify

from tasks.utils.expression_parsing import custom_parse_expr

sys.path.append("")
sys.path.append("../../..")

import streamlit as st
from tasks.utils.streamlit import set_initial_key, display_whitespace, display_title, input_sympy_function, get_new_key

LINE_START = "$\quad$"


def main():
    set_initial_key(st)

    display_title(st, "Приближенное вычисление интеграла по квадратурным формулам")
    display_whitespace(st)

    sympy_function = input_sympy_function(st, "exp(3*x)", key=get_new_key(st))
    function = lambdify("x", custom_parse_expr(sympy_function))

    col_1, col_2, col_3 = st.columns((4, 4, 3))
    left_value = col_1.number_input("Введите значение начальной точки", step=0.1, value=0.0)
    inter_node_length = col_2.number_input("Введите расстояние между точками", format="%e", value=5e-2)
    number_of_points = col_3.number_input("Введите количество точек", value=10)

    if inter_node_length < 0:
        col_2.error("Расстояние должно быть > 0")
    elif number_of_points < 3:
        col_3.error("Необходимо минимум 3 точки")
    else:
        line_segment = LineSegment(left_value, left_value + inter_node_length * (number_of_points - 1))
        all_points = sorted(EquidistantPointGenerator().generate(line_segment, number_of_points))
        function_values = [function(point) for point in all_points]
        display_x_points(
            st,
            x=function_values,
            y=all_points,
            key=get_new_key(st),
            names=("f(x)", "x"),
            title="Значения функции в сгенерированных точках",
        )

        first_derivative_values = first_derivative_calculator.calculate(function_values, inter_node_length)
        second_derivative_values = second_derivative_calculator.calculate(function_values, inter_node_length)
        display_result(all_points, sympy_function, first_derivative_values, second_derivative_values)


if __name__ == "__main__":
    main()
