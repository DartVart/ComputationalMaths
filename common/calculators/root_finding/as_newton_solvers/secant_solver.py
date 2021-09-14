from dataclasses import dataclass
from typing import Optional

from sympy import lambdify

from a.common import AsNewtonMethodSolver
from a.common import Statistic
from a.common import LineSegment


@dataclass
class StatisticWithAdditionalInitial(Statistic):
    additional_value: float = 0.0


class SecantLineSolver(AsNewtonMethodSolver):
    method_name = "Secant line"

    def clear_statistic(self):
        self.stat.values = []
        self.stat.additional_value = 0.0

    def __init__(self):
        super().__init__()
        self.stat = StatisticWithAdditionalInitial()

    def _find_root_with_initial(
        self, function, line_segment: LineSegment, accuracy, initial_value, variable: str = "x"
    ) -> Optional[float]:
        self.clear_statistic()
        func_as_lambda = lambdify(variable, function)

        step_counter = 0
        prev_value = None
        prev_function_value = None
        cur_value = initial_value

        self.stat.values.append(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            if prev_value is None:
                prev_prev_value = line_segment.right
                self.stat.additional_value = prev_prev_value
                prev_prev_function_value = func_as_lambda(prev_prev_value)
            else:
                prev_prev_value = prev_value
                prev_prev_function_value = prev_function_value

            prev_value = cur_value
            prev_function_value = func_as_lambda(prev_value)

            cur_value = prev_value - prev_function_value * (prev_value - prev_prev_value) / (
                prev_function_value - prev_prev_function_value
            )

            self.stat.values.append(cur_value)
        return cur_value