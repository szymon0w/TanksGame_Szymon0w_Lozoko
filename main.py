import sys
import math
import time
import pygame
import random
import copy
from Application import Application
from EventHandler import EventHandler
from GameEngine import GameEngine
from GraphicElements.Button import Button
from GraphicElements.StartingScreen import StartingScreen

maps = ["static/gravel.png", "static/black.png", "static/houses.png", "static/first_map.png"]
parachute_path = "static/parachute.png"
tank_path = "static/round_tank.png"
bg_path = "static/bg.png"
chest_path = "static/chest.png"
grenade_path = "static/grenade.png"
bouncing_path = "static/bouncing.png"
fastball_path = "static/fastball.png"
gunpoint_path = "static/gunpoint.png"


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



if __name__ == '__main__':
    application = Application()
    application.starting()
    application.run()
