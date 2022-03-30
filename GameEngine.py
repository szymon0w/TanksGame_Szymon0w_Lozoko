import sys
import math
import time
import pygame
import random
import copy
from GameElements.Tank import Tank
from GameElements.Missile import Missile
from GameElements.Box import Box


def missile_tank_collision(shooting_tank, tanks, missile, scale):
    for tank in tanks:
        if tank is not shooting_tank:
            if math.sqrt((tank.x - missile.x) ** 2 + (tank.y - missile.y) ** 2) < min(missile.radius, 30) * scale:
                return True
    return False


class CollisionDetector:
    def __init__(self, terrain_position):
        self.terrain_position = terrain_position

    def missile_terrain_collision(self, missile):
        for interval in self.terrain_position[round(missile.x)]:
            if interval[0] <= round(missile.y) <= interval[1]:
                return True
        return False


# game engine class
# noinspection PyTypeChecker
class GameEngine:
    def __init__(self, starting_parameters, terrain_image):
        self.parameters = {}
        self.scale = starting_parameters["screen_parameters"][0] / 2000
        self.width = starting_parameters["screen_parameters"][0]
        self.height = starting_parameters["screen_parameters"][1]
        self.game_mode = starting_parameters["game_mode"]
        self.turn_timer = time.time()
        # terrain
        self.terrain = self.create_slices(terrain_image)
        self.parameters.update({"terrain": self.terrain})

        # tank
        tank_parameters = starting_parameters["tank_parameters"]
        self.tanks = [Tank(tank_parameters[i])
                      for i in range(len(tank_parameters))]
        self.tank = self.tanks[0]
        self.tank_index = 0

        # special missiles
        self.dummy_missile_owner = None
        self.bouncy_timer = None
        self.dummy_power = 0

        # collision
        self.collision_detector = CollisionDetector(self.terrain)
        self.collision = False
        self.gravity_effect = 0.2 * self.scale

        # boxes
        self.chance_of_boxes_spawn = starting_parameters["boxes_parameters"][0]
        self.number_of_boxes_to_spawn = starting_parameters["boxes_parameters"][1]
        self.boxes_spawned = True
        self.boxes = []
        self.end = -1

    def create_slices(self, terrain_image):
        white = terrain_image.map_rgb((255, 255, 255, 255))
        px_array = pygame.PixelArray(terrain_image)
        slices = [[] for _ in range(self.width)]
        y_up = False
        y_up_pos = 0
        for x in range(self.width):
            for y in range(self.height):
                if px_array[x, y] != white:
                    if not y_up:
                        y_up = True
                        y_up_pos = y
                elif y_up and y_up_pos < y:
                    y_up = False
                    slices[x].append([y_up_pos, y])
            if y_up_pos != 0 and y_up_pos < self.height:
                slices[x].append([y_up_pos, self.height])
            y_up = False
            y_up_pos = 0
        return slices

    def game_loop(self, event_parameters):
        # boxes moving
        for box in self.boxes:
            box.move(self.terrain)
        if not self.boxes_spawned:
            self.spawn_boxes()
        # tank shooting
        power = event_parameters["power"]
        self.dummy_power = event_parameters["pull"]
        active_missile = event_parameters["active_missile"]

        if self.tank.active_missile == 4:
            self.move_smart_missile_and_check_collisions()
            self.smart_explosion()

        self.tank.shoot(power, active_missile)
        # tank moving
        move = event_parameters["move_tank"]
        if self.dummy_power > 0:
            move = 0
        self.tank.move(move, self.terrain)
        for t in self.tanks:
            if t is not self.tank:
                t.move(0, self.terrain)
        self.pick_boxes()

        # move and check for collisions
        if self.tank.active_missile == 0:
            self.move_standard_missile_and_check_collisions()
            self.standard_explosion()
        elif self.tank.active_missile == 1:
            self.move_grenade_missile_and_check_collisions()
            self.grenade_explosion()
        elif self.tank.active_missile == 2:
            self.move_bounce_missile_and_check_collisions()
            self.bouncy_explosion()
        elif self.tank.active_missile == 3:
            self.move_fast_missile_and_check_collisions()
            self.standard_explosion()

        if time.time() - self.turn_timer > 15 and self.dummy_missile_owner is None and not self.tank.missile_exists() \
                and self.dummy_power == 0:
            self.end = self.end_turn()

        # parameters update
        self.parameters.update({"time": time.time() - self.turn_timer})
        self.parameters.update({"active_missile": active_missile})
        self.parameters.update({"boxes": self.boxes})
        self.parameters.update({"pull": event_parameters["pull"]})
        self.parameters.update({"tanks": self.tanks})
        self.parameters.update({"active_tank": self.tank_index})
        self.parameters.update({"barrel": self.tank.barrel()})
        self.parameters.update({"end": self.end})
        if self.dummy_missile_owner is not None:
            self.parameters.update({"missiles": self.dummy_missile_owner})
        else:
            self.parameters.update({"missiles": self.tank.missile})
        return self.parameters

    def move_standard_missile_and_check_collisions(self):
        self.collision = False
        missile = self.tank.missile
        if self.tank.missile_exists():
            missile.speed_y += self.gravity_effect
            max_v = max(abs(missile.speed_x), abs(missile.speed_y))
            for i in range(round(max_v)):
                missile.move(missile.speed_x / max_v, missile.speed_y / max_v)
                if round(missile.x) >= self.width or missile.x < 0 or missile.y > self.height:
                    self.dummy_missile_owner = None
                    self.end = self.end_turn()
                    break
                self.collision = (
                        missile_tank_collision(self.tank, self.tanks,
                                               self.tank.missile, self.scale)
                        or self.collision_detector.missile_terrain_collision(self.tank.missile))
                if self.collision:
                    break

    def standard_explosion(self):
        if not self.collision:
            return
        r = self.tank.missile.radius * self.scale
        r2 = r
        if self.tank.missile.missile_type == 3:
            r2 = 2 * r
        missile_x = round(self.tank.missile.x)
        missile_y = round(self.tank.missile.y)
        self.remove_terrain_y_dif(missile_x, missile_y, r)
        self.damage_tanks(missile_x, missile_y, r2, self.tank.missile.damage)
        self.end = self.end_turn()

    def move_grenade_missile_and_check_collisions(self):
        self.collision = False
        if self.dummy_missile_owner is None:
            if self.tank.missile_exists():
                self.move_standard_missile_and_check_collisions()
        else:
            missiles = self.dummy_missile_owner
            if len(missiles) == 0:
                self.dummy_missile_owner = None
                self.end = self.end_turn()
            else:
                index = 0
                while index < len(missiles):
                    missile = missiles[index]
                    missile.speed_y += self.gravity_effect
                    max_v = max(abs(missile.speed_x), abs(missile.speed_y))
                    for i in range(round(max_v)):
                        missile.move(missile.speed_x / max_v, missile.speed_y / max_v)
                        if round(missile.x) >= self.width or missile.x < 0 or missile.y > self.height:
                            missiles.pop(index)
                            index -= 1
                            break
                    index += 1
                self.collision = [False] * len(missiles)
                for index, missile in enumerate(missiles):
                    self.collision[index] = (
                            missile_tank_collision(self.tank, self.tanks,
                                                   missile, self.scale)
                            or self.collision_detector.missile_terrain_collision(missile))

    def grenade_explosion(self):
        if not self.collision:
            return
        if type(self.collision) != list:
            r = self.tank.missile.radius * self.scale
            missile_x = round(self.tank.missile.x)
            missile_y = round(self.tank.missile.y)
            self.remove_terrain_y_dif(missile_x, missile_y, r)
            x = self.tank.missile.x
            y = self.tank.missile.y
            old_speed_x = self.tank.missile.speed_x
            power = 5 * self.scale
            active_missile = self.tank.active_missile
            damage = self.tank.missile.damage
            radius = self.tank.missile.radius / 1.5
            self.dummy_missile_owner = []
            for i in range(5):
                speed_x = math.cos(i / 4 * math.pi) * power + old_speed_x
                speed_y = -(math.sin(i / 4 * math.pi) * power + power / 5)
                self.dummy_missile_owner.append(Missile(active_missile, x, y, speed_x, speed_y, damage, radius))

            self.damage_tanks(missile_x, missile_y, r, self.tank.missile.damage)
            self.tank.missile = None
        elif type(self.collision) == list:
            if len(self.dummy_missile_owner) == 0:
                self.dummy_missile_owner = None
                self.end = self.end_turn()
            else:
                index = 0
                while index < len(self.dummy_missile_owner):
                    if self.collision[index]:
                        r = self.dummy_missile_owner[index].radius * self.scale
                        missile_x = round(self.dummy_missile_owner[index].x)
                        missile_y = round(self.dummy_missile_owner[index].y)
                        self.remove_terrain_y_dif(missile_x, missile_y, r)
                        self.damage_tanks(missile_x, missile_y, r, self.dummy_missile_owner[index].damage)
                        self.dummy_missile_owner.pop(index)
                        self.collision.pop(index)
                        index -= 1
                    index += 1

    def move_bounce_missile_and_check_collisions(self):
        def index(x, y, terrain):
            for ind in range(len(terrain[x])):
                if terrain[x][ind][0] >= y - 2:
                    return ind
            return -1

        def index2(x, y, terrain):
            for ind in range(len(terrain[x])):
                if terrain[x][ind][1] <= y + 2:
                    return ind
            return -1

        self.collision = False
        missile = self.tank.missile
        if self.tank.missile_exists():
            if self.bouncy_timer is None:
                self.bouncy_timer = time.time()
            missile.speed_y += self.gravity_effect
            max_v = max(abs(missile.speed_x), abs(missile.speed_y))
            for i in range(round(max_v)):
                missile.move(missile.speed_x / max_v, missile.speed_y / max_v)
                if round(missile.x) >= self.width or missile.x < 0 or missile.y > self.height:
                    self.end = self.end_turn()
                    self.bouncy_timer = None
                    break
                self.collision = (
                    self.collision_detector.missile_terrain_collision(self.tank.missile))
                if self.collision:
                    missile.move(-2 * (missile.speed_x / max_v), -2 * (missile.speed_y / max_v))
                    if missile.speed_y > 0:
                        dis_y = (self.terrain[int(missile.x - 2 * self.scale)][
                                     index(int(missile.x - 2 * self.scale), missile.y, self.terrain)][0] -
                                 self.terrain[int(missile.x + 2 * self.scale)][
                                     index(int(missile.x + 2 * self.scale), missile.y, self.terrain)][0])
                    else:
                        dis_y = (self.terrain[int(missile.x - 2 * self.scale)][
                                     index2(int(missile.x - 2 * self.scale), missile.y, self.terrain)][1] -
                                 self.terrain[int(missile.x + 2 * self.scale)][
                                     index2(int(missile.x + 2 * self.scale), missile.y, self.terrain)][1])
                    angle = math.atan(dis_y / (8 * self.scale))
                    alpha = math.atan(missile.speed_y / missile.speed_x)
                    v = missile.speed_x / math.cos(alpha) * 0.8
                    alpha += angle
                    missile.speed_x = v * math.cos(alpha)
                    missile.speed_y = -v * math.sin(alpha)
                    break

    def bouncy_explosion(self):
        if self.bouncy_timer is not None and time.time() - self.bouncy_timer > 10:
            self.collision = True
            self.bouncy_timer = None
            self.standard_explosion()

    def move_fast_missile_and_check_collisions(self):
        self.collision = False
        missile = self.tank.missile
        if self.tank.missile_exists():
            speed_y = 3 * missile.speed_y
            speed_x = 3 * missile.speed_x
            max_v = max(abs(speed_x), abs(speed_y))
            speed_y = speed_y / max_v * 7
            speed_x = speed_x / max_v * 7
            for i in range(round(max_v)):
                missile.move(speed_x / max_v, speed_y / max_v)
                if round(missile.x) >= self.width or missile.x < 0 or missile.y > self.height or missile.y < 0:
                    self.end = self.end_turn()
                    break
                self.collision = (
                        missile_tank_collision(self.tank, self.tanks,
                                               self.tank.missile, self.scale)
                        or self.collision_detector.missile_terrain_collision(self.tank.missile))
                if self.collision:
                    break

    def move_smart_missile_and_check_collisions(self):
        def dummy_shoot():
            length = self.tank.length
            power = self.dummy_power * 20 * self.scale
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dis = math.sqrt((mouse_x - self.tank.x) ** 2 + (mouse_y - self.tank.y) ** 2)
            dummy_x = self.tank.x + int((float(mouse_x - self.tank.x) * length) / dis)
            dummy_y = self.tank.y + int((float(mouse_y - self.tank.y) * length) / dis)
            dummy_speed_x = (float(mouse_x - self.tank.x) * power) / dis
            dummy_speed_y = (float(mouse_y - self.tank.y) * power) / dis
            return dummy_x, dummy_y, dummy_speed_x, dummy_speed_y

        if self.dummy_power > 0 and self.tank.missiles[4] > 0:
            self.dummy_missile_owner = []
            x, y, speed_x, speed_y = dummy_shoot()
            missile = Missile(-1, x, y, speed_x, speed_y, 0, 0)
            self.dummy_missile_owner.append(missile)
            for _ in range(9):
                missile = copy.copy(self.dummy_missile_owner[-1])
                for j in range(10):
                    missile.speed_y += self.gravity_effect
                    max_v = max(abs(missile.speed_x), abs(missile.speed_y))
                    for i in range(round(max_v)):
                        missile.move(missile.speed_x / max_v, missile.speed_y / max_v)
                self.dummy_missile_owner.append(missile)

        self.move_standard_missile_and_check_collisions()
        if self.tank.missile_exists():
            self.dummy_missile_owner.append(self.tank.missile)

    def smart_explosion(self):
        if not self.collision:
            return
        self.standard_explosion()
        self.dummy_missile_owner = None

    def remove_terrain_y_dif(self, missile_x, missile_y, r):
        r2 = r ** 2
        for explosion_x in range(int(missile_x - r) + 1, int(missile_x + r)):
            y_dif = round(math.sqrt(r2 - (missile_x - explosion_x) ** 2))
            self.remove_terrain(explosion_x, missile_y, y_dif)

    def remove_terrain(self, explosion_x, missile_y, y_dif):
        if explosion_x < 0 or explosion_x >= self.width:
            return
        intervals = self.terrain[explosion_x]
        interval_length = len(intervals)
        int_index = 0
        floor = min(missile_y + y_dif, int(self.height - 200 * self.scale))
        while int_index < interval_length:

            if intervals[int_index][0] < missile_y - y_dif and intervals[int_index][1] > floor:
                intervals.insert(int_index, [floor, intervals[int_index][1]])
                int_index += 1
                interval_length += 1
                intervals[int_index][1] = missile_y - y_dif
                intervals[int_index], intervals[int_index - 1] = intervals[int_index - 1], intervals[int_index]
            elif intervals[int_index][0] < missile_y - y_dif <= intervals[int_index][1] <= floor:
                intervals[int_index][1] = missile_y - y_dif
            elif missile_y - y_dif <= intervals[int_index][0] <= floor < intervals[int_index][1]:
                intervals[int_index][0] = floor
            elif intervals[int_index][0] >= missile_y - y_dif and intervals[int_index][1] <= floor:
                intervals.pop(int_index)
                int_index -= 1
                interval_length -= 1
            int_index += 1

    def damage_tanks(self, missile_x, missile_y, r, damage):
        for tank in self.tanks:
            if math.sqrt((missile_x - tank.x) ** 2 + (missile_y - tank.y) ** 2) < r:
                tank.hp -= damage
        index = 0
        while index < len(self.tanks):
            if self.tanks[index].hp <= 0:
                self.tanks.pop(index)
                if index <= self.tank_index:
                    self.tank_index -= 1
                index -= 1
            index += 1

    def spawn_boxes(self):
        if random.uniform(0, 1) < self.chance_of_boxes_spawn:
            for _ in range(self.number_of_boxes_to_spawn):
                self.boxes.append(Box(random.randint(10, self.width - 10), random.randint(1, 4), self.width))
        self.boxes_spawned = True

    def pick_boxes(self):
        index = 0
        while index < len(self.boxes):
            box = self.boxes[index]
            if math.sqrt((self.tank.x - box.x) ** 2 + (self.tank.y - box.y) ** 2) < 30 * self.scale:
                self.tank.missiles[box.type] += 1
                self.boxes.pop(index)
                index -= 1
            index += 1

    def end_turn(self):
        self.tank.missile = None
        self.tank.active_missile = 0
        self.turn_timer = time.time()
        self.tank_index += 1
        if self.tank_index >= len(self.tanks):
            self.tank_index = 0
        if len(self.tanks) == 0:
            print("draw")
            return 0
        self.boxes_spawned = False
        if self.game_mode == "free_for_all":
            if len(self.tanks) == 1:
                print("The winner is ", self.tanks[0].name)
                return 1
            else:
                self.tank = self.tanks[self.tank_index]
        elif self.game_mode == "team_death_match":
            potential_winning_team = self.tanks[0].team
            for tank in self.tanks:
                if tank.team != potential_winning_team:
                    self.tank = self.tanks[self.tank_index]
                    return -1
            print("the winner team is ", potential_winning_team)
            return 2

