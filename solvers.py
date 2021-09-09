from abc import ABC, abstractmethod
from sympy import diff
from line_segment import LineSegment
from root_separator import RootSeparator


class SingleRootSolver(ABC):
    @abstractmethod
    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        pass


class WithStatistic(ABC):
    def __init__(self, on_get_new_value=lambda statistic: None):
        self.statistic = self._get_initial_statistic()
        self._on_get_new_value = on_get_new_value

    def _clear_statistic(self):
        self.statistic = self._get_initial_statistic()

    @staticmethod
    @abstractmethod
    def _get_initial_statistic():
        pass

    @abstractmethod
    def _update_statistic(self, value):
        pass


class WithHalfDivisionStatistic(WithStatistic):
    @staticmethod
    def _get_initial_statistic():
        return {
            'number_of_steps': 0,
            'approximating_segments': [],
            'approximating_values': []
        }

    def _update_statistic(self, segment):
        self.statistic['number_of_steps'] += 1
        self._save_segment_to_statistic(segment)
        self._on_get_new_value(self.statistic)

    def _save_segment_to_statistic(self, segment):
        self.statistic['approximating_segments'].append(segment.copy())
        self.statistic['approximating_values'].append(segment.center)


# It is assumed that there is exactly one non-multiple root inside the line segment
class HalfDivisionSolver(WithHalfDivisionStatistic, SingleRootSolver):
    def __init__(self, on_get_new_value=lambda statistic: None):
        super().__init__(on_get_new_value)
        self.statistic = self._get_initial_statistic()

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self._clear_statistic()

        cur_segment = line_segment

        self._save_segment_to_statistic(cur_segment)

        left_function_value = function.subs({variable: cur_segment.left})
        right_function_value = function.subs({variable: cur_segment.right})

        while cur_segment.length > 2 * accuracy:

            center_function_value = function.subs({variable: cur_segment.center})

            if left_function_value * center_function_value <= 0:
                cur_segment.right = cur_segment.center
                right_function_value = center_function_value
            elif center_function_value * right_function_value <= 0:
                cur_segment.left = cur_segment.center
                left_function_value = center_function_value
            else:
                raise ValueError("Some error")

            self._update_statistic(cur_segment)

        return cur_segment.center


class WithOneValueStatistic(WithStatistic):
    @staticmethod
    def _get_initial_statistic():
        return {
            'number_of_steps': 0,
            'approximating_values': []
        }

    def _update_statistic(self, value):
        self.statistic['number_of_steps'] += 1
        self.statistic['approximating_values'].append(value)
        self._on_get_new_value(self.statistic)

    def _save_new_value_to_statistic(self, value):
        self.statistic['approximating_values'].append(value)


class NewtonMethodSolver(WithOneValueStatistic, SingleRootSolver):
    def __init__(self, max_iterations=1000, on_get_new_value=lambda statistic: None):
        super().__init__(on_get_new_value)
        self.max_iterations = max_iterations

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self._clear_statistic()

        derivative = diff(function)
        prev_value = None
        cur_value = line_segment.left

        self._save_new_value_to_statistic(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            prev_value = cur_value
            cur_value = prev_value - function.subs({variable: prev_value}) / derivative.subs({variable: prev_value})

            self._update_statistic(cur_value)

        return cur_value


class ModifiedNewtonMethodSolver(WithOneValueStatistic, SingleRootSolver):
    def __init__(self, max_iterations=1000, on_get_new_value=lambda statistic: None):
        super().__init__(on_get_new_value)
        self.max_iterations = max_iterations

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self._clear_statistic()

        prev_value = None
        cur_value = line_segment.left
        derivative_value = diff(function).subs({variable: cur_value})

        self._save_new_value_to_statistic(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            prev_value = cur_value
            cur_value = prev_value - function.subs({variable: prev_value}) / derivative_value

            self._update_statistic(cur_value)

        return cur_value


class SecantLineSolver(WithOneValueStatistic, SingleRootSolver):
    def __init__(self, max_iterations=1000, on_get_new_value=lambda statistic: None):
        super().__init__(on_get_new_value)
        self.max_iterations = max_iterations

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self._clear_statistic()

        prev_value = None
        cur_value = line_segment.left
        derivative_value = diff(function).subs({variable: cur_value})

        self._save_new_value_to_statistic(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            prev_value = cur_value
            cur_value = prev_value - function.subs({variable: prev_value}) / derivative_value

            self._update_statistic(cur_value)

        return cur_value


class Solver:
    def __init__(self, single_root_solver):
        self.single_root_solver = single_root_solver
        self.root_separator = RootSeparator()

    def find_roots(self, function, line_segment, accuracy, number_of_steps, variable: str = 'x'):
        segments = self.root_separator.separate(function, line_segment, number_of_steps, variable)
        roots = []

        for segment in segments:
            root = self.single_root_solver.find_root(function, segment, accuracy, variable)
            roots.append(root)

        return roots
