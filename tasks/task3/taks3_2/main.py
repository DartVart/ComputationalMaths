import sys

sys.path.append("")
sys.path.append("../../..")

import streamlit as st
import pandas as pd
from sympy import lambdify, diff
import numpy as np
from plotly.subplots import make_subplots

from config import COLORS
from common.calculation.derivative.derivative_calculator import FirstDerivativeCalculator, SecondDerivativeCalculator
from common.models.line_segment import LineSegment
from common.models.point_generation import EquidistantPointGenerator
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.streamlit import (
    display_x_points,
    display_title,
    get_new_key,
    set_initial_key,
    input_sympy_function,
    add_line,
    display_whitespace,
)

LINE_START = "$\quad$"


def fill_beginning_and_end(input_list, value_to_fill=None):
    return [value_to_fill] + input_list + [value_to_fill]


def display_result_table(
    points,
    function_as_lambda,
    first_derivative_as_lambda,
    second_derivative_as_lambda,
    first_derivative_values,
    second_derivatives_values,
):
    no_value_text = "No value"
    data = {
        "x": points,
        "f(x)": [function_as_lambda(point) for point in points],
        "approx f'(x)": first_derivative_values,
        "|Δf'(x)|": [
            abs(first_derivative_as_lambda(point) - first_derivative_values[i]) for i, point in enumerate(points)
        ],
        "approx f''(x)": fill_beginning_and_end(second_derivatives_values),
        "|Δf''(x)|": fill_beginning_and_end(
            [
                abs(second_derivative_as_lambda(point) - second_derivatives_values[i])
                for i, point in enumerate(points[1:-1])
            ]
        ),
    }
    df = pd.DataFrame(data=data)
    idx = pd.IndexSlice
    df_styler = (
        df.style.format(
            formatter={
                "|Δf'(x)|": "{:e}",
                "approx f''(x)": lambda x: no_value_text if np.isnan(x) else f"{x:.6f}",
                "|Δf''(x)|": lambda x: no_value_text if np.isnan(x) else f"{x:e}",
            }
        )
        .set_properties(**{"background-color": "#fff2f7"}, subset=idx[::2, :])
        .set_properties(**{"background-color": "#f2faff"}, subset=idx[1::2, :])
    )
    st.dataframe(df_styler)


def add_line_with_points(
    fig, x_points, y_points, function, line_title, points_title, line_color, point_color, row, col
):
    max_point = max(list(x_points))
    min_point = min(list(x_points))
    additional_value = (max_point - min_point) * 0.1
    points_for_function = np.linspace(min_point - additional_value, max_point + additional_value, 150)
    add_line(fig, points_for_function, function, line_title, line_color, row=row, col=col)

    fig.add_scatter(
        x=x_points,
        y=y_points,
        mode="markers",
        hovertemplate="(%{x}, %{y})",
        name=points_title,
        marker=dict(color=point_color, size=7),
        row=row,
        col=col,
    )


def display_result(points, sympy_function, first_derivative_values, second_derivatives_values):
    display_title(st, "Результат", 2)

    first_derivative = diff(sympy_function)
    second_derivative = diff(first_derivative)
    first_derivative_as_lambda = lambdify("x", first_derivative)
    second_derivative_as_lambda = lambdify("x", second_derivative)
    function_as_lambda = lambdify("x", sympy_function)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Первая производная", "Вторая производная"))
    add_line_with_points(
        fig,
        points,
        first_derivative_values,
        function=first_derivative_as_lambda,
        line_title="f'",
        points_title="approx f'",
        line_color="gray",
        point_color=COLORS["theme_color"],
        row=1,
        col=1,
    )
    add_line_with_points(
        fig,
        points[1:-1],
        second_derivatives_values,
        function=second_derivative_as_lambda,
        line_title="f''",
        points_title="approx f''",
        line_color="black",
        point_color=COLORS["dark_blue"],
        row=1,
        col=2,
    )
    fig.update_layout(margin=dict(l=0, t=50, b=0, r=0))

    display_title(st, "Графики", 4)
    st.plotly_chart(fig, use_container_width=True)

    display_title(st, "Таблица", 4)
    display_result_table(
        points,
        function_as_lambda,
        first_derivative_as_lambda,
        second_derivative_as_lambda,
        first_derivative_values,
        second_derivatives_values,
    )


def main():
    set_initial_key(st)
    first_derivative_calculator = FirstDerivativeCalculator()
    second_derivative_calculator = SecondDerivativeCalculator()

    display_title(st, "Нахождение производных таблично-заданной функции по формулам численного дифференцирования")
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
