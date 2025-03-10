'''
Created on 17 Jun 2019

@author: Bren
'''

'''Continuing from matrix_stuff1...

Created on 15 Jun 2019

@author: Bren
'''
import math
import random
import fbx

import numpy
# from scipy.spatial.transform import Rotation as scipy_rotation

try:
    from maya import cmds
    MAYA_ENVIRONMENT = True
except ImportError:
    MAYA_ENVIRONMENT = False

ROTATE_SEED = 16.6
ROTATE_SEED = None


def eq_tol(value, other_value, tolerance):
    """Test if a value is equal to another within tolerance
    """
    return other_value - tolerance > value < other_value + tolerance

def get_sine_cosine_angle(sin_value, cos_value, degrees=True, tolerance=1.0e-12):
    """Determine angle from sine and cosine values.

    This method helps to determine if
    the angle is positive or negative
    and if the angle is greater than 90 degrees
    or less than negative 90 degrees

    Tolerance allows for floating point error, when comparing sin or cos values to 0, 1 or -1.

    """
    try:
        # if cos_value == 1:
        if eq_tol(cos_value, 1, tolerance):
            radians = 0.0
        # elif cos_value == 0:
        elif eq_tol(cos_value, 0, tolerance):
            radians = math.radians(180)
        # elif sin_value == 1:
        elif eq_tol(sin_value, 1, tolerance):
            radians = math.radians(90)
        # elif sin_value == -1:
        elif eq_tol(sin_value, -1, tolerance):
            radians = math.radians(-90)
        elif cos_value > 0 and sin_value > 0:
            # positive rotation below 90 degrees
            radians = math.acos(cos_value)
        elif cos_value < 0 and sin_value > 0:
            # positive rotation above 90 degrees
            radians = math.radians(180) - math.asin(sin_value)
        elif cos_value > 0 and sin_value < 0:
            # negative rotation above -90 degrees
            radians = -math.acos(cos_value)
        elif cos_value < 0 and sin_value < 0:
            # negative rotation below -90 degrees
            radians = math.radians(-180) - math.asin(sin_value)
        elif cos_value > 1 or cos_value < -1 or sin_value > 1 or sin_value < -1:
            raise Exception("-1 > cos/sin > 1 out of  bounds")
            # TOOD if neccesary
    except ValueError as err:
        print "Failed to calculate value, sin_value: {}, cos_value: {}".format(sin_value, cos_value)
        raise err

    if degrees:
        return math.degrees(radians)
    else:
        return radians


# represent each axis rotation as a list of functions
# this will allow us to "multiply" sequences of functions
# that allow us to procedurally solve euler rotation
# independent of rotation order
# and ideally independant of world axes (TODO)

class SignPositive():
    @classmethod
    def __eq__(cls, other):
        return other > 0

    @classmethod
    def __ne__(cls, other):
        return other < 0

    @classmethod
    def flip(cls):
        return SignNegative


class SignNegative():
    @classmethod
    def __eq__(self, other):
        return other < 0

    @classmethod
    def __ne__(self, other):
        return other > 0

    @classmethod
    def flip(cls):
        return SignPositive


class Sign():
    positive = SignPositive
    negative = SignNegative

    @classmethod
    def evaluate(cls, value, sign):
        if sign is cls.positive:
            return value
        elif sign is cls.negative:
            return value * -1
        else:
            raise Exception("Sign not recognized: {}".format(sign))

# wip...


class Axis(object):
    pass


class XAxis(Axis):
    @staticmethod
    def __repr__():
        return "x"


class YAxis(Axis):
    @staticmethod
    def __repr__():
        return "y"


class ZAxis(Axis):
    @classmethod
    def __name__(cls):
        return "z"


class Axes():
    null = None
    x = XAxis
    y = YAxis
    z = ZAxis

    axes = [XAxis, YAxis, ZAxis]

    @classmethod
    def get(cls, vector, axis):
        return vector[
            cls.axes.index(axis)
        ]


