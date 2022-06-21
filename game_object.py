import pygame as pg
from pygame.locals import *

class Game_object:

    def __init__(self, x : int, y : int, image_path: str, length: int, width: int) -> None:

        self.x = x
        self.y = y
        self.image_path = image_path
        self.length = length
        self.width = width
        self.image = pg.image.load(image_path)
        self.image = pg.transform.scale(self.image, (self.length, self.width))
        
    def draw(self, screen: pg.surface) -> None:

        screen.blit(self.image, (self.x, self.y))

class Board(Game_object):

    def __init__(self, x: int, y: int, image_path: str, length: int, width: int) -> None:
        super().__init__(x, y, image_path, length, width)
    
        

class Piece(Game_object):

    def __init__(self, x: int, y: int, image_path: str, length: int, width: int) -> None:
        super().__init__(x, y, image_path, length, width)