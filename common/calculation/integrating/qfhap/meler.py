from math import cos, pi
from typing import List, Dict, Optional

from common.calculation.root_finding.utils import get_lambda_func
from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr


class MelerQF:
    """Works only with standard line segment"""

    standard_line_segment = LineSegment(-1, 1)
    weight_function = custom_parse_expr("1 / sqrt(1 - x ** 2)")

    def __init__(self):
        self._standard_nodes: Dict[int, Optional[List[float]]] = self.get_initial_standard_nodes()
        self._standard_coefficients = self.get_initial_standard_coefficients()

    @staticmethod
    def get_initial_standard_nodes():
        return {
            0: None,
            1: [0.0],
        }

    @staticmethod
    def get_initial_standard_coefficients():
        return {}

    def get_nodes(self, nodes_count: int) -> List[float]:
        common_ratio = pi / (2 * nodes_count)
        if nodes_count not in self._standard_nodes:
            self._standard_nodes[nodes_count] = [cos((2 * i - 1) * common_ratio) for i in range(1, nodes_count + 1)]
        return self._standard_nodes[nodes_count]

    @staticmethod
    def get_coefficient(nodes_count):
        return pi / nodes_count

    def get_approx_integral(self, function_values: List[float]):
        """The values of the function must be calculated in the corresponding nodes of the Gaussian QF."""

        return sum(function_values) * self.get_coefficient(len(function_values))

    def get_function_values(self, function, nodes_count):
        lambda_function = get_lambda_func(function)
        return [lambda_function(node) for node in self.get_nodes(nodes_count)]


if __name__ == '__main__':
    g = MelerQF()
    func = custom_parse_expr("cos(x)")
    print(g.get_coefficient(3))
    print(g.get_nodes(3))
    func_values = g.get_function_values(func, 3)
    print(g.get_approx_integral(func_values))
