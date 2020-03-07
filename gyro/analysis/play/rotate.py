import numpy as np
import math

def solve_2(v):
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

    Q1 = np.array([
        [cos_ksi, 0, -sin_ksi],
        [0, 1, 0],
        [sin_ksi, 0, cos_ksi]])
    Q2 = np.array([
        [cos_phi, -sin_phi, 0],
        [sin_phi, cos_phi, 0],
        [0, 0, 1]])
    return Q1.dot(Q2)

def solve_3(v):
    phi = math.pi / 2
    if v[0] != 0:
        phi = math.atan(- v[1] / v[0])

    v0_prime = v[0] * math.cos(phi) - v[1] * math.sin(phi)

    ksi = math.pi / 2
    if v[2] != 0:
        ksi = math.atan(v0_prime / v[2])

    v2_prime = v0_prime * math.sin(ksi) + v[2] * math.cos(ksi)

    if v2_prime > 0:
        ksi = math.pi + ksi

    Q1 = np.array([
        [math.cos(ksi), 0, -math.sin(ksi)],
        [0, 1, 0],
        [math.sin(ksi), 0, math.cos(ksi)]])
    Q2 = np.array([
        [math.cos(phi), -math.sin(phi), 0],
        [math.sin(phi), math.cos(phi), 0],
        [0, 0, 1]])
    return Q1.dot(Q2)

def solve(v):
    return solve_2(v)

v = np.array([0, 0, 1])
print(v, solve(v).dot( v))
v = np.array([0, 1, 0])
print(v, solve(v).dot( v))
v = np.array([1, 0, 0])
print(v, solve(v).dot( v))
v = np.array([0.1, 0.2, 0.4])
print(v, solve(v).dot( v))