class MatrixOperationSum(object):
    def __init__(self, operations=[]):
        self._operations = operations

    def __repr__(self):
        return "[{}]".format(
            " + ".join(
                [str(i) for i in self._operations]
            ))

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def evaluate(self, xyz_values):
        value = 0.0

        for operation in self._operations:
            value += operation.evaluate(xyz_values)

        return value


class MatrixOperationProduct(object):
    """Product of multiple trigonometric function as a component of a matrix.
    """

    def __init__(self, operations=[]):
        self._operations = operations

    def operations(self):
        return self._operations

    def __mul__(self, other):
        if other == 1:
            return self

        if isinstance(other, MatrixOperationProduct):
            return list(self._operations) + list(other._operations)

        if isinstance(other, MatrixOperation):
            result = list(self._operations)
            result.append(other)

            return MatrixOperationProduct(operations=result)

        return 0

    def __repr__(self, *args, **kwargs):
        return "{{{}}}".format(
            " * ".join(
                [str(i) for i in self._operations]
            ))

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def evaluate(self, xyz_values):
        value = 1.0

        for operation in self._operations:
            value *= operation.evaluate(xyz_values)

        return value

    def evaluate_axis(self, axis, input_value):
        """For each operation matching axis, solve using value.
        """
        evaluated_values = []
        remaining_operations = []

        for operation in self.operations():
            if operation.axis == axis:
                evaluated_values.append(
                    operation.evaluate(input_value)
                )
            else:
                remaining_operations.append(operation)

        if not len(evaluated_values):
            raise Exception("Failed to evaluate axis: {}".format(axis))

        return numpy.product(evaluated_values), remaining_operations

    def can_solve_using_axis(self, axis):
        """Determine if we can solve operations by substituting specified axis.

        returns:
            (Axis) object of solvable axis, or
            (False) if not solvable

        """
        remaining_axes = set([])

        for operation in self.operations():
            if operation.axis != axis:
                remaining_axes.add(operation.axis)

        if len(remaining_axes) == 1:
            return list(remaining_axes)[0]
        else:
            return False


class MatrixOperation(object):
    """Object to represent a trigonometric function as a component of a matrix.
    """

    def __init__(self, axis, sign, trig_function, inverse_function):
        self.axis = axis
        self.sign = sign
        self.trig_function = trig_function
        self.inverse_function = inverse_function

    def __repr__(self, *args, **kwargs):
        trig_strs = {
            math.sin: "sin",
            math.cos: "cos",
        }

        axis_strs = {
            XAxis: "x",
            YAxis: "y",
            ZAxis: "z"
        }

        repr_str = "{}({})".format(
            trig_strs[self.trig_function],
            axis_strs[self.axis],
        )

        if self.sign is SignNegative:
            repr_str = "-{}".format(repr_str)

        return repr_str

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def evaluate(self, value):
        if isinstance(value, list):
            value = Axes.get(value, self.axis)

        result = self.trig_function(value)

        if self.sign is SignNegative:
            result *= -1.0

        return result

    def inverse(self, value):
        result = self.inverse_function(value)

        if self.sign is SignNegative:
            result *= -1.0

        return result

    def __mul__(self, other):
        if other == 0:
            return 0

        if other == 1:
            return self

        if isinstance(other, MatrixOperation):
            return MatrixOperationProduct(
                operations=[self, other]
            )

        if isinstance(other, MatrixOperationProduct):
            return other * self

        return 0

    def __eq__(self, other):
        if not isinstance(other, MatrixOperation):
            return False

        return all([
            self.axis == other.axis,
            self.trig_function == other.trig_function,
            #             self.sign == other.sign # ignore this for now
        ])

    def copy(self):
        """Return copy of self
        """
        return MatrixOperation(
            self.axis,
            self.sign,
            self.trig_function,
            self.inverse_function
        )


