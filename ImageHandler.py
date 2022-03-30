import sys
import math
import time
import pygame
import random
import copy
maps = ["static/gravel.png", "static/black.png", "static/houses.png", "static/first_map.png"]
parachute_path = "static/parachute.png"
tank_path = "static/round_tank.png"
bg_path = "static/bg.png"
chest_path = "static/chest.png"
grenade_path = "static/grenade.png"
bouncing_path = "static/bouncing.png"
fastball_path = "static/fastball.png"
gunpoint_path = "static/gunpoint.png"


class ImageHandler:
    def __init__(self, starting_parameters):
        # colours
        self.black = (0, 0, 0)
        self.scale = starting_parameters["screen_parameters"][0] / 2000
        self.width = starting_parameters["screen_parameters"][0]
        self.height = starting_parameters["screen_parameters"][1]
        # images
        self.grenade_image = pygame.transform.scale(pygame.image.load(grenade_path),
                                                    (int(80 * self.scale), int(100 * self.scale)))
        self.bouncing_image = pygame.transform.scale(pygame.image.load(bouncing_path),
                                                     (int(120 * self.scale), int(80 * self.scale)))
        self.fastball_image = pygame.transform.scale(pygame.image.load(fastball_path),
                                                     (int(100 * self.scale), int(100 * self.scale)))
        self.gunpoint_image = pygame.transform.scale(pygame.image.load(gunpoint_path),
                                                     (int(100 * self.scale), int(100 * self.scale)))
        self.screen = pygame.display.set_mode(starting_parameters["screen_parameters"])
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        self.terrain_image = pygame.image.load(starting_parameters["map"]).convert()
        self.terrain_image = pygame.transform.scale(self.terrain_image, (self.width, self.height))

    def update(self, parameters):
        # background display
        self.screen.blit(self.bg, (0, 0))
        end = parameters["end"]
        tanks = parameters["tanks"]
        my_time = parameters["time"]
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', int(100 * self.scale))
        if end == 0:
            text_surface = my_font.render("draw", False, self.black)
            self.screen.blit(text_surface, (int(850 * self.scale), int(550 * self.scale)))
        elif end == 1:
            text_surface = my_font.render("the winner is ", False, self.black)
            self.screen.blit(text_surface, (int(650 * self.scale), int(400 * self.scale)))
            text_surface = my_font.render(tanks[0].name, False, self.black)
            self.screen.blit(text_surface, (int(850 * self.scale), int(500 * self.scale)))
        elif end == 2:
            text_surface = my_font.render("the winner team is ", False, self.black)
            self.screen.blit(text_surface, (int(600 * self.scale), int(400 * self.scale)))
            text_surface = my_font.render(str(tanks[0].team), False, self.black)
            self.screen.blit(text_surface, (int(1000 * self.scale), int(500 * self.scale)))

        else:

            # missile display
            missiles = parameters["missiles"]
            if missiles is not None:
                if type(missiles) == list:
                    for missile in missiles:
                        pygame.draw.circle(self.screen, self.black, (missile.x, missile.y), 5 * self.scale)
                else:
                    pygame.draw.circle(self.screen, self.black, (missiles.x, missiles.y), 5 * self.scale)

            # terrain display
            terrain = parameters["terrain"]
            for x in range(self.width):
                for interval in terrain[x]:
                    self.screen.blit(self.terrain_image, (x, interval[0]),
                                     (x, interval[0], 1, interval[1] - interval[0]))

            # box display
            boxes = parameters["boxes"]
            for box in boxes:
                self.screen.blit(box.parachute, box.parachute_image_rect)
                self.screen.blit(box.box_image, box.box_image_rect)

            # tank display
            barrel = parameters["barrel"]
            active_tank = parameters["active_tank"]
            pull = parameters["pull"]
            # pull and tanks display
            pygame.draw.line(self.screen, (150, 150, 150), (0, self.height - int(100 * self.scale)),
                             (self.width, self.height - int(100 * self.scale)), int(200 * self.scale))

            line1_left_down = (int(self.width - 16 * self.scale), int(self.height - 16 * self.scale))
            line1_right_top = (int(self.width - 18 * self.scale), int(self.height - 142 * self.scale))
            pygame.draw.line(self.screen, (250, 250, 250), line1_left_down, line1_right_top, int(30 * self.scale))
            line2_left_down = (int(self.width - 20 * self.scale), int(self.height - 20 * self.scale))
            line2_right_top = (int(self.width - 20 * self.scale), int(self.height - 140 * self.scale))
            pygame.draw.line(self.screen, self.black, line2_left_down, line2_right_top, int(24 * self.scale))
            line3_left_down = (int(self.width - 20 * self.scale), int(self.height - 20 * self.scale))
            line3_right_top = (
                int(self.width - 20 * self.scale), int(self.height - 20 * self.scale - (pull * 120) * self.scale))
            pygame.draw.line(self.screen, (200, 0, 0), line3_left_down, line3_right_top, int(24 * self.scale))

            my_font = pygame.font.SysFont('Comic Sans MS', int(35 * self.scale))
            for index in range(len(tanks)):
                if index == active_tank:
                    if index < 4:
                        pygame.draw.line(self.screen, (0, 200, 0), (
                            int(16 * self.scale),
                            int(self.height + 30 * self.scale + (index * 50 - 200) * self.scale)), (
                                             int(270 * self.scale),
                                             int(self.height + 30 * self.scale + (index * 50 - 200) * self.scale)),
                                         int(60 * self.scale))
                        pygame.draw.line(self.screen, (250, 250, 250), (
                            int(20 * self.scale),
                            int(self.height + 28 * self.scale + (index * 50 - 200) * self.scale)), (
                                             int(265 * self.scale),
                                             int(self.height + 28 * self.scale + (index * 50 - 200) * self.scale)),
                                         int(50 * self.scale))
                    else:
                        pygame.draw.line(self.screen, (0, 200, 0), (int(276 * self.scale),
                                                                    int(self.height + 30 * self.scale + (
                                                                            (index - 4) * 50 - 200) * self.scale)),
                                         (int(530 * self.scale),
                                          int(self.height + 30 * self.scale + ((index - 4) * 50 - 200) * self.scale)),
                                         int(60 * self.scale))
                        pygame.draw.line(self.screen, (250, 250, 250), (int(280 * self.scale),
                                                                        int(self.height + 28 * self.scale + ((
                                                                                index - 4) * 50 - 200) * self.scale)),
                                         (int(525 * self.scale),
                                          int(self.height + 28 * self.scale + ((index - 4) * 50 - 200) * self.scale)),
                                         int(50 * self.scale))
                text_surface = my_font.render(tanks[index].name + " " + str(tanks[index].hp) + "hp", False,
                                              tanks[index].color)
                if index < 4:
                    self.screen.blit(text_surface,
                                     (int(20 * self.scale), int(self.height + (index * 50 - 200) * self.scale)))
                else:
                    self.screen.blit(text_surface,
                                     (int(280 * self.scale), int(self.height + ((index - 4) * 50 - 200) * self.scale)))
                color = tanks[index].color
                self.screen.blit(tanks[index].parachute, tanks[index].parachute_image_rect)
                self.screen.blit(tanks[index].tank_image_rotated, tanks[index].tank_image_rect)
                line1_left_down = (int(tanks[index].x - 22 * self.scale), int(tanks[index].y - 35 * self.scale))
                line1_right_top = (int(tanks[index].x + 23 * self.scale), int(tanks[index].y - 35 * self.scale))
                pygame.draw.line(self.screen, (250, 250, 250), line1_left_down, line1_right_top, int(12 * self.scale))
                line2_left_down = (int(tanks[index].x - 20 * self.scale), int(tanks[index].y - 34 * self.scale))
                line2_right_top = (int(tanks[index].x + 20 * self.scale), int(tanks[index].y - 34 * self.scale))
                pygame.draw.line(self.screen, self.black, line2_left_down, line2_right_top, int(8 * self.scale))
                line3_left_down = (int(tanks[index].x - 20 * self.scale), int(tanks[index].y - 34 * self.scale))
                line3_right_top = (int(tanks[index].x - 20 * self.scale + 40 * self.scale * (tanks[index].hp / 100)),
                                   int(tanks[index].y - 34 * self.scale))
                pygame.draw.line(self.screen, (200, 0, 0), line3_left_down, line3_right_top, int(8 * self.scale))
                barrel_left_down = (int(tanks[index].x - 10 * self.scale * math.sin(tanks[index].angle * 6.28 / 360)),
                                    int(tanks[index].y - 10 * self.scale * math.cos(tanks[index].angle * 6.28 / 360)))
                if index == active_tank:
                    pygame.draw.line(self.screen, color,
                                     barrel_left_down,
                                     (int(tanks[index].x + barrel[0]), int(tanks[index].y + barrel[1])),
                                     int(6 * self.scale))
                    active_missile = tanks[index].active_missile

                    pygame.draw.rect(self.screen, (0, 250, 0), (
                        int((535 + active_missile * 130) * self.scale), self.height - int(150 * self.scale),
                        int(130 * self.scale), int(150 * self.scale)), 0)

                    pygame.draw.circle(self.screen, self.black,
                                       (int(600 * self.scale), int(self.height - 50 * self.scale)), 30 * self.scale)
                    text_surface = my_font.render(str(tanks[index].missiles[0]), False, self.black)
                    self.screen.blit(text_surface, (int(570 * self.scale), int(self.height - 150 * self.scale)))

                    self.screen.blit(self.grenade_image, (int(685 * self.scale), int(self.height - 100 * self.scale)))
                    text_surface = my_font.render(str(tanks[index].missiles[1]), False, self.black)
                    self.screen.blit(text_surface, (int(720 * self.scale), int(self.height - 150 * self.scale)))

                    self.screen.blit(self.bouncing_image, (int(795 * self.scale), int(self.height - 100 * self.scale)))
                    text_surface = my_font.render(str(tanks[index].missiles[2]), False, self.black)
                    self.screen.blit(text_surface, (int(850 * self.scale), int(self.height - 150 * self.scale)))

                    self.screen.blit(self.fastball_image, (int(935 * self.scale), int(self.height - 100 * self.scale)))
                    text_surface = my_font.render(str(tanks[index].missiles[3]), False, self.black)
                    self.screen.blit(text_surface, (int(1000 * self.scale), int(self.height - 150 * self.scale)))

                    self.screen.blit(self.gunpoint_image, (int(1070 * self.scale), int(self.height - 100 * self.scale)))
                    text_surface = my_font.render(str(tanks[index].missiles[4]), False, self.black)
                    self.screen.blit(text_surface, (int(1105 * self.scale), int(self.height - 150 * self.scale)))

                    my_time = min(15, my_time) / 1.5
                    pygame.draw.line(self.screen, (250, 250, 250),
                                     (int(1398 * self.scale), int(self.height - 35 * self.scale)),
                                     ((1552 * self.scale), int(self.height - 35 * self.scale)), int(42 * self.scale))
                    pygame.draw.line(self.screen, self.black,
                                     (int(1400 * self.scale), int(self.height - 34 * self.scale)),
                                     (int(1550 * self.scale), int(self.height - 34 * self.scale)), int(40 * self.scale))
                    pygame.draw.line(self.screen, (200, 0, 0),
                                     (int(1550 * self.scale), int(self.height - 34 * self.scale)),
                                     (int((1550 - my_time * 15) * self.scale), int(self.height - 34 * self.scale)),
                                     int(40 * self.scale))

                else:
                    pygame.draw.line(self.screen, color,
                                     barrel_left_down,
                                     (tanks[index].tank_image_rect.right,
                                      tanks[index].tank_image_rect.centery - 8 * self.scale), int(6 * self.scale))

        pygame.display.update()
