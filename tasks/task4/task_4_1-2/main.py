import math
import sys

sys.path.append("")
sys.path.append("../../..")

from common.calculation.integrating.compound_quadrature_formulas import get_sum_in_middle_nodes, \
    get_sum_in_middle_of_segments, get_sum_at_extremes, RightRectanglesFormula, LeftRectanglesFormula, \
    MiddleRectanglesFormula, TrapezesFormula, SimpsonFormula, ThreeFractionsOfEightFormula
from common.models.point_generation import EquidistantPointGenerator
from sympy import integrate, lambdify
import streamlit as st
from math import cos
import plotly.graph_objects as go
import numpy as np

from config import COLORS
from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr
from tasks.utils.streamlit import set_initial_key, display_whitespace, display_title, get_new_key, \
    input_line_segment, input_sympy_function
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator
from tasks.utils.plotly import add_line, add_nodes

INTERPOLATOR = NewtonInterpolator()

LINE_START = "$\quad$"

QUADRATURES = {
    "Формула левых прямоугольников": LeftRectanglesFormula(),
    "Формула правых прямоугольников": RightRectanglesFormula(),
    "Формула средних прямоугольников": MiddleRectanglesFormula(),
    "Формула трапеций": TrapezesFormula(),
    "Формула Симпсона": SimpsonFormula(),
    "Формула 3/8": ThreeFractionsOfEightFormula()
}


def sin_modulo_max(line_segment: LineSegment):
    return cos_modulo_max(LineSegment(line_segment.left + math.pi / 2, line_segment.right + math.pi / 2))


def cos_modulo_max(line_segment: LineSegment):
    pi_in_right = int(line_segment.right / math.pi)
    pi_in_left = int(line_segment.left / math.pi)
    if (pi_in_right - pi_in_left > 0) or (line_segment.left < 0 and line_segment.right > 0):
        return 1.0
    else:
        return max(abs(cos(line_segment.left)), abs(cos(line_segment.right)))


def zero_func(*args):
    return 0


def get_modulo_max_in_extreme_points(func):
    def max_in_extreme_points(line_segment: LineSegment):
        left_value = abs(func(line_segment.left))
        right_value = abs(func(line_segment.right))
        return max(left_value, right_value)

    return max_in_extreme_points


FUNCTIONS = {
    "cos(x)": {
        "sympy": custom_parse_expr('cos(x)'),
        "1_der_max": sin_modulo_max,
        "2_der_max": cos_modulo_max,
        "3_der_max": sin_modulo_max,
        "4_der_max": cos_modulo_max,
    },
    "10 (константа)": {
        "sympy": custom_parse_expr('10 + x*0'),
        "1_der_max": zero_func,
        "2_der_max": zero_func,
        "3_der_max": zero_func,
        "4_der_max": zero_func,
    },
    "3x + 1": {
        "sympy": custom_parse_expr('3*x + 1'),
        "1_der_max": lambda x: 3,
        "2_der_max": zero_func,
        "3_der_max": zero_func,
        "4_der_max": zero_func,
    },
    "2x^2 + x + 1": {
        "sympy": custom_parse_expr('2 * (x ** 2) + x + 1'),
        "1_der_max": get_modulo_max_in_extreme_points(lambda x: 4 * x + 1),
        "2_der_max": lambda x: 4,
        "3_der_max": zero_func,
        "4_der_max": zero_func,
    },
    "3x^3 - x^2 + x + 1": {
        "sympy": custom_parse_expr('3 * (x ** 3) - (x ** 2) + x + 1'),
        "1_der_max": get_modulo_max_in_extreme_points(lambda x: 9 * (x ** 2) - 2 * x + 1),
        "2_der_max": get_modulo_max_in_extreme_points(lambda x: 18 * x - 2),
        "3_der_max": lambda x: 18,
        "4_der_max": zero_func,
    },
    "E^(3*x)": {
        "sympy": custom_parse_expr('E^(3*x)'),
        "1_der_max": get_modulo_max_in_extreme_points(lambda x: 3 * (math.e ** (3 * x))),
        "2_der_max": get_modulo_max_in_extreme_points(lambda x: 9 * (math.e ** (3 * x))),
        "3_der_max": get_modulo_max_in_extreme_points(lambda x: 27 * (math.e ** (3 * x))),
        "4_der_max": get_modulo_max_in_extreme_points(lambda x: 81 * (math.e ** (3 * x))),
    },
}