class MatrixFunctions(object):
    def __init__(self):
        self._matrix = self.GetIdentity()

    def GetIdentity(self):
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    def SetRow(self, row_index, row_value):
        if not isinstance(row_value, (list, tuple)):
            raise Exception("Row value must be list or tuple")

        for i, value in enumerate(list(row_value)[:4]):
            if isinstance(value, tuple):
                value = MatrixOperation(*value)

            self._matrix[row_index][i] = value

    def __mul__(self, other):
        """matrix multiplication

        create lists of function tuples per rows and columns

        """

        result = MatrixFunctions()

        for row_index, row in enumerate(self._matrix):
            result_row = []

            for column_index in range(4):
                other_column = [
                    other_row[column_index]
                    for other_row in other._matrix
                ]

                result_row_column = []

                for value, other_value in zip(row, other_column):

                    if value == 0 or other_value == 0:
                        continue

                    elif value == 1:
                        result_row_column.append(other_value)

                    else:
                        # multiplication is supported by
                        # MatrixOperation and MatrixOperationProduct classes
                        result_row_column.append(
                            value * other_value
                        )

                if len(result_row_column):
                    if len(result_row_column) == 1:
                        result_row.append(result_row_column[0])
                    else:
                        result_row.append(
                            MatrixOperationSum(operations=result_row_column)
                        )
                else:
                    result_row.append(0)

            result.SetRow(row_index, result_row)

        return result

    def compose(self, xyz_values, degrees=True):
        composed_matrix = []

        if degrees:
            xyz_values = [math.radians(i) for i in xyz_values]

        for row in self._matrix:
            composed_row = []

            for obj in row:
                if isinstance(obj, (float, int)):
                    composed_row.append(obj)

                elif isinstance(
                    obj,
                    (
                        MatrixOperation,
                        MatrixOperationProduct,
                        MatrixOperationSum
                    )
                ):
                    composed_row.append(
                        obj.evaluate(xyz_values)
                    )

            composed_matrix.append(
                composed_row
            )

        return composed_matrix

    def decompose(self, matrix_values, degrees=True, verbose=False):
        """attempt to solve xyz euler values from matrix
        """

        # conform matrix shape
        input_matrix = numpy.array(matrix_values).reshape([4, 4])

        # step 1:
        # look for any indices in matrix that are a single operation
        # and solve whatever axis that is
        single_operations = []

        xyz_values = {
            XAxis: None,
            YAxis: None,
            ZAxis: None
        }

        solved_axes = []
        remaining_axes = list(Axes.axes)

        for row_index, row in enumerate(self._matrix):
            for column_index, obj in enumerate(row):
                if isinstance(obj, MatrixOperation):
                    single_operations.append(
                        (row_index, column_index, obj)
                    )

        if len(single_operations) == 1:
            row_index, column_index, operation = single_operations[0]
            # guess direction and +-90
            matrix_value = input_matrix[row_index][column_index]

            euler_value = operation.inverse(matrix_value)

            xyz_values[operation.axis] = euler_value

            solved_axis = operation.axis
            solved_axes.append(operation.axis)
            remaining_axes.remove(operation.axis)

            if verbose:
                print "single operation: {} {} {} {}".format(
                    operation,
                    operation.axis,
                    matrix_value,
                    euler_value
                )

        elif len(single_operations):
            raise NotImplementedError(
                "TODO"
            )
        else:
            raise Exception(
                "Failed to solve Matrix function (no single operations)"
            )

        # step 2:
        sin_values = {}
        cos_values = {}

        # determine which products can be solved
        # and solve...
        for row_index, row in enumerate(self._matrix):
            for column_index, obj in enumerate(row):
                if isinstance(obj, MatrixOperationProduct):
                    if obj.can_solve_using_axis(solved_axis):

                        evaluated_value, remaining_operations = obj.evaluate_axis(
                            solved_axis,
                            xyz_values[solved_axis]
                        )

                        if len(remaining_operations) > 1:
                            # TODO
                            # solve more than one remaining operation
                            continue

                        r_opp = remaining_operations[0]

                        matrix_value = input_matrix[row_index][column_index]

                        trig_value = matrix_value / evaluated_value

                        if r_opp.sign == SignNegative:
                            trig_value *= -1

                        if r_opp.trig_function == math.sin:
                            # TODO append values
                            # and compare to verify results
                            sin_values[r_opp.axis] = trig_value
                        elif r_opp.trig_function == math.cos:
                            cos_values[r_opp.axis] = trig_value
                        else:
                            raise Exception("Something?")

        for axis in list(remaining_axes):
            if axis not in sin_values and axis not in cos_values:
                continue

            axis_value = get_sine_cosine_angle(
                sin_values[axis], cos_values[axis], degrees=False
            )

            xyz_values[axis] = axis_value

            solved_axes.append(axis)
            remaining_axes.remove(axis)

        # if we haven't solved both remaining axes
        # throw an error
        # TODO would this ever be the case?
        if len(solved_axes) != 3:
            raise Exception(
                "Failed to solve Matrix function (no sin/cos operations for stuff)"
            )

        # compose xyz list
        rotate = [xyz_values[i] for i in Axes.axes]
        rotate = [i if i else 0 for i in rotate]

        if degrees:
            rotate = [math.degrees(i) for i in rotate]

        return rotate


