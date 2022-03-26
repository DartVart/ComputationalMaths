from cmath import sqrt
from typing import Callable

from numpy import linalg as LA
import numpy as np


def get_generalized_vandermonde_matrix(a_k: Callable[[float], float], b_k: Callable[[float], float], matrix_size: int):
    list_matrix = [[a_k(k_for_a) ** b_k(k_for_b) for k_for_b in range(1, matrix_size + 1)] for k_for_a in
                   range(1, matrix_size + 1)]
    return np.array(list_matrix)


def matrix_sqrt(input_matrix):
    """Only oscillation matrices are accepted."""

    eig_values, V = LA.linalg.eig(input_matrix)
    big_lambda = np.diag(eig_values)
    big_lambda_sqrt = np.sqrt(big_lambda)
    return V @ big_lambda_sqrt @ LA.linalg.inv(V)


def matrix_norm(input_matrix):
    """
    A subordinate matrix norm for the Euclidean norm of vectors is used.
    The matrix consists of real numbers.
    """

    eig_values, _ = LA.linalg.eig(np.transpose(input_matrix) @ input_matrix)
    return sqrt(max(eig_values))


def cond(input_matrix):
    """
    It returns condition number.
    A subordinate matrix norm for the Euclidean norm of vectors is used.
    """

    inverse_matrix = np.linalg.inv(input_matrix)
    return matrix_norm(input_matrix) * matrix_norm(inverse_matrix)


if __name__ == '__main__':
    for size in range(9, 10):
        A = get_generalized_vandermonde_matrix(lambda k: k, lambda k: k / 3, size)
        B = matrix_sqrt(A)
        print(f"n = {size}: cond(A) = {cond(A)};  cond(B) = {cond(B)};  ||A - B^2|| = {matrix_norm(A - B @ B)}")
        u = A @ np.array([1] * size)
        print("First")
        for a in [10 ** (-i) for i in range(15)]:
            transpose_A = np.transpose(A)
            matrix = transpose_A @ A + a * np.eye(size)
            vector = transpose_A @ u
            print(f"a = {a}: {LA.solve(matrix, vector)}")

        print("Second")
        for a in [10 ** (-i) for i in range(15)]:
            transpose_B = np.transpose(B)
            matrix = transpose_B @ B + a * np.eye(size)
            vector = transpose_B @ np.linalg.inv(B) @ u
            print(f"a = {a}: {LA.solve(matrix, vector)}")
