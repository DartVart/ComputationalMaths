from typing import List

from common.calculation.root_finding.root_calculator import RootCalculator
from common.calculation.root_finding.singe_solvers.as_newton_solvers.secant_solver import SecantLineSolver
from common.calculation.root_finding.utils import get_lambda_func
from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr


class GaussQF:
    standard_line_segment = LineSegment(-1, 1)

    def __init__(self, accuracy=1e-12):
        self._standard_lejandr_polynomials = [1, custom_parse_expr("x")]  # None for nodes_count = 0 and = 1
        self._standard_nodes = self.get_initial_standard_nodes()
        self._standard_coefficients = self.get_initial_standard_coefficients()
        self._solver = RootCalculator(SecantLineSolver())
        self._accuracy = accuracy

    def print_all(self):
        for i, pol in enumerate(self._standard_lejandr_polynomials):
            print(f"{i}: {pol if pol == 1 else pol.as_poly()}")

    @staticmethod
    def get_initial_standard_nodes():
        return {
            0: None,
            1: [0],
        }

    @staticmethod
    def get_initial_standard_coefficients():
        return {}

    def set_accuracy(self, new_accuracy):
        self._standard_nodes = self.get_initial_standard_nodes()
        self._standard_coefficients = self.get_initial_standard_coefficients()
        self._accuracy = new_accuracy

    def get_nodes_in_standard_line_segment(self, nodes_count: int) -> List[float]:
        if nodes_count not in self._standard_nodes:
            nodes = self._solver.find_roots(self.get_standard_lejandr_polynomial(nodes_count),
                                            self.standard_line_segment,
                                            self._accuracy, int(self.standard_line_segment.length // 0.001))
            self._standard_nodes[nodes_count] = nodes
        return self._standard_nodes[nodes_count]

    def _expand_standard_lejandr_polynomials(self, nodes_count: int):
        last_calculated_nodes_count = len(self._standard_lejandr_polynomials) - 1
        for i in range(last_calculated_nodes_count + 1, nodes_count + 1):
            new_polynomial = (float(2 * i - 1) / i) * self._standard_lejandr_polynomials[-1] * custom_parse_expr(
                "x") - (
                                     float(i - 1) / i) * self._standard_lejandr_polynomials[-2]
            self._standard_lejandr_polynomials.append(new_polynomial)

    def get_standard_lejandr_polynomial(self, nodes_count: int):
        if len(self._standard_lejandr_polynomials) <= nodes_count:
            self._expand_standard_lejandr_polynomials(nodes_count)
        return self._standard_lejandr_polynomials[nodes_count]

    def get_standard_coefficients(self, nodes_count):
        if nodes_count not in self._standard_coefficients:
            coefficients = [0] * nodes_count
            nodes = self.get_nodes_in_standard_line_segment(nodes_count)
            polynomial = get_lambda_func(self.get_standard_lejandr_polynomial(nodes_count - 1))
            for i in range(nodes_count // 2 + nodes_count % 2):
                current_coef = (2 * (1 - (nodes[i]) ** 2)) / ((nodes_count * polynomial(nodes[i])) ** 2)
                coefficients[i] = current_coef
                coefficients[nodes_count - 1 - i] = current_coef
            self._standard_coefficients[nodes_count] = coefficients
        return self._standard_coefficients[nodes_count]

    def get_nodes(self, line_segment: LineSegment, nodes_count) -> List[float]:
        ratio = line_segment.length / self.standard_line_segment.length
        return [(line_segment.left + ratio * (standard_node - self.standard_line_segment.left)) for standard_node in
                self.get_nodes_in_standard_line_segment(nodes_count)]

    def get_coefficients(self, line_segment: LineSegment, nodes_count):
        ratio = line_segment.length / self.standard_line_segment.length
        return [coeff * ratio for coeff in self.get_standard_coefficients(nodes_count)]

    def get_approx_integral(self, function_values: List[float], line_segment: LineSegment):
        """The values of the function must be calculated in the corresponding nodes of the Gaussian QF."""

        nodes_count = len(function_values)
        return sum(coef * value for coef, value in
                   zip(self.get_coefficients(line_segment, nodes_count), function_values))

    def get_function_values(self, function, line_segment: LineSegment, nodes_count):
        lambda_function = get_lambda_func(function)
        return [lambda_function(node) for node in self.get_nodes(line_segment, nodes_count)]