def add_area_part(fig, line_segment, quad_name, function, index):
    x0 = line_segment.left
    x1 = line_segment.right

    points_for_quadrature = np.linspace(x0, x1, 150)

    fig.add_scatter(
        x=[x0] + list(points_for_quadrature) + [x1, x0],
        y=[0] + [function(point) for point in points_for_quadrature] + [0, 0],
        line_width=0,
        line=dict(color=COLORS["dark_blue"]),
        fill='toself',
        opacity=0.15,
        showlegend=False
    )

    x = [x0, x0, x1, x1, x0]
    if quad_name == "Формула левых прямоугольников":
        additional_points = [line_segment.left]
        y = [0, function(x0), function(x0), 0, 0]
    elif quad_name == "Формула правых прямоугольников":
        additional_points = [line_segment.right]
        y = [0, function(x1), function(x1), 0, 0]
    elif quad_name == "Формула средних прямоугольников":
        additional_points = [line_segment.center]
        y = [0, function(line_segment.center), function(line_segment.center), 0, 0]
    elif quad_name == "Формула трапеций":
        additional_points = [line_segment.left, line_segment.right]
        y = [0, function(x0), function(x1), 0, 0]
    elif quad_name == "Формула Симпсона":
        additional_points = [x0, line_segment.center, x1]
        parabola_table = (additional_points, [function(point) for point in additional_points])
        parabola_values = [INTERPOLATOR.get_approximate_value(point, parabola_table) for point in points_for_quadrature]
        x = [x0] + list(points_for_quadrature) + [x1, x0]
        y = [0] + parabola_values + [0, 0]
    else:
        h = line_segment.length / 3
        additional_points = [x0, x0 + h, x0 + 2 * h, x1]
        cubuc_table = (additional_points, [function(point) for point in additional_points])
        cubic_values = [INTERPOLATOR.get_approximate_value(point, cubuc_table) for point in points_for_quadrature]
        x = [x0] + list(points_for_quadrature) + [x1, x0]
        y = [0] + cubic_values + [0, 0]

    fig.add_scatter(
        legendgroup='area',
        x=x,
        y=y,
        mode="lines",
        line=dict(color=COLORS["dark_red"]),
        fill='toself',
        opacity=0.6,
        name="proximity of area",
        showlegend=(index == 0)
    )

    add_nodes(fig, additional_points, function, "function values",
              COLORS['theme_color'], 7.5, showlegend=(index == 0))


def display_graph(function, line_segment: LineSegment, quad_name, partition_count):
    x0 = line_segment.left
    x1 = line_segment.right
    fig = go.Figure()

    additional_value = line_segment.length * 3
    points_for_function = np.linspace(x0 - additional_value, x1 + additional_value, 800)

    points_for_height_calculate = np.linspace(x0 - additional_value / 6, x1 + additional_value / 6, 200)
    func_calculate_height_points = [function(point) for point in points_for_height_calculate]
    max_y = max(func_calculate_height_points)
    min_y = min(func_calculate_height_points + [0])
    additional_height = (max_y - min_y) * 0.1

    add_line(fig, points_for_function, function, "function", COLORS['dark_blue'])

    point_generator = EquidistantPointGenerator()
    points_for_quadratures = point_generator.generate(line_segment, partition_count + 1)
    for i in range(len(points_for_quadratures) - 1):
        add_area_part(fig, LineSegment(points_for_quadratures[i], points_for_quadratures[i + 1]), quad_name, function,
                      i)

    fig.update_layout(margin=dict(l=20, t=40, b=20, r=0))
    fig.update_xaxes(range=[x0 - additional_value / 6, x1 + additional_value / 6])
    fig.update_yaxes(range=[min_y - additional_height, max_y + additional_height])
    fig.update_layout(template='none')
    with st.expander("Графиеческое представление", expanded=True):
        st.plotly_chart(fig, use_container_width=True)


