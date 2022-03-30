import sys
import math
import time
import pygame
import random
import copy


# event handler class
class EventHandler:
    def __init__(self, width):
        self.mouse_pres_start = 0
        self.mouse_pres_end = 0
        self.event_parameters = {}
        self.move_tank = 0
        self.active_missile = None
        self.width = width
        self.shoot = False

    def handle_events(self):
        mouse_pres_interval = 0
        self.active_missile = None
        if self.mouse_pres_start != 0:
            self.event_parameters.update({"pull": min((time.time() - self.mouse_pres_start) / 2, 1)})
        else:
            self.event_parameters.update({"pull": 0})
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pres_start = time.time()
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pres_end = time.time()
                if self.shoot:
                    mouse_pres_interval = (self.mouse_pres_end - self.mouse_pres_start) / 2
                else:
                    self.shoot = True

                self.mouse_pres_start = 0
                if mouse_pres_interval > 1:
                    mouse_pres_interval = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.move_tank = 0.002 * self.width
                if event.key == pygame.K_LEFT:
                    self.move_tank = -0.002 * self.width
                if event.key == pygame.K_1:
                    self.active_missile = 0
                if event.key == pygame.K_2:
                    self.active_missile = 1
                if event.key == pygame.K_3:
                    self.active_missile = 2
                if event.key == pygame.K_4:
                    self.active_missile = 3
                if event.key == pygame.K_5:
                    self.active_missile = 4
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    self.move_tank = 0

        self.event_parameters.update({"power": mouse_pres_interval})
        self.event_parameters.update({"move_tank": self.move_tank})
        self.event_parameters.update({"active_missile": self.active_missile})
        return self.event_parameters