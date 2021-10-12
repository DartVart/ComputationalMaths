from typing import Tuple

from sympy import lambdify
import plotly.graph_objects as go
import pandas as pd

from common.models.line_segment import LineSegment
from common.models.point_generation import EquidistantPointGenerator
from config import COLORS
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.plotly import update_figure_to_x_axis, add_nodes, add_line


def get_new_key(st):
    st.session_state["key"] += 1
    return st.session_state["key"]


def set_initial_key(st):
    st.session_state["key"] = 100


def input_function(st, initial_expression: str, key):
    expression = input_sympy_function(st, initial_expression, key)
    return lambdify("x", custom_parse_expr(expression))


def input_sympy_function(st, initial_expression: str, key):
    return st.text_input("Введите выражение", initial_expression, key=key)


def input_points(st, line_segment, keys: Tuple[int, int, int]):
    number_of_all_points = st.number_input("Введите количество узлов", value=15, key=keys[0])
    all_points = sorted(EquidistantPointGenerator().generate(line_segment, number_of_all_points))
    display_x_points(st, all_points, keys[2], title="Сгенерированные узлы")
    return number_of_all_points, all_points


def input_polynomial_degree(st, max_degree, value, key):
    """If there was an error, it returns None."""

    polynomial_degree = st.number_input(
        f"Введите степень интерполяционного многочлена n, где n <= {max_degree}", value=value, key=key
    )
    if polynomial_degree > max_degree:
        st.error(f"Пожалуйста, введите n <= {max_degree}")
        return None
    elif polynomial_degree < 1:
        st.error(f"Пожалуйста, введите n > 0.")
        return None
    return polynomial_degree


def input_line_segment(columns, keys: Tuple[int, int], left_initial=0.0, right_initial=1.0):
    left_bound = columns[0].number_input("Введите границы отрезка", step=0.1, value=left_initial, key=keys[0])
    right_bound = columns[1].number_input("", step=0.1, value=right_initial, key=keys[1])
    return LineSegment(left_bound, right_bound)


def display_title(st, text, level=1):
    st.markdown(
        f"""
        <h{level} style='text-align: center'>
            {text}
        </h{level}>
        """,
        unsafe_allow_html=True,
    )


def display_x_points(st, x, key, names=None, title="", y=None, x_point=None, x_point_name="x"):
    if names is None:
        names = ["Значение"]

    fig = go.Figure()
    hover_template = "%{x}"
    size = 7
    add_nodes(fig, x, lambda z: 0, "", COLORS["theme_color"], size, hover_template)
    if x_point:
        add_nodes(fig, [x_point], lambda z: 0, f"{x_point_name}", COLORS["dark_blue"], size, hover_template)

    update_figure_to_x_axis(fig)
    fig.update_layout(title=title)
    st.write(fig, key=key)
    data = {f"{i + 1}": [point] + ([y[i]] if y is not None else []) for i, point in enumerate(x)}
    index = [names[0]] + ([names[1]] if y is not None else [])
    st.dataframe(pd.DataFrame(data=data, index=index))


def display_whitespace(st):
    st.text("")
