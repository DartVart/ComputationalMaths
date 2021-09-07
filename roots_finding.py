from typing import List
from abc import ABC, abstractmethod
from sympy.parsing.sympy_parser import parse_expr


class LineSegment:
    def __init__(self, left: float, right: float):
        if right < left:
            raise ValueError("The beginning of a line segment cannot exceed its end.")

        self.left = left
        self.right = right

    @property
    def length(self):
        return self.right - self.left

    @property
    def center(self):
        return (self.right + self.left) / 2

    def to_string(self):
        return f"[{self.left}, {self.right}]"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


def separate_roots(function, line_segment: LineSegment,
                   number_of_steps: int, variable: str = 'x') -> List[LineSegment]:
    segments = []
    step = line_segment.length / number_of_steps
    cur_segment = line_segment
    left_function_value = function.subs({variable: cur_segment.left})

    for _ in range(number_of_steps):
        cur_segment.right = cur_segment.left + step
        right_function_value = function.subs({variable: cur_segment.right})
        if left_function_value * right_function_value <= 0:  # todo: добавить погрешность?
            segments.append(LineSegment(cur_segment.left, cur_segment.right))
        left_function_value = right_function_value
        cur_segment.left = cur_segment.right

    return segments


class SingleRootSolver(ABC):
    @abstractmethod
    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        pass


# It is assumed that there is exactly one non-multiple root inside the line segment
class HalfDivisionSolver(SingleRootSolver):
    def __init__(self):
        self.number_of_iterations = 0

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self.number_of_iterations = 0

        cur_segment = line_segment
        left_function_value = function.subs({variable: cur_segment.left})
        right_function_value = function.subs({variable: cur_segment.right})

        while cur_segment.length / 2 > accuracy:
            self.number_of_iterations += 1
            center_function_value = function.subs({variable: cur_segment.center})

            if left_function_value * center_function_value <= 0:
                cur_segment.right = cur_segment.center
                right_function_value = center_function_value
            elif center_function_value * right_function_value <= 0:
                cur_segment.left = cur_segment.center
                left_function_value = center_function_value
            else:
                raise ValueError("Some error")

        return cur_segment.center


class Solver:
    def __init__(self, single_root_solver):
        self.single_root_solver = single_root_solver

    def find_roots(self, function, line_segment, accuracy, number_of_steps, variable: str = 'x'):
        segments = separate_roots(function, line_segment, number_of_steps, variable)
        roots = []

        for segment in segments:
            root = self.single_root_solver.find_root(function, segment, accuracy, variable)
            roots.append(root)

        return roots


if __name__ == "__main__":
    print("Start\n")
    expr = parse_expr("sin(2*x)-0.5")
    solver = Solver(HalfDivisionSolver())
    print(solver.find_roots(expr, LineSegment(0, 2), 10e-15, 10))
