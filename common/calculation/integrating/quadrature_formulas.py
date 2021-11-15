from common.models.line_segment import LineSegment


class LeftRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.left)


class RightRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.right)


class MiddleRectangleQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * function(line_segment.center)


class TrapezeQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return line_segment.length * (function(line_segment.left) + function(line_segment.right)) / 2


class SimpsonQuadFormula:
    @staticmethod
    def calculate(function, line_segment: LineSegment):
        return (
            line_segment.length
            * (function(line_segment.left) + function(line_segment.right) + 4 * function(line_segment.center))
            / 6
        )


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
