from abc import ABC, abstractmethod
from typing import Optional

from common.calculators.root_finding.single_root_solver import SingleRootSolver
from common.models.line_segment import LineSegment


class AsNewtonMethodSolver(SingleRootSolver, ABC):
    def __init__(self, max_iterations=100, max_number_of_initial_values=1):
        super().__init__()
        self.max_iterations = max_iterations
        self.max_number_of_initial_values = max_number_of_initial_values

    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = "x") -> Optional[float]:
        initial_value = line_segment.left
        step = line_segment.length / self.max_number_of_initial_values
        result = None

        while result is None:
            if initial_value > line_segment.right:
                return None

            result = self._find_root_with_initial(function, line_segment, accuracy, initial_value, variable)
            initial_value += step

            if result is not None and (result < line_segment.left or result > line_segment.right):
                result = None

        return result

    @abstractmethod
    def _find_root_with_initial(
        self, function, line_segment: LineSegment, accuracy, initial_value, variable: str = "x"
    ) -> Optional[float]:
        """Does no more than max_iterations iterations. Otherwise, it returns None."""
        pass
