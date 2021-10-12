import sys


sys.path.append("")
sys.path.append("../..")

from config import COLORS
from tasks.utils.plotly import add_line, add_nodes
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator
from common.models.point_generation import RandomPointGenerator, EquidistantPointGenerator
from common.calculation.interpolation.find_optimal_points import find_optimal_points
from common.calculation.interpolation.interpolators.lagrangian_interpolator import LagrangianInterpolator
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from tasks.utils.streamlit import (
    input_polynomial_degree,
    input_line_segment,
    input_function,
    display_x_points,
    display_title,
    get_new_key,
    set_initial_key,
)

LINE_START = "$\quad$"

INTERPOLATORS = [LagrangianInterpolator(), NewtonInterpolator()]

POINT_GENERATORS = {
    RandomPointGenerator.name: RandomPointGenerator(),
    EquidistantPointGenerator.name: EquidistantPointGenerator(),
}


def display_result(func, x, approximate_value, points, interpolator_name):
    st.header(interpolator_name)

    max_point = max(points + [x])
    min_point = min(points + [x])
    additional_value = (max_point - min_point) * 0.1
    points_for_func = np.linspace(min_point - additional_value, max_point + additional_value, 150)

    fig = go.Figure()
    add_line(fig, points_for_func, func, "Функция", "gray")
    add_nodes(fig, points, func, "Узлы", COLORS["theme_color"], 8)
    add_nodes(fig, [x], lambda y: approximate_value, "Результат", COLORS["dark_blue"], 10)

    fig.update_layout(margin=dict(l=0, t=40, b=0, r=0))
    with st.expander("График", expanded=True):
        st.plotly_chart(fig, use_container_width=True)

    polynomial_symbol = "P^{L}_n" if interpolator_name == LagrangianInterpolator.name else "P^{N}_n"
    st.markdown(rf"""{LINE_START} Интерполяционное значение ${polynomial_symbol}(x) = {approximate_value}$""")
    st.markdown(rf"""{LINE_START} Значение интерполируемой функции $f(x) = {func(x)}$""")
    st.markdown(rf"""{LINE_START} $|{polynomial_symbol}(x) - f(x)| = {abs(approximate_value - func(x))}$""")


def main():
    set_initial_key(st)
    if "seed" not in st.session_state:
        st.session_state["seed"] = 666
        st.session_state["number_of_points"] = 15

    display_title(st, "Задача алгебраического интерполирования")

    func = input_function(st, "ln(1+x)", key=get_new_key(st))

    number_of_all_points = st.number_input("Введите количество узлов", value=st.session_state["number_of_points"])

    if number_of_all_points != st.session_state["number_of_points"]:
        st.session_state["number_of_points"] = number_of_all_points
        st.session_state["seed"] += 1
        POINT_GENERATORS[RandomPointGenerator.name].seed = st.session_state["seed"]

    line_segment = input_line_segment(st.columns(2), (get_new_key(st), get_new_key(st)))

    point_generator_name = st.selectbox("Выберите то, какие сгенерировать узлы", tuple(POINT_GENERATORS))

    if number_of_all_points is not None:
        all_points = sorted(POINT_GENERATORS[point_generator_name].generate(line_segment, number_of_all_points))
        display_x_points(st, all_points, get_new_key(st), title="Сгенерированные узлы")
        x_node = st.number_input("Введите точку интерполирования x:", step=0.1, value=0.35)
        polynomial_degree = input_polynomial_degree(st, number_of_all_points - 1, 7, get_new_key(st))
        if polynomial_degree is not None:
            optimal_points = sorted(find_optimal_points(x_node, all_points, polynomial_degree + 1))
            display_x_points(st, optimal_points, get_new_key(st), title="Оптимальные узлы", x_point=x_node)

            value_table = (optimal_points, [func(point) for point in optimal_points])

            st.title("Результат")
            for interpolator in INTERPOLATORS:
                display_result(
                    func,
                    x_node,
                    interpolator.get_approximate_value(x_node, value_table),
                    optimal_points,
                    interpolator.name,
                )


if __name__ == "__main__":
    main()
