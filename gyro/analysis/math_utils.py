import math
import numpy

def find_Q(v):
    def solve_2d(v0, v1): # v1 -> 0
        cos_phi, sin_phi = 0, 1
        if v0 != 0:
            tan_phi = v1 / v0
            cos_phi = math.sqrt(1. / (1. + tan_phi * tan_phi))
            sin_phi = tan_phi * cos_phi
        return cos_phi, sin_phi

    cos_phi, sin_phi = solve_2d(v[0], - v[1])
    v0_prime = v[0] * cos_phi - v[1] * sin_phi

    cos_ksi, sin_ksi = solve_2d(v[2], v0_prime)
    v2_prime = v0_prime * sin_ksi + v[2] * cos_ksi
    if v2_prime > 0:
        cos_ksi, sin_ksi = -cos_ksi, -sin_ksi

    Q1 = numpy.array([
        [cos_ksi, 0, -sin_ksi],
        [0, 1, 0],
        [sin_ksi, 0, cos_ksi]])
    Q2 = numpy.array([
        [cos_phi, -sin_phi, 0],
        [sin_phi, cos_phi, 0],
        [0, 0, 1]])
    return Q1.dot(Q2)


