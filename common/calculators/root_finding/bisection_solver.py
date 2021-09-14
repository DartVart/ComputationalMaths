from dataclasses import dataclass

from sympy import lambdify

from a.common.calculators.root_finding.single_root_solver import SingleRootSolver
from a.common import Statistic
from a.common import LineSegment
from a.config import COMPUTER_DEVIATION


@dataclass
class BisectionStatistic(Statistic):
    last_segment_length: float = 0.0


class BisectionSolver(SingleRootSolver):
    method_name = "Bisection"

    def __init__(self):
        super().__init__()
        self.stat = BisectionStatistic()

    def clear_statistic(self):
        self.stat.values = []
        self.stat.last_segment_length = 0

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = "x") -> float:
        self.clear_statistic()
        func_as_lambda = lambdify(variable, function)

        step_counter = 0
        cur_segment = line_segment.copy()

        self.stat.values.append(cur_segment.center)

        left_function_value = func_as_lambda(cur_segment.left)

        while cur_segment.length > 2 * accuracy:
            step_counter += 1
            center_function_value = func_as_lambda(cur_segment.center)

            if left_function_value * center_function_value < COMPUTER_DEVIATION:
                cur_segment.right = cur_segment.center
            else:
                cur_segment.left = cur_segment.center
                left_function_value = center_function_value

            self.stat.values.append(cur_segment.center)

        self.stat.last_segment_length = cur_segment.length
        return cur_segment.center
