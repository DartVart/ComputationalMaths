from sympy import diff
from sympy.parsing.sympy_parser import parse_expr
from line_segment import LineSegment
from solvers import ModifiedNewtonMethodSolver, Solver


def print_stat(stat):
    print(f"{stat['number_of_steps']}  {stat['approximating_values'][-1]}")


if __name__ == "__main__":
    print("Start\n")
    expr = parse_expr("sin(2*x)-0.5")
    solver = Solver(ModifiedNewtonMethodSolver(on_get_new_value=print_stat))

    print(solver.find_roots(expr, LineSegment(0, 2), 10e-5, 10))

    print(float(diff(expr).subs({'x': 2})))
