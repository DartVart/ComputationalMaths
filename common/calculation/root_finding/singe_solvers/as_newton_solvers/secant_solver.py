from dataclasses import dataclass
from typing import Optional

from sympy import lambdify
from sympy.core.assumptions import ManagedProperties

from common.calculation.root_finding.singe_solvers.as_newton_solvers.iterating_over_initial_values import (
    IteratingOverInitialValues,
)
from common.calculation.root_finding.utils import Statistic, get_lambda_func
from common.models.line_segment import LineSegment


@dataclass
class StatisticWithAdditionalInitial(Statistic):
    additional_value: float = 0.0


class SecantLineSolver(IteratingOverInitialValues):
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
        func_as_lambda = get_lambda_func(function, variable)

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
            if prev_function_value - prev_prev_function_value == 0:
                return None
            cur_value = prev_value - prev_function_value * (prev_value - prev_prev_value) / (
                prev_function_value - prev_prev_function_value
            )

            self.stat.values.append(cur_value)
        return cur_value
