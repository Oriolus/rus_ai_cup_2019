import math
import enum
import model

from helper import is_same_position, get_sign, distance


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

    def __repr__(self):
        return 'M({};{})->({};{})'.format(
            self.from_position.x, self.from_position.y,
            self.to_position.x, self.to_position.y
        )


class JumpParams(MoveParam):
    def __init__(self, from_pos: model.Vec2Double, to_pos: model.Vec2Double, game_params: model.Properties):
        def get_middle_position(from_pos: model.Vec2Double, to_pos: model.Vec2Double, game_params: model.Properties):
            # Добавить ограничение по времени
            # Добавить ограничение по геометрии
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

    def __repr__(self):
        return 'J({};{})->({};{})'.format(
            self.from_position.x, self.from_position.y,
            self.to_position.x, self.to_position.y
        )

    def is_in_high_point(self, position: model.Vec2Double):
        return is_same_position(position, self.middle_position)

    def get_jump(self, position: model.Vec2Double):
        if not self.jump_changed and is_same_position(position, self.middle_position):
            self.jump_changed = True
        return not self.jump_changed and not is_same_position(position, self.middle_position)

    @staticmethod
    def get_jump_radius(game_params: model.Properties):
        return math.sqrt(JumpParams.get_jump_max_dx(game_params) ** 2
                         + JumpParams.get_jump_max_dy(game_params) ** 2)

    @staticmethod
    def get_jump_max_dy(game_props: model.Properties):
        return game_props.unit_jump_speed * game_props.unit_jump_time

    @staticmethod
    def get_jump_max_dx(game_props: model.Properties):
        return game_props.unit_jump_time * game_props.unit_max_horizontal_speed

    @staticmethod
    def is_one_jump_avail(game: model.Game, from_position: model.Vec2Double, to_position: model.Vec2Double):
        # Quick check
        max_dx = JumpParams.get_jump_max_dx(game.properties)
        if math.fabs(from_position.x - to_position.x) > max_dx:
            return False
        max_dy = JumpParams.get_jump_max_dy(game.properties)
        if math.fabs(from_position.y - to_position.y) > max_dy:
            return False
        max_r = math.sqrt(max_dy ** 2 + max_dy ** 2)
        if distance(from_position, to_position) > max_r:
            return False

        return True


class Movement:
    def __init__(self, move_type, move_param):
        self.move_type = move_type
        self.move_param = move_param
