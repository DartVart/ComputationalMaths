from abc import ABC, abstractmethod
from random import uniform
from typing import List

from common.models.float_with_accuracy import FloatWithAccuracy
from common.models.line_segment import LineSegment


class PointGenerator(ABC):
    @abstractmethod
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        pass


class RandomPointGenerator(PointGenerator):
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        points = set()
        while len(points) < number_of_points:
            new_value = FloatWithAccuracy(uniform(line_segment.left, line_segment.right))
            points.add(new_value)
        return [float(val) for val in points]


class EquidistantPointGenerator(PointGenerator):
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        return line_segment.split_into_points(number_of_points)
