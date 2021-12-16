import sys

sys.path.append("")
sys.path.append("../..")

import pandas as pd
from sympy import integrate
import streamlit as st

from config import COLORS
from common.models.line_segment import LineSegment
from common.calculation.integrating.qfhap.gauss.compound_gauss import CompoundGaussQF
from common.calculation.integrating.qfhap.gaussian_type import GaussianTypeQF
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.streamlit import (
    set_initial_key,
    display_whitespace,
    display_title,
    get_new_key,
    input_line_segment,
    input_sympy_function,
)
from tasks.utils.plotly import update_figure_to_x_axis
import plotly.graph_objects as go

compound_gauss_qf = CompoundGaussQF()
gaussian_type_qf = GaussianTypeQF()


def display_nodes_and_coefficients(nodes, coefficients, need_to_show_graphs, line_segment):
    data = {f"{i}": [node, coef] for i, (node, coef) in enumerate(zip(nodes, coefficients))}
    index = ["Узлы", "Коэффициенты"]
    df = pd.DataFrame(data=data, index=index)
    df_styler = df.style.format(formatter={i: lambda x: f"{x:.6f}" for i, _ in enumerate(nodes)})

    st.dataframe(df_styler)

    if need_to_show_graphs:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=nodes,
                y=[0] * len(nodes),
                marker={"size": 7},
                line={"color": COLORS["theme_color"], "width": 3},
                name="",
                mode="markers",
                hovertemplate="%{x}",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[line_segment.left, line_segment.right],
                y=[0, 0],
                marker={"size": 7},
                line={"color": COLORS["dark_blue"], "width": 3},
                name="",
                mode="markers",
                hovertemplate="%{x}",
            )
        )

        update_figure_to_x_axis(fig)
        st.write(fig)


def show_integral(real_integral_value, approx_integral, need_to_show_real_integral):
    if need_to_show_real_integral:
        st.markdown(rf"""Точное значение интеграла $I_{{real}} = {real_integral_value:.14f}$""")
        st.markdown(rf"""Приближенное значение интеграла $I_{{approx}} = {approx_integral:.14f}$""")
        st.markdown(rf"""$|I_{{approx}} - I_{{real}}| = {abs(approx_integral - real_integral_value)}$""")
    else:
        st.markdown(rf"""Приближенное значение интеграла $I_{{approx}} = {approx_integral:.14f}$""")


def display_compound_gauss_qf(
    sympy_function,
    sympy_weight_function,
    line_segment,
    node_count,
    partition_count,
    real_integral_value,
    need_to_show_graphs,
    need_to_show_real_integral,
):
    display_title(st, "Составная КФ Гаусса", 4)
    function_values = compound_gauss_qf.get_function_values(
        sympy_function * sympy_weight_function, line_segment, node_count, partition_count
    )
    approx_integral = compound_gauss_qf.integrate(function_values, line_segment, node_count, partition_count)

    display_nodes_and_coefficients(
        compound_gauss_qf.stat["standard_nodes"],
        compound_gauss_qf.stat["standard_coefficients"],
        need_to_show_graphs,
        LineSegment(-1, 1),
    )
    show_integral(real_integral_value, approx_integral, need_to_show_real_integral)


def display_gaussian_type_qf(
    sympy_function,
    sympy_weight_function,
    line_segment,
    node_count,
    real_integral_value,
    need_to_show_graphs,
    need_to_show_real_integral,
):
    display_title(st, "КФ типа Гаусса", 4)
    moments = gaussian_type_qf.get_moments(sympy_weight_function, line_segment, node_count)
    orthogonal_poly_coefficients = gaussian_type_qf.get_orthogonal_poly_coefficients(moments)
    nodes = gaussian_type_qf.find_nodes(orthogonal_poly_coefficients)
    coefficients = gaussian_type_qf.find_coefficients(nodes, moments)
    function_values = gaussian_type_qf.get_function_values(sympy_function, nodes)
    approx_integral = gaussian_type_qf.integrate(function_values, coefficients)

    data = {f"{i}": [moment] for i, moment in enumerate(moments)}
    index = ["Моменты"]
    df = pd.DataFrame(data=data, index=index)
    df_styler = df.style.format(formatter={i: lambda x: f"{x:.6f}" for i, _ in enumerate(nodes)})
    st.dataframe(df_styler)

    orthogonal_poly = f"x^{{{node_count}}}" + "".join(
        reversed(
            [
                f"{'+' if coef >= 0 else '-'}{abs(coef)}" + (f"x^{{{i}}}" if i > 1 else ("x" if i == 1 else ""))
                for i, coef in enumerate(orthogonal_poly_coefficients)
            ]
        )
    )

    st.markdown(rf"""Отрогональный многочлен $\omega_n(x) = {orthogonal_poly}$""")

    display_nodes_and_coefficients(nodes, coefficients, need_to_show_graphs, line_segment)

    show_integral(real_integral_value, approx_integral, need_to_show_real_integral)


def main():
    set_initial_key(st)

    display_title(st, "Приближённое вычисление интегралов при помощи КФ НАСТ")
    display_whitespace(st)
    func_col1, func_col2 = st.columns(2)
    sympy_function = custom_parse_expr(
        input_sympy_function(func_col1, "sin(x)", key=get_new_key(st), message="Введите функцию")
    )
    sympy_weight_function = custom_parse_expr(
        input_sympy_function(func_col2, "x^(1/4)", key=get_new_key(st), message="Введите весовую функцию")
    )

    line_segment_col1, line_segment_col2, line_segment_col3 = st.columns((1, 1, 2))
    line_segment = input_line_segment(
        (line_segment_col1, line_segment_col2),
        (get_new_key(st), get_new_key(st)),
        left_initial=0.0,
        right_initial=1.0,
        message="Границы отрезка",
    )
    partition_count = line_segment_col3.number_input(
        "На сколько частей разбивать отрезок", value=10, step=1, format="%i", min_value=1
    )

    nodes_count_col1, nodes_count_col2 = st.columns(2)
    max_node_count = nodes_count_col1.number_input(
        "Максимальное количество узлов", value=8, step=1, format="%i", min_value=1
    )
    node_counts = nodes_count_col2.multiselect(
        "Количество узлов", list(range(1, max_node_count + 1)), default=5 if max_node_count >= 5 else max_node_count
    )

    display_whitespace(st)
    add_col1, add_col2 = st.columns(2)
    need_to_show_real_integral = add_col1.checkbox("Показывать точное значение интеграла", True)
    need_to_show_graphs = add_col2.checkbox("Показывать точки на оси", True)

    display_title(st, "Результат", 2)
    for node_count in sorted(node_counts):
        display_title(st, f"Количество узлов: {node_count}", 3)
        real_integral_value = None
        if need_to_show_real_integral:
            real_integral_value = float(
                integrate(sympy_function * sympy_weight_function, ("x", line_segment.left, line_segment.right))
            )

        display_compound_gauss_qf(
            sympy_function,
            sympy_weight_function,
            line_segment,
            node_count,
            partition_count,
            real_integral_value,
            need_to_show_graphs,
            need_to_show_real_integral,
        )

        display_gaussian_type_qf(
            sympy_function,
            sympy_weight_function,
            line_segment,
            node_count,
            real_integral_value,
            need_to_show_graphs,
            need_to_show_real_integral,
        )


if __name__ == "__main__":
    main()
