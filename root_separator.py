from typing import List

from sympy import lambdify

from config import COMPUTER_DEVIATION
from line_segment import LineSegment
from solvers import COMPUTATION_COMPLETED


def default_on_action(action_type, payload=None):
    if payload is None:
        payload = {}


NEW_SEGMENT_RECEIVED = 'new_segment_received'
CALCULATION_STARTED = 'calculation_started'


class RootSeparator:
    def __init__(self, on_action=default_on_action):
        self.on_action = on_action

    def on_new_segment_received(self, segment):
        self.on_action(NEW_SEGMENT_RECEIVED, {
            'segment': segment
        })

    def separate(self, expression, line_segment: LineSegment,
                 number_of_steps: int, variable: str = 'x') -> List[LineSegment]:
        self.on_action(CALCULATION_STARTED)

        function = lambdify(variable, expression)
        segments = []
        step = line_segment.length / number_of_steps
        cur_segment = line_segment
        left_function_value = function(cur_segment.left)

        for _ in range(number_of_steps):
            cur_segment.right = cur_segment.left + step
            right_function_value = function(cur_segment.right)
            # todo: добавить погрешность?
            if left_function_value * right_function_value < COMPUTER_DEVIATION \
                    and (len(segments) == 0 or abs(left_function_value) > COMPUTER_DEVIATION):
                cur_segment_copy = cur_segment.copy()
                segments.append(cur_segment.copy())
                self.on_new_segment_received(cur_segment_copy)
            left_function_value = right_function_value
            cur_segment.left = cur_segment.right

        self.on_action(COMPUTATION_COMPLETED)
        return segments
