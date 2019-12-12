import math

from typing import List
from collections import deque
from datetime import datetime
from copy import deepcopy

import model
from movements import JumpParams, MoveParam, MovementType, Movement


class GTile(object):
    def __init__(self, tile: model.Tile, position: model.Vec2Double):
        self.tile = tile
        self.position = position

    def stred_position(self):
        return str(int(self.position.x)) + str(int(self.position.y))

    def __repr__(self):
        return '(x={};y={}):{}'.format(int(self.position.x), int(self.position.y), self.tile)

    def get_tuple(self):
        return self.position.get_tuple()


class GraphVertex(object):
    def __init__(self, from_pos: model.Vec2Double, to_pos: model.Vec2Double, move_type: MovementType, game: model.Game):
        self.from_position = from_pos
        self.to_position = to_pos
        self.move_type = move_type
        self.game = game
        self.move_time = 0

    def get_movement(self):
        if self.move_type == MovementType.JUMP_TO:
            return Movement(
                self.move_type,
                JumpParams(self.from_position, self.to_position, self.game.properties)
            )
        if self.move_type == MovementType.MOVE_TO:
            return Movement(
                self.move_type,
                MoveParam(self.from_position, self.to_position, self.game.properties)
            )
        return None

    def __repr__(self):
        return '({};{})->({};{}):{}'.format(self.from_position.x, self.from_position.y,
                                            self.to_position.x, self.to_position.y,
                                            self.move_type)

    def __hash__(self):
        return hash(self.from_position.x)


class Graph(object):
    def __init__(self, game: model.Game, vertexes: list):
        def build_matrix(vertices: List[GTile], game: model.Game):
            _tiles = list(zip(*game.level.tiles))
            matrix = []
            # Строим матрицу смежности:
            #     1. по всем вершинам ищем пешие пути
            for i, v_from in enumerate(vertices):
                self.vertexes_map[v_from.get_tuple()] = i
                path_to = []
                for v_to in vertices:
                    if v_from.stred_position() != v_to.stred_position():
                        if v_from.position.y == v_to.position.y and v_from.position.y > 0:
                            max_x = max([v_from.position.x, v_to.position.x])
                            min_x = min([v_from.position.x, v_to.position.x])

                            tiles_between = _tiles[int(v_from.position.y)][min_x:max_x]
                            tiles_under = _tiles[int(v_from.position.y - 1)][min_x:max_x]

                            # if v_to.position.x == 37. and v_to.position.y == 1.:
                            #     a = 1
                            #
                            # if v_from.position.x == 37 and v_from.position.y == 1:
                            #     a = 1

                            if model.Tile.WALL not in tiles_between\
                                    and model.Tile.JUMP_PAD not in tiles_between\
                                    and model.Tile.EMPTY not in tiles_under:
                                path_to.append(GraphVertex(v_from.position, v_to.position, MovementType.MOVE_TO, game))
                            elif model.Tile.EMPTY in tiles_under:
                                is_one_jump = JumpParams.is_one_jump_avail(
                                    game,
                                    from_position=v_from.position,
                                    to_position=v_to.position
                                )
                                if is_one_jump:
                                    path_to.append(GraphVertex(v_from.position, v_to.position, MovementType.JUMP_TO, game))
                                else:
                                    path_to.append(None)
                            elif model.Tile.JUMP_PAD in tiles_between:
                                if JumpParams.is_one_jump_avail(game, v_from.position, v_to.position):
                                    path_to.append(GraphVertex(v_from.position, v_to.position, MovementType.JUMP_TO, game))
                                else:
                                    path_to.append(None)
                            elif model.Tile.WALL in tiles_between:
                                is_one_jump = JumpParams.is_one_jump_avail(
                                    game,
                                    from_position=v_from.position,
                                    to_position=v_to.position
                                )
                                if is_one_jump:
                                    path_to.append(GraphVertex(v_from.position, v_to.position, MovementType.JUMP_TO, game))
                                else:
                                    path_to.append(None)
                            else:
                                path_to.append(None)
                        else:
                            if JumpParams.is_one_jump_avail(game, v_from.position, v_to.position):
                                path_to.append(GraphVertex(v_from.position, v_to.position, MovementType.JUMP_TO, game))
                            else:
                                path_to.append(None)
                    else:
                        path_to.append(None)
                matrix.append(path_to)
            return matrix

        self.game = game
        self.vertexes = vertexes  # type: List[GTile]
        self.vertexes_map = {}
        self.matrix = build_matrix(self.vertexes, game)
        self.game = game

    def get_path(self, position_from: model.Vec2Double, position_to: model.Vec2Double, game: model.Game) -> List[Movement]:
        path = []
        index_from = self.vertexes_map[(int(position_from.x), int(position_from.y))]
        index_to = self.vertexes_map[(int(position_to.x), int(position_to.y))]
        if not index_from or not index_to:
            return None
        reverse_path = [None, ] * len(self.vertexes)
        queue = deque()
        queue.append(index_from)
        reverse_path[index_from] = (-1, None)
        step = 1
        while len(queue) > 0:
            cur_i = queue.pop()
            iteration_vertex = self.vertexes[cur_i]
            for i, vert in enumerate(self.matrix[cur_i]):
                if vert is not None and not reverse_path[i]:
                    if self.vertexes_map[vert.to_position.get_tuple()] == index_to:
                        path.append(vert)
                        prev_pos = cur_i
                        while prev_pos != -1:
                            path.append(reverse_path[prev_pos][1])
                            prev_pos = reverse_path[prev_pos][0]
                        queue.clear()
                        break
                    queue.append(i)
                    reverse_path[i] = (cur_i, vert)
            step += 1
        return [a.get_movement() for a in path[:-1]]

    def __vertex_index_by_coord(self, vertex: model.Vec2Double):
        v_x = round(vertex.x)
        v_y = round(vertex.y)
        ind = None
        for i, v in enumerate(self.vertexes):
            if v.position.x == v_x and v.position.y == v_y:
                return i


class MyStrategy:
    def __init__(self):
        self.is_initialized = False
        self.jump_dy_max = 0
        self.jump_dx_max = 0
        self.graph = None

        self.ground_tiles = [model.tile.Tile.WALL, model.tile.Tile.PLATFORM]

        self.movement = deque()

    def make_graph(self, game: model.Game):
        def is_under_surface(tiles, i, j):
            # TODO: добавить лестницы!!!
            if tiles[i][j] in [model.Tile.EMPTY, model.Tile.LADDER] and\
                j > 0 and\
                    tiles[i][j-1] in self.ground_tiles:
                return True
            return False

        vertexes = []
        tiles = game.level.tiles
        for i, tile_row in enumerate(tiles):
            for j, tile in enumerate(tile_row):
                if is_under_surface(tiles, i, j):
                    vertexes.append(GTile(tile, model.Vec2Double(i, j)))
        g = Graph(game, vertexes)
        return g

    def initialize(self, unit: model.Unit, game: model.Game):
        if not self.is_initialized:
            self.jump_dy_max = game.properties.unit_jump_time * game.properties.unit_jump_speed
            self.jump_dx_max = game.properties.unit_jump_time * game.properties.unit_max_horizontal_speed
            print(str(datetime.now()))
            self.graph = self.make_graph(game)
            print(str(datetime.now()))

            a = self.graph.get_path(unit.position, model.Vec2Double(20., 1.), game)

            self.movement.extend(a)

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
