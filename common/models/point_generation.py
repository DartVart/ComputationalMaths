from abc import ABC, abstractmethod
from typing import List

from common.models.line_segment import LineSegment


class PointGenerator(ABC):
    @abstractmethod
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[int]:
        pass


#
# class RandomPointGenerator(PointGenerator):
#
#
#
class EquidistantPointGenerator(PointGenerator):
    def generate(self, line_segment: LineSegment, number_of_points: int) -> List[int]:
        return line_segment.split_into_points(number_of_points)
