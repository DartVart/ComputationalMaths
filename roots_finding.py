from typing import List

from sympy import lambdify
from sympy.parsing.sympy_parser import parse_expr
from line_segment import LineSegment
from solvers import HalfDivisionSolver, Solver, NewtonMethodSolver, ModifiedNewtonMethodSolver, SecantLineSolver
import streamlit as st
import plotly.graph_objects as go

THEME_COLOR = "#ff0067"


def display_segments(segments: List[LineSegment]):
    for index, segment in enumerate(segments):
        st.markdown(rf'''$\quad$ {index + 1}. ${segment}$''')

    st.markdown(rf'''$\quad$ Total count: $\;$ ${len(segments)}$''')

    fig = go.Figure()
    for segment in segments:
        fig.add_trace(go.Scatter(
            x=[segment.left, segment.right],
            y=[0, 0],
            marker={'size': 7},
            line={'color': THEME_COLOR, 'width': 3},
            name="",
            hovertemplate='%{x}'
        ))

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, zeroline=True, zerolinecolor='gray', zerolinewidth=2, showticklabels=False)
    fig.update_layout(height=70, plot_bgcolor='white', showlegend=False,
                      margin=dict(b=0, t=60)
                      )
    st.write(fig)


def display_approximate_values(statistic, function, method_name):
    values = statistic.values
    st.markdown(rf'''$\quad$ The number of steps $m$: $\;$ ${len(values) - 1}$''')
    st.markdown(rf'''$\quad$ Initial approximation $x_{0}$: $\;$ ${values[0]}$''')
    if method_name == SecantLineSolver.method_name:
        st.markdown(rf'''$\quad$ Second initial approximation: $\;$ ${statistic.additional_value}$''')
    st.markdown(rf'''$\quad$ Final approximation $x_m$: $\;$ ${values[-1]}$''')

    if method_name == HalfDivisionSolver.method_name:
        st.markdown(rf'''$\quad$ Half the length of the last segment: $\;$ ${statistic.last_segment_length / 2}$''')
    else:
        st.markdown(rf'''$\quad$ $|x_m - x_{{m-1}}|$: $\;$ ${abs(values[-1] - values[-2])}$''')
    st.markdown(rf'''$\quad$ $|f(x_m) - 0|$: $\;$ ${abs(function(values[-1]))}$''')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))), y=values, marker=dict(size=7), line=dict(color=THEME_COLOR, width=3), name="",
        hovertemplate='Step: %{x}<br>' +
                      'Value: %{y}'
    ))
    fig.update_layout(showlegend=False,
                      margin=dict(l=0, r=0, b=0, t=30),
                      height=230,
                      )

    st.plotly_chart(fig)


def main():
    solvers = {
        HalfDivisionSolver.method_name: HalfDivisionSolver,
        NewtonMethodSolver.method_name: NewtonMethodSolver,
        ModifiedNewtonMethodSolver.method_name: ModifiedNewtonMethodSolver,
        SecantLineSolver.method_name: SecantLineSolver,
        # todo: ALL
    }

    st.title('Evaluating the roots')
    expression = st.text_input('Enter expression', '2^(-x)-sin(x)')
    function = parse_expr(process_expression(expression))
    func_as_lambda = lambdify('x', function)

    solver_name = st.selectbox("Choose what you want to colorize", tuple(solvers))
    solver = Solver(solvers[solver_name]())

    segment_col1, segment_col2 = st.columns(2)
    left_bound = segment_col1.number_input('Enter line boundaries', step=1.0, value=-5.0)
    right_bound = segment_col2.number_input('', step=1.0, value=10.0)

    accuracy = st.number_input('Enter accuracy', format='%e', value=10e-6)
    number_of_steps = st.number_input('Enter how many parts the segment will be divided into', value=25, step=1,
                                      format='%i')

    if st.button('Evaluate'):
        st.balloons()

        st.title('Result')

        result = solver.find_roots(function, LineSegment(left_bound, right_bound), accuracy, number_of_steps)

        st.header("Separation of roots")

        display_segments(solver.stat.segments)

        st.header("Refinement of the solution")

        for i in range(len(result)):
            st.subheader(f'Solution {i + 1}')
            display_approximate_values(solver.stat.single_solver_statistics[i], func_as_lambda, solver_name)
        # st.latex(result)


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
    solver = Solver(SecantLineSolver())
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
    # calc()