class XMatrixFunctions(MatrixFunctions):
    """

    1    0       0     0
    0  cos(n)  sin(n)  0
    0 -sin(n)  cos(n)  0
    0    0       0     1

    """

    def __init__(self):
        super(XMatrixFunctions, self).__init__()

        self.SetRow(1, [
            0,
            (Axes.x, Sign.positive, math.cos, math.acos),
            (Axes.x, Sign.positive, math.sin, math.asin),
            0
        ])

        self.SetRow(2, [
            0,
            (Axes.x, Sign.negative, math.sin, math.asin),
            (Axes.x, Sign.positive, math.cos, math.acos),
            0
        ])


class YMatrixFunctions(MatrixFunctions):
    """

    cos(n)  0 -sin(n)  0
    0       1    0     0 
    sin(n)  0  cos(n)  0
    0       0    0     1

    """

    def __init__(self):
        super(YMatrixFunctions, self).__init__()

        self.SetRow(0, [
            (Axes.y, Sign.positive, math.cos, math.acos),
            0,
            (Axes.y, Sign.negative, math.sin, math.asin),
            0
        ])

        self.SetRow(2, [
            (Axes.y, Sign.positive, math.sin, math.asin),
            0,
            (Axes.y, Sign.positive, math.cos, math.acos),
            0
        ])


class ZMatrixFunctions(MatrixFunctions):
    """

     cos(n)  sin(n)  0   0
    -sin(n)  cos(n)  0   0
       0       0     1   0
       0       0     0   1

    """

    def __init__(self):
        super(ZMatrixFunctions, self).__init__()

        self.SetRow(0, [
            (Axes.z, Sign.positive, math.cos, math.acos),
            (Axes.z, Sign.positive, math.sin, math.asin),
            0,
            0
        ])

        self.SetRow(1, [
            (Axes.z, Sign.negative, math.sin, math.asin),
            (Axes.z, Sign.positive, math.cos, math.acos),
            0,
            0
        ])


class EulerMatrixFunctions():
    X = XMatrixFunctions()
    Y = YMatrixFunctions()
    Z = ZMatrixFunctions()

    @staticmethod
    def names():
        return [
            'xyz',
            'yzx',
            'zxy',
            'xzy',
            'yxz',
            'zyx'
        ]

    @classmethod
    def xyz(cls):
        return cls.X * cls.Y * cls.Z

    @classmethod
    def yzx(cls):
        return cls.Y * cls.Z * cls.X

    @classmethod
    def zxy(cls):
        return cls.Z * cls.X * cls.Y

    @classmethod
    def xzy(cls):
        return cls.X * cls.Z * cls.Y

    @classmethod
    def yxz(cls):
        return cls.Y * cls.X * cls.Z

    @classmethod
    def zyx(cls):
        return cls.Z * cls.Y * cls.X
