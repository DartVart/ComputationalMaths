import sys


sys.path.append("")
sys.path.append("../../..")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from common.models.point_generation import EquidistantPointGenerator
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator
from common.calculation.interpolation.find_optimal_points import find_optimal_points
from common.calculation.interpolation.interpolators.lagrangian_interpolator import LagrangianInterpolator
from common.calculation.root_finding.root_calculator import RootCalculator
from common.calculation.root_finding.singe_solvers.as_newton_solvers.secant_solver import SecantLineSolver
from tasks.utils.plotly import add_line, add_nodes
from config import COLORS
from tasks.utils.streamlit import (
    input_polynomial_degree,
    input_line_segment,
    input_function,
    display_x_points,
    display_title,
    get_new_key,
    set_initial_key,
    display_whitespace,
)

LINE_START = "$\quad$"

INTERPOLATORS = {LagrangianInterpolator.name: LagrangianInterpolator(), NewtonInterpolator.name: NewtonInterpolator()}


def get_polynomial_as_lambda(interpolator, value_table):
    def polynomial_as_lambda(x):
        return interpolator.get_approximate_value(x, value_table)

    return polynomial_as_lambda


def get_add_polynomial(polynomial_as_lambda):
    def add_polynomial(fig, graph_points):
        add_line(fig, graph_points, polynomial_as_lambda, "График полинома", "#000000")

    return add_polynomial


def get_add_inverse_polynomial(function, polynomial_as_lambda):
    def add_polynomial(fig, graph_points):
        inverse_graph_points = np.linspace(function(graph_points[0]), function(graph_points[-1]), 150)
        add_line(fig, inverse_graph_points, polynomial_as_lambda, "График обратного полинома", "#000000", inverse=True)

    return add_polynomial


def display_result_value(streamlit_parent, function, value, desired_value, line_segment, title=None):
    if title is not None:
        display_title(st, title, 3)
    if not line_segment.contains(value):
        streamlit_parent.info("Внимание! Значение выходит за гранциы отрезка")

    streamlit_parent.markdown(rf"""{LINE_START} Искомое значение $x = {value}$""")
    streamlit_parent.markdown(rf"""{LINE_START} $f(x) = {function(value)}$""")
    streamlit_parent.markdown(rf"""{LINE_START} Модуль невязки $|f(x) - F| = {abs(function(value) - desired_value)}$""")


def display_result_values(function, values, desired_value, line_segment):
    number_of_values = len(values)
    if number_of_values == 1:
        display_result_value(st, function, values[0], desired_value, line_segment)
    elif number_of_values > 1:
        for i in range(number_of_values):
            display_result_value(st, function, values[i], desired_value, line_segment, f"Значение {i + 1}")
    else:
        st.markdown(rf"""{LINE_START} Значений не нашлось 😞""")


def display_result(function, points, desired_values, desired_f_value, add_graph_function, line_segment):
    max_point = max(list(points) + desired_values)
    min_point = min(list(points) + desired_values)
    additional_value = (max_point - min_point) * 0.1
    points_for_function = np.linspace(min_point - additional_value, max_point + additional_value, 150)

    fig = go.Figure()
    add_line(
        fig,
        points_for_function,
        func=lambda x: desired_f_value,
        name="Искомое значение",
        color="gray",
        dash="dash",
        hover_template="%{y}",
    )
    add_line(fig, points_for_function, function, "Функция", "gray")
    add_graph_function(fig, points_for_function)
    add_nodes(fig, points, function, "Узлы", COLORS["theme_color"], 8)
    add_nodes(fig, desired_values, function, "Результат", COLORS["dark_blue"], 10)

    fig.update_layout(margin=dict(l=0, t=40, b=0, r=0))
    with st.expander("График", expanded=True):
        st.plotly_chart(fig, use_container_width=True)

    display_result_values(function, desired_values, desired_f_value, line_segment)


