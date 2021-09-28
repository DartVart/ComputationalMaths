import sys


sys.path.append("")
sys.path.append("../..")

from sympy import lambdify

from config import COLORS
from common.models.line_segment import LineSegment
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator
from common.models.point_generation import RandomPointGenerator, EquidistantPointGenerator
from tasks.utils.plotly_utils import update_figure_to_x_axis
from tasks.utils.expression_parsing import custom_parse_expr
from common.calculation.interpolation.find_optimal_points import find_optimal_points
from common.calculation.interpolation.interpolators.lagrangian_interpolator import LagrangianInterpolator
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

LINE_START = "$\quad$"

INTERPOLATORS = {
    LagrangianInterpolator.name: LagrangianInterpolator(),
    NewtonInterpolator.name: NewtonInterpolator(),
}

POINT_GENERATORS = {
    RandomPointGenerator.name: RandomPointGenerator(),
    EquidistantPointGenerator.name: EquidistantPointGenerator(),
}


def display_points(points, title="", x_point=None):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            mode="markers+text",
            x=points,
            y=[0] * len(points),
            marker={"size": 7},
            line={"color": COLORS['theme_color'], "width": 3},
            name="",
            hovertemplate="%{x}",
        )
    )

    if x_point:
        fig.add_scatter(x=[x_point], y=[0], mode="markers", marker={"size": 7, "color": COLORS['dark_blue']}, name="x",
                        hovertemplate="%{x}")

    update_figure_to_x_axis(fig)
    fig.update_layout(title=title)
    st.write(fig)
    df = pd.DataFrame(data={f"{i + 1}": point for i, point in enumerate(points)}, index=["Value"])
    st.dataframe(df)


def display_result(func, x, approximate_value, points, interpolator_name):
    st.title("Result")

    max_point = max(points + [x])
    min_point = min(points + [x])
    additional_value = (max_point - min_point) * 0.1
    points_for_func = np.linspace(min_point - additional_value, max_point + additional_value, 150)
    fig = go.Figure(
        data=go.Scatter(
            x=points_for_func,
            y=[func(point) for point in points_for_func],
            mode="lines",
            name="Function",
            marker=dict(color='gray'),
        )
    )

    fig.add_scatter(
        x=[x],
        y=[approximate_value],
        mode="markers",
        hovertemplate="(%{x}, %{y})",
        name="Result",
        marker=dict(color=COLORS['dark_blue'], size=10),
    )
    fig.add_scatter(
        x=points,
        y=[func(point) for point in points],
        mode="markers",
        hovertemplate="(%{x}, %{y})",
        name="Nodes",
        marker=dict(color=COLORS['theme_color'], size=8),
    )
    fig.update_layout(margin=dict(l=0, t=40, b=0, r=0))
    st.write(fig)

    polynomial_symbol = "P^{L}_n" if interpolator_name == LagrangianInterpolator.name else "P^{N}_n"
    st.markdown(rf"""{LINE_START} Interpolation value ${polynomial_symbol}(x) = {approximate_value}$""")
    st.markdown(rf"""{LINE_START} Real value $f(x) = {func(x)}$""")
    st.markdown(rf"""{LINE_START} $|{polynomial_symbol}(x) - f(x)| = {abs(approximate_value - func(x))}$""")


def main():
    if "seed" not in st.session_state:
        st.session_state["seed"] = 666
        st.session_state["number_of_points"] = 15

    st.title("Algebraic interpolation")

    expression = st.text_input("Enter expression", "ln(1+x)")
    func = lambdify("x", custom_parse_expr(expression))

    number_of_all_points = st.number_input("Enter number of points m + 1", value=st.session_state["number_of_points"])

    if number_of_all_points != st.session_state["number_of_points"]:
        st.session_state["number_of_points"] = number_of_all_points
        st.session_state["seed"] += 1
        POINT_GENERATORS[RandomPointGenerator.name].seed = st.session_state["seed"]

    segment_col1, segment_col2 = st.columns(2)
    left_bound = segment_col1.number_input("Enter segment boundaries", step=0.1, value=0.0)
    right_bound = segment_col2.number_input("", step=0.1, value=1.0)

    line_segment = LineSegment(left_bound, right_bound)

    point_generator_name = st.selectbox("Choose how to generate points", tuple(POINT_GENERATORS))

    if number_of_all_points is not None:
        all_points = sorted(POINT_GENERATORS[point_generator_name].generate(line_segment, number_of_all_points))
        st.markdown(f"${LINE_START[1:-1] * 3}$ **Generated points**")
        display_points(all_points)
        x_node = st.number_input("Enter interpolation point x:", step=0.1, value=0.35)
        polynomial_degree = st.number_input(
            f"Enter interpolation polynomial degree n <= {number_of_all_points - 1}", value=7
        )
        if polynomial_degree > number_of_all_points - 1:
            st.error(f"Please, enter n <= {number_of_all_points - 1}")
        elif polynomial_degree < 1:
            st.error(f"Please, enter n > 0.")
        else:
            optimal_points = find_optimal_points(x_node, all_points, polynomial_degree + 1)
            st.markdown(f"${LINE_START[1:-1] * 3}$ **Optimal points**")
            display_points(optimal_points, "Оптимальные узлы", x_node)
            interpolator_name = st.selectbox("Choose interpolator", tuple(INTERPOLATORS))
            value_table = (optimal_points, [func(point) for point in optimal_points])
            display_result(
                func,
                x_node,
                INTERPOLATORS[interpolator_name].get_approximate_value(x_node, value_table),
                optimal_points,
                interpolator_name,
            )


if __name__ == "__main__":
    main()
