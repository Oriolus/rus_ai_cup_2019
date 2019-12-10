import model
import math

from collections import deque
import enum


class MovementType(enum.Enum):
    KILL_ENEMY = 0
    MOVE_TO = 1
    JUMP_TO = 2


class Movement:
    def __init__(self, move_type, move_param):
        self.move_type = move_type
        self.move_param = move_param


class MyStrategy:
    def __init__(self):
        self.is_initialized = False
        self.jump_dy_max = 0
        self.jump_dx_max = 0

        self.movement = deque()
        # self.movement.appendleft(Movement(MovementType.JUMP_TO, model.Vec2Double(32., 1.)))
        self.movement.appendleft(Movement(MovementType.MOVE_TO, model.Vec2Double(38., 1.)))
        self.movement.appendleft(Movement(MovementType.MOVE_TO, model.Vec2Double(35., 1.)))

    def initialize(self, unit: model.Unit, game: model.Game):
        if not self.is_initialized:
            self.jump_dy_max = game.properties.unit_jump_time * game.properties.unit_jump_speed
            self.jump_dx_max = game.properties.unit_jump_time * game.properties.unit_max_horizontal_speed
            self.is_initialized = True

    def current_movement(self) -> Movement:
        if len(self.movement) > 0:
            return self.movement[0]
        else:
            return None

    def get_action(self, unit: model.Unit, game: model.Game, debug):
        # Replace this code with your own
        def distance_sqr(a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

        def distance(a, b):
            return math.sqrt(math.fabs(distance_sqr(a, b)))

        def is_same_position(a, b):
            return distance(a, b) < 0.1

        self.initialize(unit, game)

        target_pos = unit.position
        aim = model.Vec2Double(0, 0)
        jump = target_pos.y > unit.position.y

        move = self.current_movement()

        jump = False
        velocity = 0

        if move is None:
            pass
        elif move.move_type == MovementType.KILL_ENEMY:
            pass
        elif move.move_type == MovementType.MOVE_TO:
            if is_same_position(move.move_param, unit.position):
                velocity = 0
                self.movement.popleft()
            else:
                velocity = (move.move_param.x - unit.position.x) * 100
        elif move.move_type == MovementType.JUMP_TO:
            if is_same_position(move.move_param, unit.position):
                velocity = 0
                jump = False
                self.movement.popleft()
            else:
                velocity = (move.move_param.x - unit.position.x) * 100
                jump = velocity != 0.

        debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))

        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=False,
            aim=aim,
            shoot=True,
            reload=False,
            swap_weapon=False,
            plant_mine=False)
