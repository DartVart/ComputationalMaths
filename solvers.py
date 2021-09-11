from abc import ABC, abstractmethod
from typing import Optional
from sympy import diff

from config import COMPUTER_DEVIATION
from line_segment import LineSegment

STEP_PASSED = 'step_passed'
COMPUTATION_COMPLETED = 'computation_completed'
INITIAL_VALUE_CHANGED = 'initial_value_changed'


class SingleRootSolver(ABC):
    @abstractmethod
    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        pass


def default_on_action(action_type, payload=None):
    if payload is None:
        payload = {}


class HalfDivisionSolver(SingleRootSolver):
    def __init__(self, on_action=default_on_action):
        self.on_action = on_action

    def on_step_passed(self, segment, value):
        self.on_action(STEP_PASSED, {
            'segment': segment,
            'value': value
        })

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        step_counter = 0
        cur_segment = line_segment

        self.on_step_passed(cur_segment, cur_segment.center)

        left_function_value = function.subs({variable: cur_segment.left})

        while cur_segment.length > 2 * accuracy:
            step_counter += 1
            center_function_value = function.subs({variable: cur_segment.center})

            if left_function_value * center_function_value < COMPUTER_DEVIATION:
                cur_segment.right = cur_segment.center
            else:
                cur_segment.left = cur_segment.center
                left_function_value = center_function_value

            self.on_step_passed(cur_segment, cur_segment.center)

        self.on_action(COMPUTATION_COMPLETED)
        return cur_segment.center


class AccordingToNewtonMethodSolver(SingleRootSolver, ABC):
    def __init__(self, on_action=default_on_action, max_iterations=100, max_number_of_initial_values=5):
        self.max_iterations = max_iterations
        self.max_number_of_initial_values = max_number_of_initial_values
        self.on_action = on_action

    def on_step_passed(self, value):
        self.on_action(STEP_PASSED, {
            'value': value
        })

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        initial_value = line_segment.left
        step = line_segment.length / self.max_number_of_initial_values
        result = None

        while result is None:
            if initial_value > line_segment.right:
                raise RuntimeError("Value not found.")

            result = self._find_root_with_initial(function, line_segment, accuracy, initial_value, variable)
            initial_value += step

            if result is not None and result < line_segment.left or result > line_segment.right:
                result = None

            if result is None:
                self.on_action(INITIAL_VALUE_CHANGED)

        self.on_action(COMPUTATION_COMPLETED)
        return result

    @abstractmethod
    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        """Does no more than max_iterations iterations. Otherwise, it returns None."""
        pass


class NewtonMethodSolver(AccordingToNewtonMethodSolver):
    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        step_counter = 0
        prev_value = None
        cur_value = initial_value
        derivative = diff(function)

        self.on_step_passed(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            prev_value = cur_value
            cur_value = float(
                prev_value - function.subs({variable: prev_value}) / derivative.subs({variable: prev_value}))

            self.on_step_passed(cur_value)

        return cur_value


class ModifiedNewtonMethodSolver(AccordingToNewtonMethodSolver):
    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        step_counter = 0
        prev_value = None
        cur_value = initial_value
        derivative_value = diff(function).subs({variable: initial_value})

        self.on_step_passed(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            prev_value = cur_value
            cur_value = float(prev_value - function.subs({variable: prev_value}) / derivative_value)

            self.on_step_passed(cur_value)

        return cur_value


SECOND_VALUE_INITIALIZING = 'second_value_initializing'


class SecantLineSolver(AccordingToNewtonMethodSolver):
    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        step_counter = 0
        prev_value = None
        prev_function_value = None
        cur_value = initial_value

        self.on_step_passed(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            if prev_value is None:
                prev_prev_value = line_segment.right
                self.on_action(SECOND_VALUE_INITIALIZING, prev_prev_value)
                prev_prev_function_value = function.subs({variable: prev_prev_value})
            else:
                prev_prev_value = prev_value
                prev_prev_function_value = prev_function_value

            prev_value = cur_value
            prev_function_value = function.subs({variable: prev_value})

            cur_value = float(prev_value - prev_function_value * (prev_value - prev_prev_value) / (
                    prev_function_value - prev_prev_function_value))

            self.on_step_passed(cur_value)

        return cur_value


class Solver:
    def __init__(self, single_root_solver, root_separator):
        self.single_root_solver = single_root_solver
        self.root_separator = root_separator

    def find_roots(self, function, line_segment, accuracy, number_of_steps, variable: str = 'x'):
        segments = self.root_separator.separate(function, line_segment, number_of_steps, variable)
        roots = []

        for segment in segments:
            root = self.single_root_solver.find_root(function, segment, accuracy, variable)
            roots.append(float(root))

        return roots
