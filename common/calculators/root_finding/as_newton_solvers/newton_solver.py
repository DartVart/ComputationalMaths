from typing import Optional

from sympy import lambdify, diff

from common.calculators.root_finding.as_newton_solvers.as_newton_solver import AsNewtonMethodSolver
from common.models.line_segment import LineSegment


class NewtonMethodSolver(AsNewtonMethodSolver):
    method_name = "Newton method"

    def clear_statistic(self):
        self.stat.values = []

    def _find_root_with_initial(
        self, function, line_segment: LineSegment, accuracy, initial_value, variable: str = "x"
    ) -> Optional[float]:
        self.clear_statistic()

        func_as_lambda = lambdify(variable, function)
        step_counter = 0
        prev_value = None
        cur_value = initial_value
        derivative = lambdify(variable, diff(function))

        self.stat.values.append(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            prev_value = cur_value
            cur_value = prev_value - func_as_lambda(prev_value) / derivative(prev_value)

            self.stat.values.append(cur_value)

        return cur_value
