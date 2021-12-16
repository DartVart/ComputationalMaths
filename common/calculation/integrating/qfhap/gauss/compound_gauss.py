from typing import Dict, Optional, List

from common.calculation.integrating.qfhap.gauss.gauss import GaussQF
from common.calculation.root_finding.utils import get_lambda_func
from common.models.line_segment import LineSegment
from common.models.point_generation import EquidistantPointGenerator
from tasks.utils.expression_parsing import custom_parse_expr


class CompoundGaussQF:
    def __init__(self, accuracy=1e-12):
        self.gauss_qf = GaussQF(accuracy)
        self.point_generator = EquidistantPointGenerator()
        self.stat: Dict[str, Optional[List[float]]] = {"standard_nodes": None, "standard_coefficients": None}

    def get_function_values(self, function, line_segment: LineSegment, nodes_count: int, partition_count: int):
        standard_segment_nodes = self.gauss_qf.get_nodes_in_standard_line_segment(nodes_count)
        self.stat["standard_nodes"] = standard_segment_nodes
        lambda_function = get_lambda_func(function)
        h = line_segment.length / partition_count
        z = self.point_generator.generate(line_segment, partition_count + 1)[:-1]
        nodes = [[(h * (standard_node + 1) / 2 + z_i) for standard_node in standard_segment_nodes] for z_i in z]
        return [[lambda_function(node) for node in node_list] for node_list in nodes]

    def integrate(self, function_values, line_segment, nodes_count, partition_count):
        coefficients = self.gauss_qf.get_standard_coefficients(nodes_count)
        self.stat["standard_coefficients"] = coefficients
        h = line_segment.length / partition_count
        return (
            sum(
                sum(coefficients[i] * function_value for i, function_value in enumerate(one_segment_values))
                for one_segment_values in function_values
            )
            * h
            / 2
        )


# if __name__ == '__main__':
#     g = CompoundGaussQF()
#     f = custom_parse_expr("sin(x) * sqrt(x)")
#     l = LineSegment(0, 1)
#     m = 10
#     f_vals = g.get_function_values(f, l, 5, m)
#     print(g.integrate(f_vals, l, 5, m))
#     print(g.stat['standard_nodes'])
#     print(g.stat['standard_coefficients'])
