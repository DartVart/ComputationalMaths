from dataclasses import dataclass, field
from typing import List


@dataclass
class Statistic:
    values: List[float] = field(default_factory=list)
