from abc import ABC, abstractmethod
import random
from typing import List

from common.models.float_with_accuracy import FloatWithAccuracy
from common.models.line_segment import LineSegment
from common.models.named import Named


class PointGenerator(ABC, Named):
    @abstractmethod
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        pass


class RandomPointGenerator(PointGenerator):
    name = 'Случайные'

    def __init__(self, seed=666):
        self.seed = seed

    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        random.seed(self.seed)
        points = set()
        while len(points) < number_of_points:
            new_value = FloatWithAccuracy(random.uniform(line_segment.left, line_segment.right))
            points.add(new_value)
        return [float(val) for val in points]


class EquidistantPointGenerator(PointGenerator):
    name = 'Равноотстающие'

    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[float]:
        return line_segment.split_into_points(number_of_points)
