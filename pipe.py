from constants import *
import random

class Pipe:
    def __init__(self):
        self.x = GAME_SCREEN_WIDTH
        self.y = random.randrange(100, GAME_SCREEN_HEIGHT - 100)
        self.bottom_color = DARK_GREEN
        self.top_color = DARK_GREEN