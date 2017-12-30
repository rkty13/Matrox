from copy import deepcopy
from functools import wraps
from numbers import Number
from fractions import Fraction

class DimensionError(Exception):
    pass

def assert_square_matrix(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Matrix):
                if not is_square_matrix(arg):
                    raise DimensionError("Matrix must be a square matrix.")
        return func(*args, **kwargs)
    return func_wrapper

def size_constraint(*args, **kwargs):
    def decorator(func):
        def func_wrapper(*fargs, **fkwargs):
            constraints = {}
            for farg, arg in zip(fargs, args):
                if isinstance(farg, Matrix) and isinstance(arg, dict):
                    if 'rows' in arg.keys() or 'cols' in arg.keys():
                        if isinstance(arg['rows'], int):
                            if arg['rows'] != num_rows(farg):
                                raise DimensionError()
                        elif isinstance(arg['rows'], str):
                            if arg['rows'] in constraints.keys() and \
                                    constraints[arg['rows']] != num_rows(farg):
                                raise DimensionError()
                            else:
                                constraints[arg['rows']] = num_rows(farg)
                        if isinstance(arg['cols'], int):
                            if arg['cols'] != num_cols(farg):
                                raise DimensionError()
                        elif isinstance(arg['cols'], str):
                            if arg['cols'] in constraints.keys() and \
                                    constraints[arg['cols']] != num_cols(farg):
                                raise DimensionError()
                            else:
                                constraints[arg['cols']] = num_cols(farg)
                    else:
                        raise KeyError()
            return func(*fargs, **fkwargs)
        return func_wrapper
    return decorator

class Matrix(object):
    def __init__(self, data, fraction=False):
        self._matrix = []
        for i in range(len(data)):
            self._matrix.append([])
            for j in range(len(data[i])):
                if fraction:
                    self._matrix[i].append(Fraction(data[i][j]))
                else:
                    self._matrix[i].append(deepcopy(data[i][j]))

    def __getitem__(self, key):
        return self._matrix[key]

    def __setitem__(self, key, value):
        self._matrix[key] = value

    def __len__(self):
        return len(self._matrix)

    def __deepcopy__(self, memo):
        return type(self)(self._matrix)

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__,
            str([[str(j) for j in i] for i in self._matrix]))

    def __add__(self, other):
        return add_matrices(self, other)

    def __radd__(self, other):
        return add_matrices(self, other)

    def __sub__(self, other):
        return subtract_matrices(self, other)

    def __rsub__(self, other):
        return subtract_matrices(other, self)

    def __mul__(self, other):
        return multiply_matrices(self, other)

    def __rmul__(self, other):
        return multiply_matrices(other, self)

    def __pow__(self, x):
        return matrix_power(self, x)



def zero_matrix(rows, cols, fraction=False):
    return Matrix([[0 for j in range(cols)] for i in range(rows)],
        fraction=fraction)

def identity_matrix(rows, fraction=False):
    return Matrix([[int(i == j) for j in range(rows)] for i in range(rows)],
        fraction=fraction)

def fill_matrix(rows, cols, fill, fraction=False):
    return Matrix([[fill for j in range(cols)] for i in range(rows)],
        fraction=fraction)

def leading_term_index(vector):
    for i in range(len(vector)):
        if vector[i] != 0:
            return i
    return -1

def is_zero_vector(vector):
    return leading_term_index(vector) < 0

def is_square_matrix(matrix):
    return num_rows(matrix) == num_cols(matrix)

@assert_square_matrix
def is_symmetric(matrix):
    for i in range(num_rows(matrix)):
        for j in range(i, num_cols(matrix)):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True

@assert_square_matrix
def is_identity(matrix):
    for i in range(num_rows(matrix)):
        for j in range(num_cols(matrix)):
            if i == j and matrix[i][j] != 1:
                return False
            if i != j and matrix[i][j] != 0:
                return False
    return True

def num_rows(matrix):
    return len(matrix)

def num_cols(matrix):
    return len(matrix[0])

def dim(matrix):
    return num_rows(matrix), num_cols(matrix)

def diagonal(matrix):
    return Matrix([[matrix[i][i] for i in range(num_rows(matrix))]])

def num_non_zero_rows(matrix):
    num_non_zero = 0
    for row in matrix:
        if not is_zero_vector(row):
            num_non_zero += 1
    return num_non_zero

def augment(matrix_a, matrix_b):
    augmented = []
    for i in range(num_rows(matrix_a)):
        augmented.append(matrix_a[i] + matrix_b[i])
    return Matrix(augmented)

def scalar_mult_matrix(matrix, k):
    matrix_c = zero_matrix(num_rows(matrix), num_cols(matrix))
    for m in range(num_rows(matrix)):
        for n in range(num_cols(matrix)):
            matrix_c[m][n] = matrix[m][n] * k
    return matrix_c

def transpose(matrix):
    matrix_c = zero_matrix(num_cols(matrix), num_rows(matrix))
    for m in range(num_rows(matrix)):
        for n in range(num_cols(matrix)):
            matrix_c[n][m] = deepcopy(matrix[m][n])
    return matrix_c

@size_constraint({'rows': 'm', 'cols': 'n'}, {'rows': 'm', 'cols': 'n'})
def add_matrices(matrix_a, matrix_b):
    matrix_c = zero_matrix(num_rows(matrix_a), num_cols(matrix_a))
    for m in range(num_rows(matrix_c)):
        for n in range(num_cols(matrix_c)):
            matrix_c[m][n] = matrix_a[m][n] + matrix_b[m][n]
    return matrix_c

@size_constraint({'rows': 'm', 'cols': 'n'}, {'rows': 'm', 'cols': 'n'})
def subtract_matrices(matrix_a, matrix_b):
    negated = scalar_mult_matrix(matrix_b, -1)
    return add_matrices(matrix_a, negated)

@size_constraint({'rows': 'm', 'cols': 'r'}, {'rows': 'r', 'cols': 'n'})
def multiply_matrices(matrix_a, matrix_b):
    if isinstance(matrix_a, Number):
        return scalar_mult_matrix(matrix_b, matrix_a)
    if isinstance(matrix_b, Number):
        return scalar_mult_matrix(matrix_a, matrix_b)
    matrix_c = zero_matrix(num_rows(matrix_a), num_cols(matrix_b))
    for i in range(num_rows(matrix_a)):
        for j in range(num_cols(matrix_b)):
            el_sum = 0
            for k in range(num_cols(matrix_a)):
                el_sum += matrix_a[i][k] * matrix_b[k][j]
            matrix_c[i][j] = el_sum
    return matrix_c

@assert_square_matrix
def matrix_power(matrix, k):
    matrix_c = deepcopy(matrix)
    if k == 0:
        return identity_matrix(num_rows(matrix))
    for i in range(k - 1):
        matrix_c = matrix_c * matrix
    return matrix_c
