import pygame as pg
from pygame.locals import *
from game_object import *

screen = pg.display.set_mode((800, 600))

class Game_manager:

    def __init__(self) -> None:
        self.screen = pg.display.set_mode((800, 600))
        self.running = True
        self.current_board = Board(40, 200, "images/board.jpg")
    
    def tick(self) -> None:

        for event in pg.event.get():
    
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        
        self.current_board.draw(self.screen)

        pg.display.update()