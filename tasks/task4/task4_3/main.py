import sys

sys.path.append("")
sys.path.append("../../..")

from common.calculation.integrating.compound_quadrature_formulas import get_sum_in_middle_nodes, \
    get_sum_in_middle_of_segments, get_sum_at_extremes, RightRectanglesFormula, LeftRectanglesFormula, \
    MiddleRectanglesFormula, TrapezesFormula, SimpsonFormula, ThreeFractionsOfEightFormula
from sympy import integrate, lambdify
import streamlit as st
from common.models.line_segment import LineSegment
from tasks.utils.streamlit import set_initial_key, display_whitespace, display_title, get_new_key, \
    input_line_segment, input_sympy_function
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator

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


def display_result(line_segment: LineSegment, partition_count, addition_partition_count, sympy_function=None):
    display_title(st, "Результат", 2)
    function = lambdify("x", sympy_function)
    try:
        integral = lambdify("x", integrate(sympy_function))
    except ValueError:  # constant
        integral = lambda x: int(str(sympy_function)) * x
    real_integral_value = integral(line_segment.right) - integral(line_segment.left)

    bigger_partition_count = partition_count * addition_partition_count

    st.markdown(rf"""{LINE_START} Точное значение интеграла $J = {real_integral_value}$""")
    st.markdown(rf"""{LINE_START} $h = {line_segment.length / partition_count}$""")
    st.markdown(rf"""{LINE_START} $h / l = {line_segment.length / bigger_partition_count}$""")


    h_additional_params = get_additional_params(function, line_segment, partition_count)
    h_l_additional_params = get_additional_params(function, line_segment, bigger_partition_count)
    for quadrature_name in QUADRATURES:
        quadrature = QUADRATURES[quadrature_name]
        h_approx = quadrature.calculate(function, line_segment, partition_count,
                                        *h_additional_params[quadrature_name])

        h_l_approx = quadrature.calculate(function, line_segment,
                                          bigger_partition_count,
                                          *h_l_additional_params[quadrature_name])
        runge_approx = get_integral_with_runge_law(h_approx, h_l_approx, addition_partition_count,
                                                   quadrature.algebraic_precision + 1)
        display_title(st, quadrature_name, 3)
        st.markdown(rf"""{LINE_START} $J(h) = {h_approx}$""")
        st.markdown(rf"""{LINE_START} $J(h/l) = {h_l_approx}$""")
        st.markdown(rf"""{LINE_START} $\overline{{J}} = {runge_approx}$""")
        st.markdown(rf"""{LINE_START} $|J - J(h)| = {abs(real_integral_value - h_approx)}$""")
        st.markdown(rf"""{LINE_START} $|J - J(h/l)| = {abs(real_integral_value - h_l_approx)}$""")
        st.markdown(rf"""{LINE_START} $|J - \overline{{J}}| = {abs(real_integral_value - runge_approx)}$""")


def get_additional_params(function, line_segment, partition_count):
    sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
    sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
    sum_at_extremes = get_sum_at_extremes(function, line_segment)

    return {
        "Формула левых прямоугольников": [sum_in_middle_nodes],
        "Формула правых прямоугольников": [sum_in_middle_nodes],
        "Формула средних прямоугольников": [sum_in_middle_of_segments],
        "Формула трапеций": [sum_at_extremes, sum_in_middle_nodes],
        "Формула Симпсона": [sum_at_extremes, sum_in_middle_nodes, sum_in_middle_of_segments],
        "Формула 3/8": []
    }


def get_integral_with_runge_law(h_integral, h_l_integral, l, r):
    l_in_r_pow = l ** r
    return (l_in_r_pow * h_l_integral - h_integral) / (l_in_r_pow - 1)


def main():
    set_initial_key(st)

    display_title(st, "Приближенное вычисление интеграла")
    display_title(st, "Принцип Рунге", 2)
    display_whitespace(st)

    sympy_function = input_sympy_function(st, "cos(x)", key=get_new_key(st))

    line_segment_columns = st.columns(2)
    line_segment = input_line_segment(line_segment_columns, (get_new_key(st), get_new_key(st)))

    partition_col1, partition_col2 = st.columns(2)
    partition_count = partition_col1.number_input(
        "На сколько частей разбивать отрезок", value=5, step=1, format="%i", min_value=1,
    )
    addition_partition_count = partition_col2.number_input(
        "Множитель l", value=2, step=1, format="%i", min_value=1,
    )

    display_result(line_segment, partition_count, addition_partition_count, sympy_function=sympy_function)


if __name__ == "__main__":
    main()