def make_inverse_interpolate_first_way(function, f_value, all_points, line_segment):
    display_title(st, "Способ с построением полинома обратной функции", 2)

    col_1, col_2 = st.columns((1.1, 2))
    need_new_polynomial_degree = col_1.radio(f"Степень как у предыдущего способа?", ("Да", "Нет")) == "Нет"
    if not need_new_polynomial_degree:
        st.session_state["second_polynomial_degree"] = st.session_state["polynomial_degree"]

    polynomial_degree = (
        input_polynomial_degree(
            col_2, len(all_points) - 1, st.session_state["second_polynomial_degree"], key=get_new_key(st)
        )
        if need_new_polynomial_degree
        else st.session_state["second_polynomial_degree"]
    )
    if polynomial_degree is not None:
        double_points = [(function(point), point) for point in all_points]
        optimal_double_points = sorted(
            find_optimal_points(f_value, double_points, polynomial_degree + 1, lambda y: y[0]),
            key=lambda y: y[0],
        )
        value_table = tuple(zip(*optimal_double_points))

        display_x_points(
            st,
            x=value_table[0],
            key=get_new_key(st),
            names=["f(x)", "x"],
            title="Оптимальные значения функции",
            y=value_table[1],
            x_point=f_value,
            x_point_name="F",
        )

        interpolator = INTERPOLATORS[
            st.selectbox("Выберите представление многочлена", tuple(INTERPOLATORS), key=get_new_key(st))
        ]
        desired_value = interpolator.get_approximate_value(f_value, value_table)

        display_result(
            function,
            points=value_table[1],
            desired_values=[desired_value],
            desired_f_value=f_value,
            add_graph_function=get_add_inverse_polynomial(
                function, get_polynomial_as_lambda(interpolator, value_table)
            ),
            line_segment=line_segment,
        )


def make_inverse_interpolate_second_way(function, f_value, line_segment, all_points):
    display_title(st, "Способ с построением полинома функции", 2)

    solver = RootCalculator(SecantLineSolver())
    polynomial_degree = input_polynomial_degree(
        st, len(all_points) - 1, st.session_state["polynomial_degree"], key=get_new_key(st)
    )
    if polynomial_degree is not None:
        st.session_state["polynomial_degree"] = polynomial_degree

        double_points = [(point, function(point)) for point in all_points]
        optimal_double_points = sorted(
            find_optimal_points(f_value, double_points, polynomial_degree + 1, lambda y: y[1]),
            key=lambda y: y[0],
        )
        value_table = tuple(zip(*optimal_double_points))
        display_x_points(
            st,
            x=value_table[1],
            key=get_new_key(st),
            names=["f(x)", "x"],
            title="Оптимальные значения функции",
            y=value_table[0],
            x_point=f_value,
            x_point_name="F",
        )
        col_1, col_2 = st.columns((1, 2))
        accuracy = col_1.number_input("Введите точность", format="%e", value=1e-12)
        number_of_steps = col_2.number_input(
            "Введите на сколько частей разобьется отрезок для нахождения корней", value=100, step=1, format="%i"
        )
        interpolator = INTERPOLATORS[
            st.selectbox("Выберите представление многочлена", tuple(INTERPOLATORS), key=get_new_key(st))
        ]
        polynomial_as_lambda = get_polynomial_as_lambda(interpolator, value_table)
        desired_values = solver.find_roots(
            lambda x: polynomial_as_lambda(x) - f_value, line_segment, accuracy, number_of_steps
        )

        display_result(
            function, value_table[0], desired_values, f_value, get_add_polynomial(polynomial_as_lambda), line_segment
        )
        return True
    else:
        return False


def set_initial_state_value(state_name, initial_value):
    if state_name not in st.session_state:
        st.session_state[state_name] = initial_value


def main():
    set_initial_key(st)
    set_initial_state_value("polynomial_degree", 7)
    set_initial_state_value("second_polynomial_degree", 7)

    display_title(st, "Задача обратного интерполирования")
    function = input_function(st, "ln(1+x)", key=get_new_key(st))

    col_1, col_2, col_3 = st.columns((2, 2, 3))
    line_segment = input_line_segment((col_1, col_2), (get_new_key(st), get_new_key(st)))
    is_func_monotone = (
        col_3.radio(f"Функция монотонна на отрезке [{line_segment.left:.1f}, {line_segment.right:.1f}]?", ("Да", "Нет"))
        == "Да"
    )

    number_of_all_points = st.number_input("Введите количество узлов", value=15, key=get_new_key(st))
    all_points = sorted(EquidistantPointGenerator().generate(line_segment, number_of_all_points))
    display_x_points(
        st,
        x=[function(point) for point in all_points],
        y=all_points,
        key=get_new_key(st),
        names=("f(x)", "x"),
        title="Значения функции в сгенерированных точках",
    )

    f_value = st.number_input("Введите значение функции:", step=0.1, value=0.35)

    display_whitespace(st)
    is_success = make_inverse_interpolate_second_way(function, f_value, line_segment, all_points)

    if is_func_monotone and is_success:
        display_whitespace(st)
        make_inverse_interpolate_first_way(function, f_value, all_points, line_segment)


if __name__ == "__main__":
    main()
