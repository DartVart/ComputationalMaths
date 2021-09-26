import sys
from typing import List

sys.path.append("")
sys.path.append("../..")

from common.calculation.root_finding.root_calculator import RootCalculator
from common.calculation.root_finding.singe_solvers.as_newton_solvers.modified_newton_solver import (
    ModifiedNewtonMethodSolver,
)
from common.calculation.root_finding.singe_solvers.as_newton_solvers.newton_solver import NewtonMethodSolver
from common.calculation.root_finding.singe_solvers.as_newton_solvers.secant_solver import SecantLineSolver
from common.calculation.root_finding.singe_solvers.bisection_solver import BisectionSolver
from common.models.line_segment import LineSegment
from sympy import lambdify
from sympy.parsing.sympy_parser import parse_expr
import streamlit as st
from config import THEME_COLOR
import plotly.graph_objects as go

LINE_START = "$\quad$"


def display_segments(segments: List[LineSegment]):
    for index, segment in enumerate(segments):
        st.markdown(rf"""{LINE_START} {index + 1}. ${segment}$""")

    st.markdown(rf"""{LINE_START} Total count: $\;$ ${len(segments)}$""")

    fig = go.Figure()
    for segment in segments:
        fig.add_trace(
            go.Scatter(
                x=[segment.left, segment.right],
                y=[0, 0],
                marker={"size": 7},
                line={"color": THEME_COLOR, "width": 3},
                name="",
                hovertemplate="%{x}",
            )
        )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, zeroline=True, zerolinecolor="gray", zerolinewidth=2, showticklabels=False)
    fig.update_layout(height=70, plot_bgcolor="white", showlegend=False, margin=dict(b=0, t=60))
    st.write(fig)


def display_approximate_values(statistic, function, method_name):
    values = statistic.values
    st.markdown(rf"""{LINE_START} The number of steps $m$: $\;$ ${len(values) - 1}$""")
    st.markdown(rf"""{LINE_START} Initial approximation $x_{0}$: $\;$ ${values[0]}$""")
    if method_name == SecantLineSolver.method_name:
        st.markdown(rf"""{LINE_START} Second initial approximation: $\;$ ${statistic.additional_value}$""")
    st.markdown(rf"""{LINE_START} Final approximation $x_m$: $\;$ ${values[-1]}$""")

    if method_name == BisectionSolver.method_name:
        st.markdown(rf"""{LINE_START} The length of the last segment: $\;$ ${statistic.last_segment_length}$""")
    else:
        st.markdown(rf"""{LINE_START} $|x_m - x_{{m-1}}|$: $\;$ ${abs(values[-1] - values[-2])}$""")
    st.markdown(rf"""{LINE_START} $|f(x_m) - 0|$: $\;$ ${abs(function(values[-1]))}$""")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(values))),
            y=values,
            marker=dict(size=7),
            line=dict(color=THEME_COLOR, width=3),
            name="",
            hovertemplate="Step: %{x}<br>" + "Value: %{y}",
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=30),
        height=230,
    )

    st.plotly_chart(fig)


def main():
    solvers = {
        BisectionSolver.method_name: BisectionSolver,
        NewtonMethodSolver.method_name: NewtonMethodSolver,
        ModifiedNewtonMethodSolver.method_name: ModifiedNewtonMethodSolver,
        SecantLineSolver.method_name: SecantLineSolver,
    }

    st.title("Evaluating the roots")
    expression = st.text_input("Enter expression", "2^(-x)-sin(x)")
    function = parse_expr(process_expression(expression))
    func_as_lambda = lambdify("x", function)

    solver_name = st.selectbox("Choose what you want to colorize", tuple(solvers))
    solver = RootCalculator(solvers[solver_name]())

    segment_col1, segment_col2 = st.columns(2)
    left_bound = segment_col1.number_input("Enter line boundaries", step=1.0, value=-5.0)
    right_bound = segment_col2.number_input("", step=1.0, value=10.0)

    accuracy = st.number_input("Enter accuracy", format="%e", value=1e-6)
    number_of_steps = st.number_input(
        "Enter how many parts the segment will be divided into", value=100, step=1, format="%i"
    )

    if st.button("Evaluate"):
        st.title("Result")
        result = solver.find_roots(function, LineSegment(left_bound, right_bound), accuracy, number_of_steps)

        st.header("Separation of roots")
        display_segments(solver.stat.segments)

        st.header("Refinement of the solution")
        for i in range(len(result)):
            st.subheader(f"Root {i + 1}")
            if result[i] is None:
                st.error("Couldn't find a solution :(")
            else:
                display_approximate_values(solver.stat.single_solver_statistics[i], func_as_lambda, solver_name)


def process_expression(expression: str) -> str:
    return expression.replace("^", "**")


if __name__ == "__main__":
    main()
