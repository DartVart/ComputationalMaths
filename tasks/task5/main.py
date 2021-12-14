import sys

sys.path.append("")
sys.path.append("../..")

import pandas as pd
from sympy import integrate
import streamlit as st

from config import COLORS
from common.calculation.integrating.qfhap.gauss import GaussQF
from common.calculation.integrating.qfhap.meler import MelerQF
from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.streamlit import set_initial_key, display_whitespace, display_title, get_new_key, \
    input_line_segment, input_sympy_function
from tasks.utils.plotly import update_figure_to_x_axis
import plotly.graph_objects as go

QF_TYPES = {
    'gauss': "Гаусса",
    'meler': "Мелера"
}

gauss_qf = GaussQF()
meler_qf = MelerQF()


def display_result(approx_integral, nodes, coefficients, line_segment, need_to_show_real_integral,
                   need_to_show_graphs, real_integral_value):
    data = {f"{i}": [node, coef] for i, (node, coef) in enumerate(zip(nodes, coefficients))}
    index = ["Узлы", "Коэффициенты"]
    df = pd.DataFrame(data=data, index=index)
    df_styler = (
        df.style.format(
            formatter={i: lambda x: f"{x:.6f}" for i, _ in enumerate(nodes)}
        )
    )

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
    if need_to_show_real_integral:
        st.markdown(rf"""Точное значение интеграла $I_{{real}} = {real_integral_value:.14f}$""")
        st.markdown(rf"""Приближенное значение интеграла $I_{{approx}} = {approx_integral:.14f}$""")
        st.markdown(rf"""$|I_{{approx}} - I_{{real}}| = {abs(approx_integral - real_integral_value)}$""")
    else:
        st.markdown(rf"""Приближенное значение интеграла $I_{{approx}} = {approx_integral:.14f}$""")


def handle_meler(sympy_function, node_counts, line_segment, need_to_show_real_integral, need_to_show_graphs):
    display_title(st, "Результат", 2)
    for node_count in sorted(node_counts):
        display_title(st, f"Количество узлов: {node_count}", 3)
        nodes = meler_qf.get_nodes(node_count)
        coefficients = [meler_qf.get_coefficient(node_count)] * node_count
        function_values = meler_qf.get_function_values(sympy_function, node_count)
        approx_integral = meler_qf.get_approx_integral(function_values)
        real_integral_value = None
        if need_to_show_real_integral:
            real_integral_value = float(integrate(sympy_function * meler_qf.weight_function, ('x', line_segment.left, line_segment.right)))
        display_result(approx_integral, nodes, coefficients, line_segment, need_to_show_real_integral,
                       need_to_show_graphs, real_integral_value)


def handle_gauss(sympy_function, node_counts, line_segment, need_to_show_real_integral, need_to_show_graphs):
    display_title(st, "Результат", 2)
    for node_count in sorted(node_counts):
        display_title(st, f"Количество узлов: {node_count}", 3)
        nodes = gauss_qf.get_nodes(line_segment, node_count)
        coefficients = gauss_qf.get_coefficients(line_segment, node_count)
        function_values = gauss_qf.get_function_values(sympy_function, line_segment, node_count)
        approx_integral = gauss_qf.get_approx_integral(function_values, line_segment)

        real_integral_value = None
        if need_to_show_real_integral:
            real_integral_value = float(integrate(sympy_function, ('x', line_segment.left, line_segment.right)))
        display_result(approx_integral, nodes, coefficients, line_segment, need_to_show_real_integral,
                       need_to_show_graphs, real_integral_value)


def main():
    set_initial_key(st)

    display_title(st, "Вычисление интегралов при помощи КФ Гаусса и Мелера")
    display_whitespace(st)
    sympy_function = custom_parse_expr(
        input_sympy_function(st, "sin(x) / x", key=get_new_key(st)))

    col1, col2, col3 = st.columns((2, 1, 1))
    qf_type = col1.selectbox("Тип КФ", QF_TYPES.values())

    if qf_type == QF_TYPES['meler']:
        for _ in range(3):
            display_whitespace(col2)
            display_whitespace(col3)
        col2.markdown(rf"""$\quad\quad A = -1$""")
        col3.markdown(rf"""$\quad\quad B = 1$""")
        line_segment = LineSegment(-1, 1)
    else:
        line_segment = input_line_segment((col2, col3), (get_new_key(st), get_new_key(st)), left_initial=0.0,
                                          right_initial=3.0)

    nodes_count_col1, nodes_count_col2 = st.columns(2)
    max_node_count = nodes_count_col1.number_input(
        "Максимальное количество узлов", value=8, step=1, format="%i", min_value=1
    )
    node_counts = nodes_count_col2.multiselect("Количество узлов", list(range(1, max_node_count + 1)),
                                               default=3 if max_node_count >= 3 else max_node_count)

    display_whitespace(st)
    add_col1, add_col2 = st.columns(2)
    need_to_show_real_integral = add_col1.checkbox("Показывать точное значение интеграла", True)
    need_to_show_graphs = add_col2.checkbox("Показывать точки на оси", True)

    if qf_type == QF_TYPES['meler']:
        handle_meler(sympy_function, node_counts, line_segment, need_to_show_real_integral, need_to_show_graphs)
    else:
        handle_gauss(sympy_function, node_counts, line_segment, need_to_show_real_integral, need_to_show_graphs)


if __name__ == '__main__':
    main()
