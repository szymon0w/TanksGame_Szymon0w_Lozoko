import sys
import math
import time
import pygame
import random
import copy
chest_path = "static/chest.png"
parachute_path = "static/parachute.png"


class Box:
    def __init__(self, x, typ, width):
        self.scale = width / 2000
        self.x = x
        self.y = 0
        self.type = typ
        self.box_image = pygame.image.load(chest_path).convert()
        self.box_image = pygame.transform.scale(self.box_image, (int(30 * self.scale), int(30 * self.scale)))
        self.parachute = pygame.transform.scale(pygame.image.load(parachute_path),
                                                (int(90 * self.scale), int(90 * self.scale))).convert_alpha()
        self.parachute_image_rect = self.parachute.get_rect(
            center=(self.x, int(- 15 * self.scale)))
        self.box_image_rect = self.box_image.get_rect(center=(self.x, self.y))

    def move(self, terrain):
        if not terrain[self.x] or self.y < terrain[self.x][0][0] - 4 * self.scale:
            self.y += 4 * self.scale
            self.parachute_image_rect = self.parachute.get_rect(center=(self.x, self.y - 25 * self.scale))
        else:
            self.y = terrain[self.x][0][0]
            self.parachute_image_rect = self.parachute.get_rect(center=(self.x, -500))
        self.box_image_rect = self.box_image.get_rect(center=(self.x, self.y))