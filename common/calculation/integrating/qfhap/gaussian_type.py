from sympy import integrate
from numpy import linalg
from numpy.polynomial import Polynomial

from common.calculation.root_finding.utils import get_lambda_func
from common.models.line_segment import LineSegment
from tasks.utils.expression_parsing import custom_parse_expr


class GaussianTypeQF:
    @staticmethod
    def get_moments(weight_function, line_segment: LineSegment, nodes_count):
        return [
            float(
                integrate(weight_function * custom_parse_expr(f"x^{i}"), ("x", line_segment.left, line_segment.right))
            )
            for i in range(2 * nodes_count)
        ]

    @staticmethod
    def get_orthogonal_poly_coefficients(moments):
        """Since the polynomial is reduced, the high coefficient does not return"""

        nodes_count = int(len(moments) / 2)
        matrix = [moments[i : i + nodes_count] for i in range(nodes_count)]
        biases = [-moments[i] for i in range(nodes_count, 2 * nodes_count)]
        return linalg.solve(matrix, biases).tolist()

    @staticmethod
    def find_nodes(orthogonal_poly_coefficients):
        orthogonal_poly = Polynomial(orthogonal_poly_coefficients + [1.0])
        return orthogonal_poly.roots()

    @staticmethod
    def find_coefficients(nodes, moments):
        nodes_count = len(nodes)
        matrix = [[1] * nodes_count] + [[pow(node, i) for node in nodes] for i in range(1, nodes_count)]
        biases = moments[:nodes_count]
        return linalg.solve(matrix, biases).tolist()

    @staticmethod
    def get_function_values(function, nodes):
        lambda_function = get_lambda_func(function)
        return [lambda_function(node) for node in nodes]

    @staticmethod
    def integrate(function_values, coefficients):
        return sum(function_val * coefficients[i] for i, function_val in enumerate(function_values))
