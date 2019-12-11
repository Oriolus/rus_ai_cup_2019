import model
import math
from typing import List

from collections import deque
import enum


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


class GTile(object):
    def __init__(self, tile: model.Tile, position: model.Vec2Double):
        self.tile = tile
        self.position = position

    def stred_position(self):
        return str(int(self.position.x)) + str(int(self.position.y))

    def __repr__(self):
        return '({}.{}):{}'.format(int(self.position.x), int(self.position.y), self.tile)


class Graph(object):
    def __init__(self, game: model.game, vertexes: list):
        def build_matrix(vertexes: List[GTile]):
            matrix = []
            for v in vertexes:
                path_to = []
                for v1 in vertexes:
                    if v.stred_position() != v1.stred_position():
                        if v.position.x == v1.position.x:
                            between_tiles = game.level.tiles[int(v.position.x)][v.position.y:v1.position.y]
                            if model.Tile.WALL in between_tiles or\
                                model.Tile.JUMP_PAD in between_tiles:
                                path_to.append(None)
                            else:
                                path_to.append(MovementType.MOVE_TO)
                        else:
                            path_to.append(None)
                    else:
                        path_to.append(None)
                matrix.append(path_to)
            return matrix

        self.game = game
        self.vertexes = vertexes
        self.matrix = build_matrix(self.vertexes)
        self.game = game


class MovementType(enum.Enum):
    KILL_ENEMY = 0
    MOVE_TO = 1
    JUMP_TO = 2


class MoveParam(object):
    def __init__(self, from_pos: model.Vec2Double, to_pos: model.Vec2Double, game_params: model.Properties):
        self.from_position = from_pos
        self.to_position = to_pos
        self.game_params = game_params

    def get_velocity(self, position: model.Vec2Double):
        return (self.to_position.x - position.x) * 100

    def is_in_destination(self, position: model.Vec2Double):
        return is_same_position(self.to_position, position)


class JumpParams(MoveParam):
    def __init__(self, from_pos: model.Vec2Double, to_pos: model.Vec2Double, game_params: model.Properties):
        def get_middle_position(from_pos: model.Vec2Double, to_pos: model.Vec2Double, game_params: model.Properties):
            dx = math.fabs(from_pos.x - to_pos.x)
            dy = math.fabs(from_pos.y - to_pos.y)

            v_x = game_params.unit_max_horizontal_speed
            v_up = game_params.unit_jump_speed
            v_down = game_params.unit_fall_speed

            time_1 = (dx + v_x * dy / v_down) * v_down /\
                     (v_x * (v_down + v_up))
            return model.Vec2Double(
                from_pos.x + (time_1 * v_x) * get_sign(to_pos.x - from_pos.x),
                from_pos.y + time_1 * game_params.unit_fall_speed if math.fabs(self.from_position.x - self.to_position.x) > 0.1 else to_pos.y
            )

        super().__init__(from_pos, to_pos, game_params)

        self.middle_position = get_middle_position(self.from_position, self.to_position, self.game_params)
        self.jump_changed = False

    def is_in_high_point(self, position: model.Vec2Double):
        return is_same_position(position, self.middle_position)

    def get_jump(self, position: model.Vec2Double):
        if not self.jump_changed and is_same_position(position, self.middle_position):
            self.jump_changed = True
        return not self.jump_changed and not is_same_position(position, self.middle_position)

    @staticmethod
    def can_jump_to(game: model.Game, from_position: model.Vec2Double, to_position: model.Vec2Double):
        pass


class Movement:
    def __init__(self, move_type, move_param):
        self.move_type = move_type
        self.move_param = move_param


class MyStrategy:
    def __init__(self):
        self.is_initialized = False
        self.jump_dy_max = 0
        self.jump_dx_max = 0

        self.ground_tiles = [model.tile.Tile.WALL, model.tile.Tile.PLATFORM]

        self.movement = deque()

    def make_graph(self, game: model.Game):
        def is_under_surface(tiles, i, j):
            if tiles[i][j] == model.tile.Tile.EMPTY and\
                j > 0 and\
                    tiles[i][j-1] in self.ground_tiles:
                return True
            return False

        graph = []
        vertexes = []
        tiles = game.level.tiles
        for i, tile_row in enumerate(tiles):
            surface_map = []
            for j, tile in enumerate(tile_row):
                if is_under_surface(tiles, i, j):
                    surface_map.append('1')
                    vertexes.append(GTile(tile, model.Vec2Double(i, j)))
                else:
                    surface_map.append('0')
            graph.append(surface_map)
        g = Graph(game, vertexes)
        return graph

    def initialize(self, unit: model.Unit, game: model.Game):
        if not self.is_initialized:
            self.jump_dy_max = game.properties.unit_jump_time * game.properties.unit_jump_speed
            self.jump_dx_max = game.properties.unit_jump_time * game.properties.unit_max_horizontal_speed
            graph = self.make_graph(game)

            graph[int(unit.position.x)][int(unit.position.y)] = '!'
            for row in reversed(list(map(list, zip(*graph)))):
                print(''.join(row))

            self.is_initialized = True

    def current_movement(self) -> Movement:
        if len(self.movement) > 0:
            return self.movement[-1]
        else:
            return None

    def get_action(self, unit: model.Unit, game: model.Game, debug):
        # Replace this code with your own

        self.initialize(unit, game)

        aim = model.Vec2Double(0, 0)

        move = self.current_movement()

        jump = False
        velocity = 0

        if move is None:
            pass
        elif move.move_type == MovementType.KILL_ENEMY:
            pass
        elif move.move_type == MovementType.MOVE_TO:
            move_param = move.move_param  # type: MoveParam
            if move_param.is_in_destination(unit.position):
                velocity = 0
                self.movement.pop()
            else:
                velocity = move_param.get_velocity(unit.position)
        elif move.move_type == MovementType.JUMP_TO:
            move_params = move.move_param  # type: JumpParams
            if move_params.is_in_destination(unit.position):
                velocity = 0
                jump = False
                self.movement.pop()
            else:
                velocity = move_params.get_velocity(unit.position)
                jump = move_params.get_jump(unit.position)

        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=False,
            aim=aim,
            shoot=True,
            reload=False,
            swap_weapon=False,
            plant_mine=False)
