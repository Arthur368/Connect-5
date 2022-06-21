import pygame as pg
from pygame.locals import *

screen = pg.display.set_mode((800, 600))

class Game_manager:

    def __init__(self) -> None:
        self.screen = pg.display.set_mode((800, 600))
        
    
    def tick(self) -> None:
        pass