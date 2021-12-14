from common.models.line_segment import LineSegment


class LeftRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.left)

    @staticmethod
    def get_theoretical_error(first_derivative_modulo_max, line_segment):
        return (line_segment.length ** 2) * first_derivative_modulo_max / 2


class RightRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.right)

    @staticmethod
    def get_theoretical_error(first_derivative_modulo_max, line_segment):
        return (line_segment.length ** 2) * first_derivative_modulo_max / 2


class MiddleRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.center)

    @staticmethod
    def get_theoretical_error(second_derivative_modulo_max, line_segment):
        return (line_segment.length ** 3) * second_derivative_modulo_max / 24


class TrapezeQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * (function(line_segment.left) + function(line_segment.right)) / 2

    @staticmethod
    def get_theoretical_error(second_derivative_modulo_max, line_segment):
        return (line_segment.length ** 3) * second_derivative_modulo_max / 12


class SimpsonQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return (
            line_segment.length
            * (function(line_segment.left) + function(line_segment.right) + 4 * function(line_segment.center))
            / 6
        )

    @staticmethod
    def get_theoretical_error(fourth_derivative_modulo_max, line_segment):
        return (line_segment.length ** 5) * fourth_derivative_modulo_max / 2880


class ThreeFractionsOfEightQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        length = line_segment.length
        h = length / 3
        return length * (
            function(line_segment.left) / 8
            + function(line_segment.left + h) * 3 / 8
            + function(line_segment.left + 2 * h) * 3 / 8
            + function(line_segment.right) / 8
        )

    @staticmethod
    def get_theoretical_error(fourth_derivative_modulo_max, line_segment):
        return (line_segment.length ** 5) * fourth_derivative_modulo_max / 6480
