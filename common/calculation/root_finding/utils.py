from dataclasses import dataclass, field
from typing import List

from sympy import lambdify
from sympy.core.assumptions import ManagedProperties


@dataclass
class Statistic:
    values: List[float] = field(default_factory=list)


def get_lambda_func(function, variable="x"):
    return lambdify(variable, function) if isinstance(type(function), ManagedProperties) else function
