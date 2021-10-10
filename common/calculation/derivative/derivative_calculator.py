from abc import ABC, abstractmethod
from typing import List


class DerivativeCalculator(ABC):
    @abstractmethod
    def calculate(self, function_values, inter_node_length) -> List[float]:
        pass


class FirstDerivativeCalculator(DerivativeCalculator):
    @staticmethod
    def _calculate_central_derivative(left_value, right_value, inter_node_length):
        return (right_value - left_value) / (2 * inter_node_length)

    @staticmethod
    def _calculate_left_derivative(left_value, central_value, right_value, inter_node_length):
        return (-3 * left_value + 4 * central_value - right_value) / (2 * inter_node_length)

    @staticmethod
    def _calculate_right_derivative(left_value, central_value, right_value, inter_node_length):
        return (3 * left_value - 4 * central_value + right_value) / (2 * inter_node_length)

    def calculate(self, function_values, inter_node_length) -> List[float]:
        if function_values < 3:
            raise ValueError("Too few function values.")
        return [
            self._calculate_left_derivative(*function_values[:3], inter_node_length),
            *[self._calculate_central_derivative(function_values[i - 1], function_values[i + 1], inter_node_length) for
              i in range(1, len(function_values) - 1)],
            self._calculate_right_derivative(*function_values[-3:], inter_node_length),
        ]


class SecondDerivativeCalculator(DerivativeCalculator):
    @staticmethod
    def _calculate_central_derivative(left_value, central_value, right_value, inter_node_length):
        return (left_value - 2 * central_value + right_value) / (inter_node_length ** 2)

    def calculate(self, function_values, inter_node_length) -> List[float]:
        if function_values < 3:
            raise ValueError("Too few function values.")
        return [self._calculate_central_derivative(*function_values[i - 1:i + 2], inter_node_length)
                for i in range(1, len(function_values) - 1)]
