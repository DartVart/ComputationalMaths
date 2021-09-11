from typing import List, Dict

from sympy import diff, lambdify
from sympy.parsing.sympy_parser import parse_expr
from line_segment import LineSegment
from root_separator import RootSeparator, NEW_SEGMENT_RECEIVED, CALCULATION_STARTED
from solvers import STEP_PASSED, COMPUTATION_COMPLETED, HalfDivisionSolver, Solver, NewtonMethodSolver, \
    INITIAL_VALUE_CHANGED, ModifiedNewtonMethodSolver, SecantLineSolver, SECOND_VALUE_INITIALIZING
import streamlit as st
import matplotlib.pyplot as plt


def get_initial_statistic():
    return {
        'step_counter': -1,
        'segment': [],
        'value': []
    }


def get_on_action(statistics: List[Dict]):
    if len(statistics) == 0:
        statistics.append(get_initial_statistic())

    def on_action(action_type, payload=None):
        if payload is None:
            payload = {}

        if action_type == STEP_PASSED:
            statistics[-1]['step_counter'] += 1
            # statistics[-1]['segment'].append(payload['segment'])
            statistics[-1]['value'].append(payload['value'])
        elif action_type == COMPUTATION_COMPLETED:
            print(statistics[-1])
            statistics.append(get_initial_statistic())
        elif action_type == INITIAL_VALUE_CHANGED:
            statistics[-1] = get_initial_statistic()
        elif action_type == SECOND_VALUE_INITIALIZING:
            print(payload)

    return on_action


class StatisticHandler:
    def __init__(self, print_text):
        self.values = None
        self.set_initial_statistic()
        self.print_text = print_text

    def set_initial_statistic(self):
        self.values = []

    def get_on_action(self, on_start, on_end):
        def on_action(action_type, payload=None):
            if payload is None:
                payload = {}

            if action_type == STEP_PASSED:
                self.values.append(payload['value'])
                # self.print_text(f"{len(self.values)}. {payload['value']}")
            elif action_type == COMPUTATION_COMPLETED:
                on_end(self.values)
                self.set_initial_statistic()
            elif action_type == CALCULATION_STARTED:
                on_start()

        return on_action


class RootSeparatorStatisticHandler:
    def __init__(self, print_text):
        self.segments = None
        self.set_initial_statistic()
        self.print_text = print_text

    def set_initial_statistic(self):
        self.segments = []

    def get_on_action(self, on_start, on_end):
        def on_action(action_type, payload=None):
            if payload is None:
                payload = {}

            if action_type == NEW_SEGMENT_RECEIVED:
                self.segments.append(payload['segment'])
                self.print_text(f"{len(self.segments)}. {payload['segment']}")
            elif action_type == COMPUTATION_COMPLETED:
                on_end(self.segments)
            elif action_type == CALCULATION_STARTED:
                on_start()

        return on_action


# def get_on_action_2(stremlt, on_end):
#     def on_action(action_type, payload=None):
#         if payload is None:
#             payload = {}
#
#         if action_type == NEW_SEGMENT_RECEIVED:
#             stremlt.text(payload['segment'])
#         elif action_type == COMPUTATION_COMPLETED:
#             on_end()
#
#     return on_action

def on_start_calc():
    st.subheader('Separation of roots')


def on_end_calc(segments):
    st.text(f"Total count: {len(segments)}")

    x_min = []
    x_max = []

    fig, ax = plt.subplots(figsize=(7.0, 0.5))
    ax.tick_params(left=False, labelleft=False)

    for segment in segments:
        x_min.append(segment.left)
        x_max.append(segment.right)
        ax.plot(segment.left, 0, 'go', color="#ff0067")
        ax.plot(segment.right, 0, 'go', color="#ff0067")

    ax.hlines([0] * len(segments), x_min, x_max, color='#ff0067')
    st.pyplot(fig)


def on_end_clarification(values):
    st.text(f"Number of steps: {len(values)}")
    st.text(f"Approximate solution: {values[-1]}")
    st.text(f"|x_m - x_(m-1)|: {abs(values[-1] - values[-2])}")


def main():
    solvers = {
        'Half division': HalfDivisionSolver,
        'Newton method': NewtonMethodSolver,
        'Modified Newton method': ModifiedNewtonMethodSolver,
        'Secant line': SecantLineSolver,
        # todo: ALL
    }

    stat_handler = RootSeparatorStatisticHandler(st.text)

    st.title('Evaluating the roots')
    expression = st.text_input('Enter expression', '2^(-x)-sin(x)')
    function = parse_expr(process_expression(expression))
    func_as_lambda = lambdify('x', function)

    solver_name = st.selectbox("Choose what you want to colorize:", tuple(solvers))
    solver = Solver(solvers[solver_name](StatisticHandler(st.text).get_on_action(on_start_calc, on_end_clarification)),
                    RootSeparator(stat_handler.get_on_action(on_start_calc, on_end_calc)))
    # (self, function, line_segment, accuracy, number_of_steps, variable: str = 'x')

    segment_col1, segment_col2 = st.columns(2)
    left_bound = segment_col1.number_input('Enter line boundaries', step=1.0, value=-5.0)
    right_bound = segment_col2.number_input('', step=1.0, value=10.0)

    accuracy = st.number_input('Enter accuracy', format='%e', value=10e-6)
    number_of_steps = st.number_input('Enter how many parts the segment will be divided into', value=25, step=1,
                                      format='%i')

    if st.button('evaluate'):
        st.header('Result')

        result = solver.find_roots(function, LineSegment(left_bound, right_bound), accuracy, number_of_steps)
        st.text(f"Residual values: {abs(func_as_lambda(result[0]))}")
        st.latex(result)


def process_expression(expression: str) -> str:
    return expression.replace("^", "**")


def calc():
    print("Start\n")
    # expr = parse_expr("x**2-4")
    expr = parse_expr(process_expression("2^(-x)-sin(x)"))
    # expr = parse_expr("sin(2*x)-0.5")
    stat = []
    # solver = Solver(NewtonMethodSolver(get_on_action(stat)))
    # solver = Solver(ModifiedNewtonMethodSolver(get_on_action(stat)))
    solver = Solver(SecantLineSolver(get_on_action(stat)), RootSeparator())
    # solver = Solver(HalfDivisionSolver(get_on_action(stat)))

    # print(solver.find_roots(expr, LineSegment(-3, 3), 10e-5, 6))
    # print(solver.find_roots(expr, LineSegment(-3, 3), 10e-5, 3))
    # print(solver.find_roots(expr, LineSegment(-2, 2), 10e-5, 10))
    print(solver.find_roots(expr, LineSegment(-5, 10), 10e-6, 25))
    ex = parse_expr("x**2")
    func = lambdify('x', ex)
    print(func(4))
    print(float(3) / 10)


# [0.6761871337890625, 3.017813110351563, 6.295913696289061, 9.423318481445309]
if __name__ == "__main__":
    main()
