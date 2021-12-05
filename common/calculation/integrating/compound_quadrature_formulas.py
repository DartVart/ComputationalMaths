from common.calculation.integrating.quadrature_formulas import LeftRectangleQuadFormula, RightRectangleQuadFormula, \
    MiddleRectangleQuadFormula, TrapezeQuadFormula, SimpsonQuadFormula, ThreeFractionsOfEightQuadFormula
from common.models.line_segment import LineSegment
from common.models.point_generation import EquidistantPointGenerator

point_generator = EquidistantPointGenerator()


def get_sum_in_middle_nodes(function, line_segment: LineSegment, partition_count: int):  # W
    h = line_segment.length / partition_count
    current_node = line_segment.left
    result = 0
    for _ in range(1, partition_count):
        current_node += h
        result += function(current_node)
    return result


def get_sum_in_middle_of_segments(function, line_segment: LineSegment, partition_count: int):  # q
    h = line_segment.length / partition_count
    current_node = line_segment.left + h / 2
    result = 0
    for _ in range(partition_count):
        result += function(current_node)
        current_node += h
    return result


def get_sum_at_extremes(function, line_segment: LineSegment):  # z
    return function(line_segment.left) + function(line_segment.right)


def get_all_errors(single_quad_formula, derivative_modulo_max, line_segment, partition_count):
    points = point_generator.generate(line_segment, partition_count + 1)
    error = 0
    for i in range(len(points) - 1):
        error += single_quad_formula.get_theoretical_error(derivative_modulo_max,
                                                           LineSegment(points[i], points[i + 1]))
    return error


class LeftRectanglesFormula:
    algebraic_precision = 0

    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_nodes: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        return h * (function(line_segment.left) + sum_in_middle_nodes)

    @staticmethod
    def get_theoretical_error(first_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return first_derivative_modulo_max * line_segment.length * (h ** 1) / 2


class RightRectanglesFormula:
    algebraic_precision = 0

    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_nodes: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        return h * (function(line_segment.right) + sum_in_middle_nodes)

    @staticmethod
    def get_theoretical_error(first_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return first_derivative_modulo_max * line_segment.length * (h ** 1) / 2


class MiddleRectanglesFormula:
    algebraic_precision = 1

    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_of_segments: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_of_segments is None:
            sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
        return h * sum_in_middle_of_segments

    @staticmethod
    def get_theoretical_error(second_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return second_derivative_modulo_max * line_segment.length * (h ** 2) / 24


class TrapezesFormula:
    algebraic_precision = 1

    @staticmethod
    def calculate(
            function,
            line_segment: LineSegment,
            partition_count,
            sum_at_extremes: float = None,
            sum_in_middle_nodes: float = None,
    ):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        if sum_at_extremes is None:
            sum_at_extremes = get_sum_at_extremes(function, line_segment)
        return h * (sum_at_extremes + 2 * sum_in_middle_nodes) / 2

    @staticmethod
    def get_theoretical_error(second_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return second_derivative_modulo_max * line_segment.length * (h ** 2) / 12


class SimpsonFormula:
    algebraic_precision = 3

    @staticmethod
    def calculate(
            function,
            line_segment: LineSegment,
            partition_count,
            sum_at_extremes: float = None,
            sum_in_middle_nodes: float = None,
            sum_in_middle_of_segments: float = None,
    ):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        if sum_at_extremes is None:
            sum_at_extremes = get_sum_at_extremes(function, line_segment)
        if sum_in_middle_of_segments is None:
            sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
        return h * (sum_at_extremes + 2 * sum_in_middle_nodes + 4 * sum_in_middle_of_segments) / 6

    @staticmethod
    def get_theoretical_error(fourth_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return fourth_derivative_modulo_max * line_segment.length * (h ** 4) / 2880


class ThreeFractionsOfEightFormula:
    algebraic_precision = 3

    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count):
        h = line_segment.length / partition_count
        one_third_of_h = h / 3
        two_third_of_h = 2 * h / 3
        first_sum = 0
        second_sum = 0
        current_node = line_segment.left
        for i in range(partition_count - 1):
            first_sum += (function(current_node + one_third_of_h) + function(current_node + two_third_of_h))
            current_node += h
            second_sum += function(current_node)
        first_sum += (function(current_node + one_third_of_h) + function(current_node + two_third_of_h))
        return h * (function(line_segment.left) + function(line_segment.right) + 3 * first_sum + 2 * second_sum) / 8

    @staticmethod
    def get_theoretical_error(fourth_derivative_modulo_max, line_segment, partition_count):
        h = line_segment.length / partition_count
        return fourth_derivative_modulo_max * line_segment.length * (h ** 4) / 6480
