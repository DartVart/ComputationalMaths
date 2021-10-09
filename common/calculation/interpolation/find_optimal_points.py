from typing import List, Union, Sequence


def find_optimal_points(x: float, points: List[Union[float, Sequence[float]]], number_of_points: int, key=lambda x: x):
    if len(points) < number_of_points:
        raise ValueError("Too few points.")
    distances = [(i, abs(x - key(point))) for i, point in enumerate(points)]
    sorted_distances = sorted(distances, key=lambda y: y[1])
    return [points[dist[0]] for dist in sorted_distances[:number_of_points]]
