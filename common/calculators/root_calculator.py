from dataclasses import replace, dataclass, field
from typing import List

from a.common.calculators.root_separator import RootSeparator
from a.common import Statistic


@dataclass
class RootCalculatorStatistic:
    segments: List[float] = field(default_factory=list)
    single_solver_statistics: List[Statistic] = field(default_factory=list)


class RootCalculator:
    def __init__(self, single_root_solver):
        self.single_root_solver = single_root_solver
        self.root_separator = RootSeparator()
        self.stat = RootCalculatorStatistic()

    def find_roots(self, function, line_segment, accuracy, number_of_steps, variable: str = "x"):
        self.stat.segments = self.root_separator.separate(function, line_segment, number_of_steps, variable)
        roots = []

        for segment in self.stat.segments:
            root = self.single_root_solver.find_root(function, segment, accuracy, variable)
            self.stat.single_solver_statistics.append(replace(self.single_root_solver.stat))
            roots.append(root)

        return roots