def display_result(line_segment: LineSegment, partition_count, need_to_show_graphs, function_name=None,
                   sympy_function=None):
    display_title(st, "Результат", 2)

    if function_name:
        sympy_function = FUNCTIONS[function_name]['sympy']
    function = lambdify("x", sympy_function)

    try:
        integral = lambdify("x", integrate(sympy_function))
    except ValueError:  # constant
        integral = lambda x: int(str(sympy_function)) * x
    real_integral_value = integral(line_segment.right) - integral(line_segment.left)

    st.markdown(rf"""{LINE_START} Точное значение интеграла $J_{{real}} = {real_integral_value}$""")
    st.markdown(rf"""{LINE_START} Длина "шага" $h = {line_segment.length / partition_count}$""")

    sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
    sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
    sum_at_extremes = get_sum_at_extremes(function, line_segment)
    additional_params = {
        "Формула левых прямоугольников": [sum_in_middle_nodes],
        "Формула правых прямоугольников": [sum_in_middle_nodes],
        "Формула средних прямоугольников": [sum_in_middle_of_segments],
        "Формула трапеций": [sum_at_extremes, sum_in_middle_nodes],
        "Формула Симпсона": [sum_at_extremes, sum_in_middle_nodes, sum_in_middle_of_segments],
        "Формула 3/8": []
    }
    for quadrature_name in QUADRATURES:
        approximate_integral = QUADRATURES[quadrature_name].calculate(function, line_segment, partition_count,
                                                                      *additional_params[quadrature_name])
        display_title(st, quadrature_name, 3)

        if need_to_show_graphs:
            display_graph(function, line_segment, quadrature_name, partition_count)

        st.markdown(rf"""{LINE_START} Приближенное значение интеграла $J_{{approx}} = {approximate_integral}$""")
        st.markdown(
            rf"""{LINE_START} Абсолютная фактическая погрешность $|J_{{approx}} - J_{{real}}| = {abs(approximate_integral - real_integral_value)}$""")

        if function_name:
            if quadrature_name in ("Формула левых прямоугольников", "Формула правых прямоугольников"):
                derivative_key = "1_der_max"
            elif quadrature_name in ("Формула средних прямоугольников", "Формула трапеций"):
                derivative_key = "2_der_max"
            elif quadrature_name in ("Формула Симпсона", "Формула 3/8"):
                derivative_key = "4_der_max"
            else:
                derivative_key = None
            theoretical_error = QUADRATURES[quadrature_name].get_theoretical_error(
                FUNCTIONS[function_name][derivative_key](line_segment), line_segment,
                partition_count) if derivative_key else "not \ implemented"
            st.markdown(rf"""{LINE_START} Теоретическая погрешность: ${theoretical_error}$""")


def main():
    set_initial_key(st)

    display_title(st, "Приближенное вычисление интеграла по квадратурным формулам")
    display_whitespace(st)

    function_choose_mode = st.radio("Выберите способ ввода функции",
                                    ("Выбрать из списка (с теоретической погрешностью)",
                                     "Ввести самому (без теоретической погрешности)"))
    function_name = None
    sympy_function = None
    if function_choose_mode == "Выбрать из списка (с теоретической погрешностью)":
        function_name = st.selectbox("Выберите функцию", tuple(FUNCTIONS))
    else:
        sympy_function = input_sympy_function(st, "cos(x)", key=get_new_key(st))

    col1, col2, col3 = st.columns((0.3, 0.3, 0.4))
    line_segment = input_line_segment((col1, col2), (get_new_key(st), get_new_key(st)))
    partition_count = col3.number_input(
        "На сколько частей разбивать отрезок", value=1, step=1, format="%i", min_value=1,
    )
    need_to_show_graphs = st.checkbox("Рисовать графики", value=True)
    display_result(line_segment, partition_count, need_to_show_graphs, function_name=function_name,
                   sympy_function=sympy_function)


if __name__ == "__main__":
    main()
