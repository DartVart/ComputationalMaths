from abc import ABC, abstractmethod
from typing import Tuple, List


class Interpolator(ABC):
    @abstractmethod
    def get_approximate_value(self, x: float, value_table: Tuple[List[float], List[float]]):
        pass
