from typing import List, Tuple

from common.calculation.interpolation.interpolators.interpolator import Interpolator


class LagrangianInterpolator(Interpolator):
    name = "Форма Лагранжа"

    def get_approximate_value(self, x: float, value_table: Tuple[List[float], List[float]]):
        differences_with_x = self._get_differences_with_nodes(x, value_table[0])
        approximate_value = 0
        for i in range(len(value_table[0])):
            approximate_value += (
                self._prod(differences_with_x, i)
                * value_table[1][i]
                / self._prod(self._get_differences_with_nodes(value_table[0][i], value_table[0], i))
            )
        return approximate_value

    @staticmethod
    def _prod(values, extra_key=None):
        product = 1.0
        for i, value in enumerate(values):
            if i != extra_key:
                product *= value
        return product

    @staticmethod
    def _get_differences_with_nodes(x, nodes: List[float], extra_node_index=None):
        differences = [x - node for node in nodes]
        if extra_node_index is not None:
            del differences[extra_node_index]
        return differences
