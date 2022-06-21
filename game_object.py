import pygame as pg
from pygame.locals import *
from game_manager import screen

class Game_object:

    def __init__(self, x : int, y : int, image_path: str) -> None:

        self.x = x
        self.y = y
        self.image_path = image_path
        self.image = pg.image.load(image_path)
        
    def draw(self) -> None:

        screen.blit(self.image, (self.x, self.y))

