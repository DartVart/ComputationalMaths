from typing import Sequence, Tuple

from common.calculation.interpolation.interpolators.interpolator import Interpolator


class NewtonInterpolator(Interpolator):
    name = "Форма Ньютона"

    def get_approximate_value(self, x: float, value_table: Tuple[Sequence[float], Sequence[float]]):
        parted_differences = self._get_parted_differences(value_table)
        approximate_value = 0
        differences_prod = 1.0
        print("Добавления")
        for i in range(len(value_table[0])):
            approximate_value += parted_differences[i] * differences_prod
            print(f"{parted_differences[i] * differences_prod}, {parted_differences[i]}")
            differences_prod *= x - value_table[0][i]
        print("Конец добавления")
        return approximate_value

    @staticmethod
    def _get_parted_differences(value_table):
        parted_differences = [value_table[1][0]]
        prev_differences_level = value_table[1]
        number_of_values = len(value_table[0])
        for i in range(1, number_of_values):
            cur_differences_level = []
            for j in range(number_of_values - i):
                new_value = (prev_differences_level[j + 1] - prev_differences_level[j]) / (
                    value_table[0][i + j] - value_table[0][j]
                )
                cur_differences_level.append(new_value)
            parted_differences.append(cur_differences_level[0])
            print(cur_differences_level)

            prev_differences_level = cur_differences_level
        print()
        print()
        return parted_differences
