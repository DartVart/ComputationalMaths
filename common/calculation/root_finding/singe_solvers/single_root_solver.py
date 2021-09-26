from abc import ABC, abstractmethod

from common.calculation.root_finding.utils import Statistic
from common.models.line_segment import LineSegment


class SingleRootSolver(ABC):
    method_name: str

    def __init__(self):
        self.stat = Statistic()

    @abstractmethod
    def find_root(self, function, line_segment: LineSegment, accuracy, variable: str = "x") -> float:
        pass
