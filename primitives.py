import math
from typing import Optional


from helper import distance
from model import Vec2Double, Tile


class LevelPoint(object):
    def __init__(self, tile: Tile, position: Vec2Double):
        self.tile = tile
        self.position = position
        self.lines = TileLines(self.position)

    def stred_position(self):
        return str(int(self.position.x)) + str(int(self.position.y))

    def __repr__(self):
        return '(x={};y={}):{}'.format(int(self.position.x), int(self.position.y), self.tile)

    def get_tuple(self):
        return self.position.get_tuple()


class Line(object):
    """Line primitive with canonical equation of a line"""

    def __init__(self, v1: Vec2Double, v2: Vec2Double):
        """Build line by two dots"""
        self.v1 = v1
        self.v2 = v2
        self.A = 0
        self.B = 0
        self.C = 0
        self.__calculate_line()

    def __repr__(self):
        return '({};{}),({};{})'.format(
            round(self.v1.x, 3),
            round(self.v1.y, 3),
            round(self.v2.x, 3),
            round(self.v2.y, 3)
        )

    def __calculate_line(self):
        """Calculate line params"""
        self.A = self.v1.y - self.v2.y
        self.B = self.v2.x - self.v1.x
        self.C = self.v1.x * self.v2.y - self.v2.x * self.v1.y

    def common_point_with(self, other: 'Line') -> Optional[Vec2Double]:
        """Calculate common with :other line
            Kramer method is used
        """
        d = self.A * other.B - other.A * self.B
        if d == 0.:
            return None
        _c1 = (- self.C)
        _c2 = (- other.C)
        dx = _c1 * other.B - _c2 * self.B
        dy = self.A * _c2 - other.A * _c1
        return Vec2Double(dx / d, dy / d)

    def is_inside(self, point: Vec2Double) -> bool:
        return math.fabs(distance(self.v1, self.v2) - (distance(point, self.v1) + distance(point, self.v2))) < 0.01


class TileLines(object):
    def __init__(self, position: Vec2Double):
        self.position = position
        self.left = Line(position, Vec2Double(position.x, position.y + 1))
        self.bottom = Line(position, Vec2Double(position.x + 1, position.y))
        self.top = Line(Vec2Double(position.x, position.y + 1), Vec2Double(position.x + 1, position.y + 1))
        self.right = Line(Vec2Double(position.x, position.y + 1), Vec2Double(position.x + 1, position.y + 1))
