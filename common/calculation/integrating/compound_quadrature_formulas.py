from common.models.line_segment import LineSegment


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


class LeftRectanglesFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_nodes: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        return h * (function(line_segment.left) + sum_in_middle_nodes)


class RightRectanglesFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_nodes: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        return h * (function(line_segment.right) + sum_in_middle_nodes)


class MiddleRectanglesFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_in_middle_of_segments: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_of_segments is None:
            sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
        return h * sum_in_middle_of_segments


class TrapezesFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_at_extremes: float = None,
                  sum_in_middle_nodes: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        if sum_at_extremes is None:
            sum_at_extremes = get_sum_at_extremes(function, line_segment)
        return h * (sum_at_extremes + 2 * sum_in_middle_nodes) / 2


class SimpsonFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment, partition_count, sum_at_extremes: float = None,
                  sum_in_middle_nodes: float = None, sum_in_middle_of_segments: float = None):
        h = line_segment.length / partition_count
        if sum_in_middle_nodes is None:
            sum_in_middle_nodes = get_sum_in_middle_nodes(function, line_segment, partition_count)
        if sum_at_extremes is None:
            sum_at_extremes = get_sum_at_extremes(function, line_segment)
        if sum_in_middle_of_segments is None:
            sum_in_middle_of_segments = get_sum_in_middle_of_segments(function, line_segment, partition_count)
        return h * (sum_at_extremes + 2 * sum_in_middle_nodes + 4 * sum_in_middle_of_segments) / 6
