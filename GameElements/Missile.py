
class Missile:
    def __init__(self, missile_type, x, y, speed_x, speed_y, damage, r):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.damage = damage
        self.missile_type = missile_type
        self.radius = r

    # move missile
    def move(self, speed_x, speed_y):
        self.x += speed_x
        self.y += speed_y