import sys
import math
import time
import pygame
import random
import copy
from GameElements.Missile import Missile
maps = ["static/gravel.png", "static/black.png", "static/houses.png", "static/first_map.png"]
parachute_path = "static/parachute.png"
tank_path = "static/round_tank.png"
bg_path = "static/bg.png"
chest_path = "static/chest.png"
grenade_path = "static/grenade.png"
bouncing_path = "static/bouncing.png"
fastball_path = "static/fastball.png"
gunpoint_path = "static/gunpoint.png"

# tank class
class Tank:
    def __init__(self, parameters):
        # tank image
        self.scale = parameters[4][0] / 2000
        self.width = parameters[4][0]
        self.height = parameters[4][1]
        self.color = parameters[6]
        self.parachute = pygame.transform.scale(pygame.image.load(parachute_path),
                                                (int(90 * self.scale), int(90 * self.scale))).convert_alpha()
        self.tank_image = pygame.transform.scale(pygame.image.load(tank_path),
                                                 (int(60 * self.scale), int(40 * self.scale))).convert_alpha()
        w, h = self.tank_image.get_size()
        r, g, b, _ = self.color
        for x in range(w):
            for y in range(h):
                a = self.tank_image.get_at((x, y))[3]
                self.tank_image.set_at((x, y), pygame.Color(r, g, b, a))
        self.tank_image_rotated = pygame.transform.rotozoom(self.tank_image, parameters[2], 1)
        self.tank_image_rect = self.tank_image_rotated.get_rect(center=(parameters[0], parameters[1]))
        self.parachute_image_rect = self.parachute.get_rect(
            center=(parameters[0], int(parameters[1] - 30 * self.scale)))

        # tank position
        self.x = self.tank_image_rect.center[0]
        self.y = self.tank_image_rect.center[1]
        self.angle = parameters[2]
        self.length = math.sqrt((self.tank_image_rect.topleft[0] - self.tank_image_rect.center[0]) ** 2 + (
                self.tank_image_rect.topleft[1] - self.tank_image_rect.center[1]) ** 2)

        # tank parameters
        self.name = parameters[3]
        self.team = parameters[5]
        self.missile_damage = [50, 25, 50, 45, 50]
        self.missile_radius = [60, 30, 60, 20, 60]
        self.hp = 100
        self.missile = None
        self.missiles = [999, 1, 1, 1, 1]
        self.active_missile = 0

    def barrel(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x == self.x and mouse_y == self.y:
            mouse_x += 1
        dis = math.sqrt((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2)
        end_x = int((float(mouse_x - self.x) * self.length) / dis) - 10 * self.scale * math.sin(self.angle * 6.28 / 360)
        end_y = int((float(mouse_y - self.y) * self.length) / dis) - 10 * self.scale * math.cos(self.angle * 6.28 / 360)
        return end_x, end_y

    def index(self, x, terrain):
        ind = -1
        block = False
        for i in range(len(terrain[x])):
            if not block:
                if terrain[x][i][0] < self.y + 12 * self.scale < terrain[x][i][1]:
                    block = True
                if ind == -1 and terrain[x][i][0] > self.y + 12 * self.scale:
                    if i == 0 or terrain[x][i - 1][1] < terrain[x][i][0] - 40 * self.scale:
                        ind = i
        return ind

    # move tank
    def move(self, move_tank, terrain):
        if (self.x <= 35 * self.scale and move_tank < 0) or (self.x > self.width - 36 * self.scale and move_tank > 0):
            return
        n = int(self.x + move_tank)

        ind = self.index(n, terrain)
        if ind != -1:
            self.x += move_tank
            if self.y - terrain[int(self.x)][ind][0] + 20 * self.scale < -8 * self.scale:

                self.parachute_image_rect = self.parachute.get_rect(center=(self.x, self.y - 50 * self.scale))
                self.y += 4 * self.scale
            elif ind != -1:
                self.y = terrain[int(self.x)][ind][0] - 20 * self.scale
                self.parachute_image_rect = self.parachute.get_rect(center=(self.x, -500 * self.scale))
        dis_y = (terrain[int(self.x - 20 * self.scale)][
                     self.index(int(self.x - 20 * self.scale), terrain)][0] -
                 terrain[int(self.x + 20 * self.scale)][
                     self.index(int(self.x + 20 * self.scale), terrain)][0])
        if abs(dis_y) < 80 * self.scale:
            self.angle = math.atan(dis_y / (40 * self.scale)) / (
                6.28) * 360
        self.tank_image_rotated = pygame.transform.rotozoom(self.tank_image, self.angle, 1)
        self.tank_image_rect = self.tank_image_rotated.get_rect(center=(self.x, self.y))

    # create missile on shoot
    def shoot(self, power, active_missile):
        if active_missile is not None and self.missiles[active_missile] > 0 and self.missile is None:
            self.active_missile = active_missile
        if power > 0 and self.missile is None and self.missiles[self.active_missile] > 0:
            power *= 20 * self.scale
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dis = math.sqrt((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2)
            x = self.x + int((float(mouse_x - self.x) * self.length) / dis)
            y = self.y + int((float(mouse_y - self.y) * self.length) / dis)
            speed_x = (float(mouse_x - self.x) * power) / dis
            speed_y = (float(mouse_y - self.y) * power) / dis
            self.missiles[self.active_missile] -= 1
            self.missile = Missile(active_missile, x, y, speed_x, speed_y, self.missile_damage[self.active_missile],
                                   self.missile_radius[self.active_missile])

    # move missile if exist
    def move_missile(self):
        if self.missile is not None:
            destroy_missile = self.missile.move()
            if destroy_missile:
                self.missile = None

    def missile_exists(self):
        return self.missile is not None