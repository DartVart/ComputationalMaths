import sys

sys.path.append("")
sys.path.append("../../..")

from sympy import integrate, lambdify
import streamlit as st
from math import sin

from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.streamlit import set_initial_key, display_whitespace, display_title, input_sympy_function, get_new_key, \
    input_line_segment

LINE_START = "$\quad$"

FUNCTIONS = {
    "sin(x)": {
        "sympy": custom_parse_expr('sin(x)'),
        0: {
            "func": lambda x: sin(x),
            "max": lambda line_seg: line_seg,
        },
        1: {

        },
        2: {

        },
        3: {

        },
        4: {

        }
    }
}


def display_result(function_name, line_segment: LineSegment):
    function_data = FUNCTIONS[function_name]
    integral = lambdify(integrate(function_data['sympy']))
    real_integral_value = integral(line_segment.right) - integral(line_segment.left)
    st.text(real_integral_value)


def main():
    set_initial_key(st)

    display_title(st, "Приближенное вычисление интеграла по квадратурным формулам")
    display_whitespace(st)

    function_name = st.selectbox("Выберите функцию", tuple(FUNCTIONS))
    columns = st.columns(2)
    line_segment = input_line_segment(columns, (get_new_key(st), get_new_key(st)))
    display_result(function_name, line_segment)


if __name__ == "__main__":
    main()
