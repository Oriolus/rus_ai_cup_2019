import math


def distance_sqr(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def distance(a, b):
    return math.sqrt(math.fabs(distance_sqr(a, b)))


def is_same_position(a, b):
    return distance(a, b) < 0.2


def get_sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0
