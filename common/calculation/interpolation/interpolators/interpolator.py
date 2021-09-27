from abc import ABC, abstractmethod
from typing import Tuple, List

from common.models.named import Named


class Interpolator(ABC, Named):
    @abstractmethod
    def get_approximate_value(self, x: float, value_table: Tuple[List[float], List[float]]):
        pass
