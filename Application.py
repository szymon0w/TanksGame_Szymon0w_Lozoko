import sys
import math
import time
import pygame
import random
import copy
from GraphicElements.StartingScreen import StartingScreen
from GraphicElements.Button import Button
from ImageHandler import ImageHandler
from EventHandler import EventHandler
from GameEngine import GameEngine
maps = ["static/gravel.png", "static/black.png", "static/houses.png", "static/first_map.png"]
parachute_path = "static/parachute.png"
tank_path = "static/round_tank.png"
bg_path = "static/bg.png"
chest_path = "static/chest.png"
grenade_path = "static/grenade.png"
bouncing_path = "static/bouncing.png"
fastball_path = "static/fastball.png"
gunpoint_path = "static/gunpoint.png"


# application class
# noinspection PyTypeChecker
class Application:
    def __init__(self):
        self.image_handler = None
        self.event_handler = None
        self.game_engine = None
        pygame.init()
        self.starting_parameters = {}
        self.starting_tanks = [("red", pygame.Color(255, 0, 0)), ("green", pygame.Color(0, 108, 0)),
                               ("blue", pygame.Color(0, 0, 120)),
                               ("purple", pygame.Color(120, 0, 120)), ("yellow", pygame.Color(230, 230, 0)),
                               ("black", pygame.Color(0, 0, 0)),
                               ("pink", pygame.Color(220, 0, 150)), ("orange", pygame.Color(220, 90, 0))]
        self.starting_parameters.update({"boxes_parameters": [0.3, 1]})
        self.clock = pygame.time.Clock()
        self.starting_screen = StartingScreen()
        self.starting_screen.add_buttons()

    def starting(self):
        screen_size = (900, 600)
        number_of_players = 2
        game_type = "free_for_all"
        my_map = 0
        run = True
        while run:
            self.starting_screen.redraw_window()
            pygame.display.update()

            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(len(self.starting_screen.players_button)):
                        if self.starting_screen.players_button[index].is_over(pos):
                            number_of_players = index + 2
                            for i in range(len(self.starting_screen.players_button)):
                                if i == index:
                                    self.starting_screen.players_button[i].color = (250, 0, 0)
                                else:
                                    self.starting_screen.players_button[i].color = (0, 0, 250)
                    for index in range(len(self.starting_screen.screen_size_button)):
                        if self.starting_screen.screen_size_button[index].is_over(pos):
                            screen_size = (int(300 * (1 + index / 2)), int(200 * (1 + index / 2)))
                            for i in range(len(self.starting_screen.screen_size_button)):
                                if i == index:
                                    self.starting_screen.screen_size_button[i].color = (250, 0, 0)
                                else:
                                    self.starting_screen.screen_size_button[i].color = (0, 0, 250)

                    for index in range(len(self.starting_screen.map_button)):
                        if self.starting_screen.map_button[index].is_over(pos):
                            my_map = index
                            for i in range(len(self.starting_screen.map_button)):
                                if i == index:
                                    self.starting_screen.map_button[i].color = (250, 0, 0)
                                else:
                                    self.starting_screen.map_button[i].color = (0, 0, 250)

                    for index in range(len(self.starting_screen.game_type_button)):
                        if self.starting_screen.game_type_button[index].is_over(pos):
                            if index == 0:
                                game_type = "free_for_all"
                            elif index == 1:
                                game_type = "team_death_match"
                            for i in range(len(self.starting_screen.game_type_button)):
                                if i == index:
                                    self.starting_screen.game_type_button[i].color = (250, 0, 0)
                                else:
                                    self.starting_screen.game_type_button[i].color = (0, 0, 250)
                    if self.starting_screen.start_button.is_over(pos):
                        run = False
        self.starting_parameters.update({"screen_parameters": screen_size})
        self.starting_parameters.update({"map": maps[my_map]})
        tanks = []
        if game_type == "team_death_match":
            for index in range(number_of_players):
                if index % 2 == 1:
                    tanks.append((random.randint(int(0.1 * screen_size[0]), int(0.9 * screen_size[0])), 0, 0,
                                  self.starting_tanks[0][0], screen_size, 1, self.starting_tanks[0][1]))
                else:
                    tanks.append((random.randint(int(0.1 * screen_size[0]), int(0.9 * screen_size[0])), 0, 0,
                                  self.starting_tanks[5][0], screen_size, 2, self.starting_tanks[5][1]))
        else:
            for index in range(number_of_players):
                team = 1
                if index > (number_of_players - 1) / 2:
                    team = 2
                tanks.append((random.randint(int(0.1 * screen_size[0]), int(0.9 * screen_size[0])), 0, 0,
                              self.starting_tanks[index][0], screen_size, team, self.starting_tanks[index][1]))
        self.starting_parameters.update({"tank_parameters": tanks})
        self.starting_parameters.update({"game_mode": game_type})
        self.image_handler = ImageHandler(self.starting_parameters)
        self.event_handler = EventHandler(self.starting_parameters["screen_parameters"][0])
        self.game_engine = GameEngine(self.starting_parameters, self.image_handler.terrain_image)

    def run(self):
        while True:
            event_parameters = self.event_handler.handle_events()
            parameters = self.game_engine.game_loop(event_parameters)
            self.image_handler.update(parameters)
            self.clock.tick(60)
