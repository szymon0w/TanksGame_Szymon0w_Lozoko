import sys
import math
import time
import pygame
import random
import copy
from GraphicElements.Button import Button
maps = ["static/gravel.png", "static/black.png", "static/houses.png", "static/first_map.png"]
parachute_path = "../static/parachute.png"
tank_path = "../static/round_tank.png"
bg_path = "../static/bg.png"
chest_path = "../static/chest.png"
grenade_path = "../static/grenade.png"
bouncing_path = "../static/bouncing.png"
fastball_path = "../static/fastball.png"
gunpoint_path = "../static/gunpoint.png"


class StartingScreen:
    def __init__(self):
        self.width = 900
        self.height = 700
        self.screen_size_button = []
        self.start_button = Button((0, 255, 0), 320, 25, 250, 100, "START")
        self.players_button = []
        self.game_type_button = []
        self.map_button = []
        self.screen = pygame.display.set_mode((900, 700))

    def add_buttons(self):
        for i in range(2, 9):
            self.players_button.append(Button((0, 0, 250), 190 + 60 * (i - 1), 320, 50, 50, str(i)))
        for i in range(1, 7):
            self.screen_size_button.append(Button((0, 0, 250), 5 + 150 * (i - 1), 200, 140, 50,
                                                  str(int(300 * (1 + i / 2))) + ":" + str(int(200 * (1 + i / 2)))))
        self.players_button[0].color = (250, 0, 0)
        self.screen_size_button[3].color = (250, 0, 0)
        self.game_type_button.append(Button((250, 0, 0), 120, 430, 300, 50, "free_for_all"))
        self.game_type_button.append(Button((0, 0, 250), 470, 430, 300, 50, "team_death_match"))
        for i in range(4):
            self.map_button.append(Button((0, 0, 250), 150 + i * 145, 530, 140, 100, "", maps[i]))
        self.map_button[0].color = (250, 0, 0)

    def redraw_window(self):
        self.screen.fill((100, 100, 100))
        my_font = pygame.font.SysFont('Comic Sans MS', 40)
        text_surface = my_font.render("Screen size:", False, (0, 0, 0))
        self.screen.blit(text_surface, (330, 130))
        text_surface = my_font.render("Number of players:", False, (0, 0, 0))
        self.screen.blit(text_surface, (280, 250))
        text_surface = my_font.render("Game type:", False, (0, 0, 0))
        self.screen.blit(text_surface, (350, 370))

        self.start_button.draw(self.screen, 60)
        for button_element in self.players_button:
            button_element.draw(self.screen, 40)
        for button_element in self.screen_size_button:
            button_element.draw(self.screen, 40)
        for button_element in self.game_type_button:
            button_element.draw(self.screen, 40)
        for button_element in self.map_button:
            button_element.draw(self.screen, 40)
        pygame.display.update()