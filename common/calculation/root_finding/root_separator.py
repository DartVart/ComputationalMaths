from typing import List
from sympy import lambdify

from common.calculation.root_finding.utils import get_lambda_func
from common.models.line_segment import LineSegment
from config import COMPUTER_DEVIATION


class RootSeparator:
    @staticmethod
    def separate(expression, line_segment: LineSegment, number_of_steps: int, variable: str = "x") -> List[LineSegment]:
        function = get_lambda_func(expression, variable)
        segments = []
        step = line_segment.length / number_of_steps
        cur_segment = line_segment.copy()
        left_function_value = function(cur_segment.left)

        for _ in range(number_of_steps):
            cur_segment.right = cur_segment.left + step
            right_function_value = function(cur_segment.right)

            if left_function_value * right_function_value < COMPUTER_DEVIATION and (
                len(segments) == 0 or abs(left_function_value) > COMPUTER_DEVIATION
            ):
                segments.append(cur_segment.copy())
            left_function_value = right_function_value
            cur_segment.left = cur_segment.right

        return segments
