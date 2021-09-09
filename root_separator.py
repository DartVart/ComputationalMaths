from typing import List
from line_segment import LineSegment


class RootSeparator:
    def __init__(self, on_get_new_segment=lambda line_segment: None):
        self.on_get_new_segment = on_get_new_segment

    def separate(self, function, line_segment: LineSegment,
                 number_of_steps: int, variable: str = 'x') -> List[LineSegment]:
        segments = []
        step = line_segment.length / number_of_steps
        cur_segment = line_segment
        left_function_value = function.subs({variable: cur_segment.left})

        for _ in range(number_of_steps):
            cur_segment.right = cur_segment.left + step
            right_function_value = function.subs({variable: cur_segment.right})
            if left_function_value * right_function_value <= 0:  # todo: добавить погрешность?
                segments.append(cur_segment.copy())
                self.on_get_new_segment(cur_segment)
            left_function_value = right_function_value
            cur_segment.left = cur_segment.right

        return segments
