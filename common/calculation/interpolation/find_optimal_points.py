from typing import List


def find_optimal_points(x: float, points: List[float], number_of_points: int):
    if len(points) < number_of_points:
        raise ValueError("Too few points.")
    distances = [(i, abs(x - point)) for i, point in enumerate(points)]
    sorted_distances = sorted(distances, key=lambda y: y[1])
    return sorted([points[dist[0]] for dist in sorted_distances[:number_of_points]])
