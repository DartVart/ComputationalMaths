from abc import ABC, abstractmethod
from typing import Optional, List

from dataclasses import dataclass, field, replace
from sympy import diff

from config import COMPUTER_DEVIATION
from line_segment import LineSegment
from root_separator import RootSeparator


class SingleRootSolver(ABC):
    method_name: str

    def __init__(self):
        self.stat = Statistic()

    @abstractmethod
    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        pass


@dataclass
class Statistic:
    values: List[float] = field(default_factory=list)


@dataclass
class HalfDivisionStatistic(Statistic):
    last_segment_length: float = 0.0


class HalfDivisionSolver(SingleRootSolver):
    method_name = 'Half division'

    def __init__(self):
        super().__init__()
        self.stat = HalfDivisionStatistic()

    def clear_statistic(self):
        self.stat.values = []
        self.stat.last_segment_length = 0

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = 'x') -> float:
        self.clear_statistic()

        step_counter = 0
        cur_segment = line_segment.copy()

        self.stat.values.append(cur_segment.center)

        left_function_value = function.subs({variable: cur_segment.left})

        while cur_segment.length > 2 * accuracy:
            step_counter += 1
            center_function_value = function.subs({variable: cur_segment.center})

            if left_function_value * center_function_value < COMPUTER_DEVIATION:
                cur_segment.right = cur_segment.center
            else:
                cur_segment.left = cur_segment.center
                left_function_value = center_function_value

            self.stat.values.append(cur_segment.center)

        self.stat.last_segment_length = cur_segment.length
        return cur_segment.center


class AccordingToNewtonMethodSolver(SingleRootSolver, ABC):
    def __init__(self, max_iterations=100, max_number_of_initial_values=5):
        super().__init__()
        self.max_iterations = max_iterations
        self.max_number_of_initial_values = max_number_of_initial_values

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

        return result

    @abstractmethod
    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        """Does no more than max_iterations iterations. Otherwise, it returns None."""
        pass


class NewtonMethodSolver(AccordingToNewtonMethodSolver):
    method_name = 'Newton method'

    def clear_statistic(self):
        self.stat.values = []

    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        self.clear_statistic()

        step_counter = 0
        prev_value = None
        cur_value = initial_value
        derivative = diff(function)

        self.stat.values.append(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            prev_value = cur_value
            cur_value = float(
                prev_value - function.subs({variable: prev_value}) / derivative.subs({variable: prev_value}))

            self.stat.values.append(cur_value)

        return cur_value


class ModifiedNewtonMethodSolver(AccordingToNewtonMethodSolver):
    method_name = 'Modified Newton method'

    def clear_statistic(self):
        self.stat.values = []

    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        self.clear_statistic()

        step_counter = 0
        prev_value = None
        cur_value = initial_value
        derivative_value = diff(function).subs({variable: initial_value})

        self.stat.values.append(cur_value)

        while prev_value is None or (abs(cur_value - prev_value) > accuracy):
            step_counter += 1
            if step_counter > self.max_iterations:
                return None

            prev_value = cur_value
            cur_value = float(prev_value - function.subs({variable: prev_value}) / derivative_value)

            self.stat.values.append(cur_value)

        return cur_value


@dataclass
class StatisticWithAdditionalInitial(Statistic):
    additional_value: float = 0.0


class SecantLineSolver(AccordingToNewtonMethodSolver):
    method_name = 'Secant line'

    def clear_statistic(self):
        self.stat.values = []
        self.stat.additional_value = 0.0

    def __init__(self):
        super().__init__()
        self.stat = StatisticWithAdditionalInitial()

    def _find_root_with_initial(self, function, line_segment: LineSegment, accuracy, initial_value,
                                variable: str = 'x') -> Optional[float]:
        self.clear_statistic()

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
                prev_prev_function_value = function.subs({variable: prev_prev_value})
            else:
                prev_prev_value = prev_value
                prev_prev_function_value = prev_function_value

            prev_value = cur_value
            prev_function_value = function.subs({variable: prev_value})

            cur_value = float(prev_value - prev_function_value * (prev_value - prev_prev_value) / (
                    prev_function_value - prev_prev_function_value))

            self.stat.values.append(cur_value)
            print(abs(cur_value - prev_value))

        return cur_value


@dataclass
class SolverStatistic:
    segments: List[float] = field(default_factory=list)
    single_solver_statistics: List[Statistic] = field(default_factory=list)


class Solver:
    def __init__(self, single_root_solver):
        self.single_root_solver = single_root_solver
        self.root_separator = RootSeparator()
        self.stat = SolverStatistic()

    def find_roots(self, function, line_segment, accuracy, number_of_steps, variable: str = 'x'):
        self.stat.segments = self.root_separator.separate(function, line_segment, number_of_steps, variable)
        roots = []

        for segment in self.stat.segments:
            root = self.single_root_solver.find_root(function, segment, accuracy, variable)
            self.stat.single_solver_statistics.append(replace(self.single_root_solver.stat))
            roots.append(float(root))

        return roots
